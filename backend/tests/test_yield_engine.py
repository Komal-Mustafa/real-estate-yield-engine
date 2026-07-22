"""
Unit tests for Real Estate Cash Flow Engine, Monte Carlo Simulator, and REST API.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.analytics.cash_flow_engine import calculate_property_yields_vectorized
from app.analytics.appreciation_simulator import simulate_property_appreciation_monte_carlo
from app.main import app

client = TestClient(app)

def test_property_cash_flow_yields():
    prices = np.array([500000.0, 1000000.0])
    rents = np.array([3500.0, 7000.0])
    exps = np.array([800.0, 1500.0])
    ltvs = np.array([0.70, 0.0])  # Leveraged vs Cash Purchase
    rates = np.array([0.06, 0.0])

    res = calculate_property_yields_vectorized(prices, rents, exps, ltvs, rates)
    assert res["annual_noi"][0] == 32400.0
    assert res["cap_rates_percent"][0] == 6.48
    assert res["cash_equity"][0] == 150000.0
    # Cash purchase LTV=0 should have 0 debt service and 100% equity matching price
    assert res["annual_debt_service"][1] == 0.0
    assert res["cash_equity"][1] == 1000000.0

def test_appreciation_monte_carlo():
    mc = simulate_property_appreciation_monte_carlo(500000.0, drift=0.05, volatility=0.07, horizon_years=5)
    assert len(mc["mean_trajectory"]) == 6
    assert mc["median_appreciation_usd"] > 500000.0
    assert mc["median_appreciation_usd"] > mc["downside_appreciation_usd"]
    assert mc["upside_appreciation_usd"] > mc["median_appreciation_usd"]

def test_api_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_sample_properties():
    response = client.get("/api/v1/property/sample")
    assert response.status_code == 200
    data = response.json()
    assert data["total_properties_evaluated"] == 5
    assert len(data["properties"]) == 5
