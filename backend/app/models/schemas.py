"""
Pydantic v2 validation schemas for PropTech Real Estate Yield Engine.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PropertyInput(BaseModel):
    property_id: str
    property_name: str
    purchase_price: float = Field(default=500000.0, ge=1000.0)
    gross_monthly_rent: float = Field(default=3500.0, ge=0.0)
    monthly_expenses: float = Field(default=800.0, ge=0.0)
    ltv_ratio: float = Field(default=0.75, ge=0.0, le=1.0)
    annual_interest_rate: float = Field(default=0.055, ge=0.0, le=0.30)
    lat: Optional[float] = None
    lon: Optional[float] = None

class PropertyOutput(PropertyInput):
    annual_noi: float
    cap_rate_percent: float
    cash_equity: float
    annual_debt_service: float
    coc_yield_percent: float
    dscr: float
    median_5y_value: float
    mean_appreciation_path: List[float]

class PropertyBatchResponse(BaseModel):
    total_properties_evaluated: int
    avg_cap_rate_percent: float
    avg_coc_yield_percent: float
    total_capital_invested_usd: float
    total_annual_noi_usd: float
    properties: List[PropertyOutput]

class CsvPropertyUploadResponse(BaseModel):
    filename: str
    total_properties_parsed: int
    analytics: PropertyBatchResponse
