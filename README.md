# Nassau Candy Distributor – Shipping Route Efficiency Analysis

## 📌 Project Overview

This project delivers a shipping-focused analytical framework for Nassau Candy Distributor. Instead of relying on sales volume alone, the analysis identifies which factory-to-customer routes are truly efficient, which routes experience frequent delays, and where geographic bottlenecks and ship mode dependencies require operational intervention.

The solution combines Python-based analytics with an interactive Streamlit dashboard designed for logistics managers and stakeholder decision-making.

---

## 🎯 Business Objectives

- Identify the most and least efficient factory-to-customer shipping routes
- Detect ship modes responsible for delays and operational risk
- Compare factory-level and region-level shipping performance
- Map geographic bottlenecks using volume vs lead time analysis
- Support data-driven decisions on route optimization, carrier selection, and ship mode strategy

---

## 🗂 Dataset Description

The dataset contains 10,194 transaction-level records with the following key attributes:

- Sales, Cost, Gross Profit, Units
- Product hierarchy (Product Name, Division)
- Shipping details (Ship Mode, Order Date, Ship Date)
- Geography (Region, State/Province, City)
- Engineered fields: Factory, Route Region, Lead Time, Is Delayed

Each row represents a product-level order line, enabling granular shipping route efficiency analysis.

---

## 📊 Key Metrics

- **Lead Time (days)** = (Ship Date − Order Date) mod 365
- **Delay Threshold** = Mean Lead Time + 1 Standard Deviation (180.1 days)
- **Is Delayed** = Lead Time > Delay Threshold
- **Efficiency Score** = 0–100 normalized score per route (100 = fastest)
- **Delay Rate (%)** = Delayed Orders ÷ Total Orders

---

## 🔑 Key Findings

- 📦 **10,194 orders** analysed across **20 factory-region routes**
- ⏱️ Average lead time: **178.3 days** | Range: 174–185 days
- ⚠️ Overall delay rate: **10.25%** (1,045 delayed orders)
- 🔴 **100% of delays** belong exclusively to **Standard Class** shipping (17.0% delay rate)
- ✅ Same Day, First Class, Second Class all record **0.0% delay rate**
- 🏆 **Fastest route:** The Other Factory → Gulf (177.63 days, Efficiency Score: 100)
- ❌ **Slowest route:** Sugar Shack → Atlantic (179.00 days, Efficiency Score: 0)

---

## 🖥 Streamlit Dashboard Features

### Dashboard Pages

- **Route Efficiency Overview** — Top 10 & Bottom 10 routes, Efficiency Scores (0–100), full route leaderboard
- **Geographic Analysis** — Factory × Region heatmap, region bar chart, state-level bottleneck scatter plot
- **Ship Mode Comparison** — Lead time, delay rate & cost charts, lead time boxplot, monthly trend
- **Route Drill-Down** — Product & factory charts, 300-row order table, CSV download

### Sidebar Controls

- Order Date Range selector
- Region & State filter
- Factory filter
- Ship Mode filter
- Max Lead Time slider

---

## 📁 Repository Structure
```
nassau-candy-shipping-analysis/
│
├── app.py
├── Nassau Candy Distributor.csv
├── unified logo.png
├── requirements.txt
├── README.md
│
├── notebooks/
│   └── Nassau_Candy_Distributor.ipynb
│
└── reports/
    ├── Nassau_Candy_Research_Paper.docx
    └── Nassau_Candy_Executive_Summary.docx
```

---

## ⚙️ How to Run the App
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧠 Business Value

This project shifts logistics decision-making from reactive issue resolution to proactive route optimization, enabling Nassau Candy Distributor to:

- Eliminate delays by reducing Standard Class dependency
- Replicate The Other Factory's best-in-class shipping practices
- Resolve geographic bottlenecks in high-volume states
- Monitor monthly delay rates with a clear escalation protocol

---

## 📌 Author

**Data Analyst Internship Project – Shipping Route Efficiency & Logistics Optimization**  
Lakshmi Mahitha Noudu | Unified Mentor | Mentored by Sai Prasad Kagne | March 2026
