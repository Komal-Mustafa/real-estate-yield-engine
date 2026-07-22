"""
FastAPI REST Routes for Real Estate Investment Yield Engine.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import numpy as np
import io
from typing import Optional, List, Dict, Any

from app.models.schemas import (
    PropertyInput,
    PropertyOutput,
    PropertyBatchResponse,
    CsvPropertyUploadResponse
)
from app.analytics.cash_flow_engine import calculate_property_yields_vectorized
from app.analytics.appreciation_simulator import simulate_property_appreciation_monte_carlo
from app.data.sample_properties import SAMPLE_PROPERTIES

router = APIRouter(prefix="/api/v1", tags=["Real Estate Yield API"])


@router.get("/health")
def health():
    return {"status": "healthy", "service": "PropTech Real Estate Yield Engine API", "version": "1.0.0"}


@router.get("/property/sample", response_model=PropertyBatchResponse)
def get_sample_properties_yield():
    """Fetches sample Dubai & Riyadh properties with cash flow optimization details."""
    records = [PropertyInput(**p) for p in SAMPLE_PROPERTIES]
    return _process_property_batch(records)


@router.post("/property/upload-csv", response_model=CsvPropertyUploadResponse)
async def upload_property_csv(file: UploadFile = File(...)):
    """Ingests property listings CSV and computes Cash-on-Cash yields, Cap Rates, and 5-year exit values."""
    if not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Only .csv and text files are supported.")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        try:
            df = pd.read_csv(io.BytesIO(content), sep=None, engine='python')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    cols_lower = {col.lower().strip().replace(" ", "_"): col for col in df.columns}

    id_col = cols_lower.get('property_id', cols_lower.get('id', df.columns[0]))
    name_col = cols_lower.get('property_name', cols_lower.get('name', cols_lower.get('title', df.columns[0])))
    price_col = cols_lower.get('purchase_price', cols_lower.get('price', cols_lower.get('cost', df.columns[0])))
    rent_col = cols_lower.get('gross_monthly_rent', cols_lower.get('rent', df.columns[0]))
    exp_col = cols_lower.get('monthly_expenses', cols_lower.get('expenses', df.columns[0]))
    ltv_col = cols_lower.get('ltv_ratio', cols_lower.get('ltv', df.columns[0]))
    rate_col = cols_lower.get('annual_interest_rate', cols_lower.get('interest_rate', cols_lower.get('rate', df.columns[0])))

    def _safe_float(val, default_val: float) -> float:
        try:
            n = float(pd.to_numeric(val, errors='coerce'))
            return default_val if np.isnan(n) else n
        except Exception:
            return default_val

    lat_col = cols_lower.get('latitude', cols_lower.get('lat'))
    lon_col = cols_lower.get('longitude', cols_lower.get('lon', cols_lower.get('lng')))

    records: List[PropertyInput] = []
    for idx, row in df.iterrows():
        try:
            lat_val = float(row.get(lat_col)) if lat_col and not pd.isna(row.get(lat_col)) else None
            lon_val = float(row.get(lon_col)) if lon_col and not pd.isna(row.get(lon_col)) else None
            records.append(PropertyInput(
                property_id=str(row.get(id_col, f"PROP-{idx+1}")),
                property_name=str(row.get(name_col, f"Property {idx+1}")),
                purchase_price=max(_safe_float(row.get(price_col), 350000.0), 1000.0),
                gross_monthly_rent=max(_safe_float(row.get(rent_col), 2500.0), 0.0),
                monthly_expenses=_safe_float(row.get(exp_col), 500.0),
                ltv_ratio=_safe_float(row.get(ltv_col), 0.70),
                annual_interest_rate=_safe_float(row.get(rate_col), 0.055),
                lat=lat_val,
                lon=lon_val
            ))
        except Exception:
            continue

    if not records:
        raise HTTPException(status_code=400, detail="No valid property rows could be parsed from the CSV.")

    batch_output = _process_property_batch(records)
    return CsvPropertyUploadResponse(
        filename=file.filename,
        total_properties_parsed=len(records),
        analytics=batch_output
    )


def _process_property_batch(records: List[PropertyInput]) -> PropertyBatchResponse:
    prices = np.array([r.purchase_price for r in records])
    rents = np.array([r.gross_monthly_rent for r in records])
    exps = np.array([r.monthly_expenses for r in records])
    ltvs = np.array([r.ltv_ratio for r in records])
    rates = np.array([r.annual_interest_rate for r in records])

    yields = calculate_property_yields_vectorized(prices, rents, exps, ltvs, rates)

    outputs: List[PropertyOutput] = []
    total_equity = 0.0
    total_noi = 0.0

    for i, r in enumerate(records):
        # Run Monte Carlo property appreciation path
        mc = simulate_property_appreciation_monte_carlo(r.purchase_price)
        
        total_equity += float(yields["cash_equity"][i])
        total_noi += float(yields["annual_noi"][i])

        outputs.append(PropertyOutput(
            **r.model_dump(),
            annual_noi=float(yields["annual_noi"][i]),
            cap_rate_percent=float(yields["cap_rates_percent"][i]),
            cash_equity=float(yields["cash_equity"][i]),
            annual_debt_service=float(yields["annual_debt_service"][i]),
            coc_yield_percent=float(yields["coc_yields_percent"][i]),
            dscr=float(yields["dscr"][i]),
            median_5y_value=float(mc["median_appreciation_usd"]),
            mean_appreciation_path=mc["mean_trajectory"]
        ))

    return PropertyBatchResponse(
        total_properties_evaluated=len(records),
        avg_cap_rate_percent=round(float(np.mean(yields["cap_rates_percent"])), 2),
        avg_coc_yield_percent=round(float(np.mean(yields["coc_yields_percent"])), 2),
        total_capital_invested_usd=round(total_equity, 2),
        total_annual_noi_usd=round(total_noi, 2),
        properties=outputs
    )
