"""
Geometric Brownian Motion (GBM) Monte Carlo Property Appreciation Simulator.
"""

import numpy as np
from typing import Dict, Any

def simulate_property_appreciation_monte_carlo(
    initial_value: float,
    drift: float = 0.04,  # Expected annual growth rate (4%)
    volatility: float = 0.08,  # Price volatility (8%)
    horizon_years: int = 5,
    num_simulations: int = 10000
) -> Dict[str, Any]:
    """
    Simulates 10,000 future property valuation trajectories over a 5-year exit horizon.
    """
    dt = 1.0
    steps = horizon_years
    
    # Deterministic seed for verification
    np.random.seed(42)
    
    # Generate GBM path updates
    # S_t = S_{t-1} * exp((drift - vol^2 / 2) * dt + vol * sqrt(dt) * Z)
    shock = np.random.normal(0, 1, (num_simulations, steps))
    increments = np.exp((drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * shock)
    
    # Cumulative product of price paths
    price_paths = initial_value * np.cumprod(increments, axis=1)
    final_values = price_paths[:, -1]

    # Calculate probability distributions
    p10 = float(np.percentile(final_values, 10))
    p50 = float(np.percentile(final_values, 50))  # Median case
    p90 = float(np.percentile(final_values, 90))

    # Mean trajectory path for line charting
    mean_trajectory = [initial_value] + list(np.mean(price_paths, axis=0))
    mean_trajectory = [round(float(v), 2) for v in mean_trajectory]

    return {
        "median_appreciation_usd": round(p50, 2),
        "downside_appreciation_usd": round(p10, 2),
        "upside_appreciation_usd": round(p90, 2),
        "mean_trajectory": mean_trajectory
    }
