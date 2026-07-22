"""
Vectorized Real Estate Cash Flow, Cap Rate & IRR Engine using NumPy.
"""

import numpy as np
from typing import Dict, Any, List

def calculate_property_yields_vectorized(
    purchase_prices: np.ndarray,
    gross_monthly_rents: np.ndarray,
    monthly_expenses: np.ndarray,
    ltv_ratios: np.ndarray,
    annual_interest_rates: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Computes Net Operating Income (NOI), Capitalization Rate (Cap Rate),
    Mortgage Payments, Cash Invested, Cash-on-Cash (CoC) Yield, and DSCR.
    """
    prices = np.asarray(purchase_prices, dtype=np.float64)
    rents = np.asarray(gross_monthly_rents, dtype=np.float64)
    exp = np.asarray(monthly_expenses, dtype=np.float64)
    ltv = np.asarray(ltv_ratios, dtype=np.float64)
    rate = np.asarray(annual_interest_rates, dtype=np.float64)

    # 1. Net Operating Income (NOI) & Cap Rate
    annual_noi = (rents - exp) * 12.0
    cap_rates = annual_noi / prices

    # 2. Mortgage Leverage calculations
    loan_amounts = prices * ltv
    cash_equity = prices - loan_amounts

    # Monthly mortgage payments (Amortizing loan: 30-year term)
    r_monthly = rate / 12.0
    n_payments = 360.0
    
    # Avoid division by zero for cash purchases (LTV = 0)
    monthly_debt_service = np.zeros_like(prices)
    has_loan = loan_amounts > 0.0
    
    # Standard Amortization formula: P * (r*(1+r)^n)/((1+r)^n - 1)
    factor = np.where(has_loan & (rate > 0.0), (r_monthly * (1.0 + r_monthly)**n_payments) / ((1.0 + r_monthly)**n_payments - 1.0), 0.0)
    monthly_debt_service = loan_amounts * factor
    annual_debt_service = monthly_debt_service * 12.0

    # 3. Cash-on-Cash (CoC) Yield
    cash_flow_after_debt = annual_noi - annual_debt_service
    coc_yields = np.where(cash_equity > 0.0, cash_flow_after_debt / cash_equity, annual_noi / prices)

    # 4. Debt Service Coverage Ratio (DSCR)
    dscr = np.where(annual_debt_service > 0.0, annual_noi / annual_debt_service, 2.5)

    return {
        "annual_noi": np.round(annual_noi, 2),
        "cap_rates_percent": np.round(cap_rates * 100.0, 2),
        "cash_equity": np.round(cash_equity, 2),
        "annual_debt_service": np.round(annual_debt_service, 2),
        "coc_yields_percent": np.round(coc_yields * 100.0, 2),
        "dscr": np.round(dscr, 2)
    }
