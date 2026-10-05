# PulseLedger AI — SME Financial Decision Intelligence

> **ForgeHacks 2026** | Track: **AI + Business**  
> An autonomous financial decision engine that monitors liquidity vitals, conducts 3-Why root-cause diagnosis, stress-tests runway through dynamic simulation, and synthesizes executive recovery artifacts.

---

## 📌 Executive Summary
Small and medium-sized enterprises (SMEs) frequently fail not due to lack of market demand, but due to liquidity blindspots and trapped working capital. Standard bookkeeping dashboards show historical aggregates ("what happened"), but lack the causal reasoning to explain **why it happened**, **what happens under stress**, or **what explicit operational countermeasure to take**.

PulseLedger solves this by coupling **deterministic financial analytics **—eliminating numerical hallucinations—with , diagnostic reasoning** to deliver end-to-end financial intelligence.

---

## ⚡ Core Capabilities
1. **Deterministic Financial Vitals:** Automatically evaluates core liquidity metrics (Cash Runway, Days Sales Outstanding, Overdue Aging, and Working Capital).
2. **3-Why Causal Diagnosis Engine:** Hierarchically isolates the operational root causes behind cash compression (Working capital lock $\rightarrow$ Top counterparty delinquency concentration $\rightarrow$ Aging thresholds).
3. **Dynamic What-If Liquidity Lab:** Interactive stress testing across operational variables (supplier inflation, collection drift, and demand contractions) with real-time Plotly runway projections.
4. **Autonomous Action Artifact Generator:** Generates legally sound, assertive overdue recovery notices and executive board memos with one click.

---

## 🛠️ System Architecture & Stack
- **Interface:** Streamlit, Plotly Express
- **Computation Engine:** Python 3.11+, Pandas
- **Reasoning & Synthesis:** Google Gemini Flash API (`google-genai` / `google-generativeai`)
- **Data Ingestion:** Interactive CSV upload engine with auto-healing baseline synthesis

---

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/gauravpawar-101/pulseledger-ai..git](https://github.com/gauravpawar-101/pulseledger-ai..git)
   cd pulseledger-ai
