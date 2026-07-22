# PropPulse — Real-Time Real Estate Investment Yield & Cash Flow Optimization Engine 🏢

An enterprise-grade **Real Estate Yield & Leverage Optimizer** featuring a **60 FPS rotating 3D architectural city wireframe background**, vectorized **NumPy** cash flow calculators, and a Geometric Brownian Motion **Monte Carlo** property appreciation simulator.

---

## 🌟 Key Features

- **3D City Wireframe Animation**: A premium 60 FPS HTML5 Canvas background rendering rotating skyscrapers that adjust based on property valuation models.
- **Leverage Stress-Testing**: Interactive sliders for LTV (Loan-to-Value), mortgage interest rate, and target appreciation.
- **DSCR Threshold Monitoring**: Flags properties falling below the bank lending limit ($\text{DSCR} < 1.25$).
- **Monte Carlo Price Forecaster**: 10,000 simulations projecting 5-year exit prices.

---

## 🚀 Quick Start Guide

### 1. Launch Live Web App (Zero Setup)
```bash
cd real-estate-yield-engine
python -m http.server 8007
```
Open **`http://localhost:8007`** in your browser!

### 2. Launch FastAPI REST Server
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8007
```

### 3. Run Pytest Test Suite
```bash
cmd /c "set PYTHONPATH=backend && python -m pytest backend/tests"
```

---

## 📖 Educational Documentation

For mathematical derivations, cash flow matrices, and investor talking points, read **[PROJECT_EXPLAINER.md](file:///C:/Users/Shahab%20Ahmad/.gemini/antigravity/scratch/real-estate-yield-engine/PROJECT_EXPLAINER.md)**.
