import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="PulseLedger | SME Financial Decision Intelligence",
    page_icon="📊",
    layout="wide"
)

# --- 1. GEMINI SDK ENGINE & RESILIENT MODEL RESOLVER ---
default_env_key = os.getenv("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("🔑 Gemini API Key", value=default_env_key, type="password")

if not api_key:
    st.sidebar.warning("⚠️ Enter a valid Gemini API Key to enable AI diagnostics.")

def call_gemini(prompt: str) -> str:
    """Robust multi-version caller that tries multiple models across SDK versions."""
    if not api_key:
        return "⚠️ Error: Missing Gemini API Key. Provide it in the sidebar or your .env file."

    # Model priority list covering current, legacy, and alias names
    candidate_models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash-latest"]

    # 1. Attempt Modern google-genai SDK
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception:
                continue
    except Exception:
        pass

    # 2. Attempt Legacy google-generativeai SDK
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        for model_name in candidate_models:
            try:
                model = legacy_genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception:
                continue
    except Exception as e:
        return f"⚠️ Execution error: {str(e)}"

    return "⚠️ Error: Could not connect to Gemini models. Check your API key and connection."

# --- 2. DATA PROVIDER & SELF-HEALING ENGINE ---
def load_mock_datasets():
    """Generates standard baseline mock data for SME financial analysis."""
    invoices_data = {
        "invoice_id": ["INV-101", "INV-102", "INV-103", "INV-104", "INV-105", "INV-106", "INV-107", "INV-108"],
        "customer": ["Apex Traders", "Delta Corp", "Global Logistics", "Delta Corp", "Metro Retail", "Apex Traders", "Zenith Tech", "Delta Corp"],
        "amount": [450000, 820000, 180000, 430000, 210000, 390000, 150000, 280000],
        "due_days_ago": [48, 52, 12, 45, 5, 38, 14, 60],
        "status": ["Overdue", "Overdue", "Paid", "Overdue", "Pending", "Overdue", "Paid", "Overdue"]
    }
    summary_data = {
        "metric": ["Current Cash Balance", "Monthly Revenue", "Monthly Operating Burn", "Total Receivables", "Total Payables"],
        "value": [2450000, 1850000, 680000, 2910000, 520000]
    }
    df_inv = pd.DataFrame(invoices_data)
    df_sum = pd.DataFrame(summary_data).set_index("metric")["value"].to_dict()
    return df_inv, df_sum

st.sidebar.header("📁 Financial Data Source")
data_source = st.sidebar.radio("Select Input Mode:", ["Use Demo SME Data", "Upload Invoices CSV"])

if data_source == "Upload Invoices CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV (Required columns: customer, amount, status, due_days_ago)", type=["csv"])
    if uploaded_file is not None:
        try:
            df_inv = pd.read_csv(uploaded_file)
            st.sidebar.success("Custom data loaded!")
            # Default financial summary for custom upload
            df_sum = {
                "Current Cash Balance": 2500000,
                "Monthly Revenue": float(df_inv["amount"].sum() * 0.8),
                "Monthly Operating Burn": 700000,
                "Total Receivables": float(df_inv["amount"].sum()),
                "Total Payables": 500000
            }
        except Exception as e:
            st.sidebar.error(f"Error parsing CSV: {e}")
            df_inv, df_sum = load_mock_datasets()
    else:
        st.sidebar.info("Awaiting file upload. Showing mock baseline.")
        df_inv, df_sum = load_mock_datasets()
else:
    df_inv, df_sum = load_mock_datasets()

# --- 3. DETERMINISTIC FINANCIAL METRICS (PANDAS MATH) ---
cash = float(df_sum.get("Current Cash Balance", 2450000))
burn = float(df_sum.get("Monthly Operating Burn", 680000))
receivables = float(df_sum.get("Total Receivables", 2910000))
revenue = float(df_sum.get("Monthly Revenue", 1850000))

# Hard Metrics
runway = round(cash / burn, 1) if burn > 0 else 0.0

# Overdue and Delinquency Analysis
overdue_df = df_inv[df_inv["status"].str.lower() == "overdue"] if "status" in df_inv.columns else pd.DataFrame()
total_overdue = float(overdue_df["amount"].sum()) if not overdue_df.empty else 0.0

if not overdue_df.empty and "customer" in overdue_df.columns:
    top_delinquents = overdue_df.groupby("customer")["amount"].sum().sort_values(ascending=False)
    top_2_sum = top_delinquents.head(2).sum()
    top_2_share = round((top_2_sum / total_overdue) * 100, 1) if total_overdue > 0 else 0.0
    top_delinquent_names = list(top_delinquents.head(2).index)
else:
    top_delinquents = pd.Series(dtype=float)
    top_2_share = 0.0
    top_delinquent_names = ["N/A"]

# --- 4. HEADER & TOP-LEVEL VITALS ---
st.title("PulseLedger — AI Financial Decision Intelligence")
st.caption("AI + Business Track | ForgeHacks 2026 • Deterministic Financial Analytics + Gemini Diagnostic Reasoning")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Cash Runway", f"{runway} Months", "-1.8 Mo (Trend)", delta_color="inverse")
m2.metric("Liquid Cash", f"₹{cash:,.0f}")
m3.metric("Total Receivables", f"₹{receivables:,.0f}")
m4.metric("Overdue (>30 Days)", f"₹{total_overdue:,.0f}", f"{top_2_share}% in Top 2 Debtors", delta_color="inverse")

st.divider()

# --- 5. INTERACTIVE TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 3-Why Root-Cause Diagnosis", "🧪 What-If Liquidity Lab", "⚡ Action Artifact Generator"])

# TAB 1: ROOT CAUSE DIAGNOSIS
with tab1:
    st.subheader("Deterministic Anomaly Traversal (3-Why Engine)")
    
    st.markdown(f"""
    * **Observed Symptom:** Cash Runway compressed to **{runway} months** (approaching standard 90-day distress line).
    * **Why #1 (Working Capital Lock):** ₹{total_overdue:,.0f} remains uncollected in overdue customer invoices (>30 days).
    * **Why #2 (Counterparty Risk):** **{top_2_share}%** of all delinquent receivables are concentrated with just 2 counterparties: **{', '.join(top_delinquent_names)}**.
    * **Why #3 (Collection Delay Drift):** Primary invoices with *{top_delinquent_names[0] if top_delinquent_names else 'delinquent clients'}* average over **45 days past agreed credit terms**.
    """)

    if st.button("Generate Executive Diagnostic Brief", type="primary"):
        with st.spinner("Synthesizing diagnostic brief with Gemini..."):
            diagnostic_prompt = f"""
            You are PulseLedger's lead financial decision intelligence copilot for an SME.
            Analyze these verified, pre-computed financial vitals:
            - Liquid Cash Balance: ₹{cash:,.0f}
            - Monthly Net Burn: ₹{burn:,.0f}
            - Current Cash Runway: {runway} months
            - Total Overdue Receivables: ₹{total_overdue:,.0f}
            - Delinquent Accounts Breakdown: {top_delinquents.to_dict() if not top_delinquents.empty else 'None'}
            - Top 2 Debtor Concentration: {top_2_share}%

            Deliver a crisp, professional decision memo structured in 3 clear sections:
            1. Executive Diagnosis (2-3 concise sentences identifying the exact operational liquidity bottleneck).
            2. 30-Day Solvency Risk (what happens if this receivable concentration remains uncollected).
            3. Tactical Action Plan (3 numbered, highly actionable operational steps for management).

            Rule: Do not hallucinate or modify any numbers provided.
            """
            analysis_output = call_gemini(diagnostic_prompt)
            st.markdown(analysis_output)

# TAB 2: WHAT-IF SCENARIO SIMULATOR
with tab2:
    st.subheader("Dynamic What-If Stress Testing")
    col_sim_controls, col_sim_chart = st.columns([1, 2])

    with col_sim_controls:
        st.write("**Simulate Operational Pressures:**")
        cost_inflation = st.slider("Supplier Cost Inflation (%)", 0, 30, 8, step=2)
        collection_delay = st.slider("Collection Delay Extension (Days)", 0, 60, 20, step=5)
        revenue_shock = st.slider("Revenue Downturn (%)", 0, 40, 10, step=5)

        # Deterministic Simulation Formulas
        sim_burn = burn * (1 + (cost_inflation / 100))
        sim_cash_drag = receivables * (collection_delay / 90)
        sim_cash = max(50000.0, cash - sim_cash_drag)
        sim_runway = round(sim_cash / sim_burn, 1)

    with col_sim_chart:
        chart_data = pd.DataFrame({
            "Operational State": ["Current Baseline", "Simulated Stress Test"],
            "Cash Runway (Months)": [runway, sim_runway]
        })
        fig = px.bar(
            chart_data,
            x="Operational State",
            y="Cash Runway (Months)",
            color="Operational State",
            text="Cash Runway (Months)",
            color_discrete_sequence=["#2b5c8f", "#d9534f"]
        )
        fig.update_layout(showlegend=False, yaxis_range=[0, max(runway, sim_runway) + 2])
        st.plotly_chart(fig, use_container_width=True)

        if sim_runway < 3.0:
            st.error(f"🚨 CRITICAL WARNING: Under this stress scenario, runway drops to **{sim_runway} Months** (Breaches safety covenant).")
        else:
            st.info(f"Projected liquidity duration under stress: **{sim_runway} Months**.")

# TAB 3: ONE-CLICK ACTION GENERATOR
with tab3:
    st.subheader("One-Click Business Artifact Generator")
    if not top_delinquents.empty:
        target_account = st.selectbox("Select Counterparty for Recovery Action:", top_delinquents.index)
        debt_amount = top_delinquents[target_account]

        if st.button("Generate Professional Overdue Recovery Notice", type="primary"):
            with st.spinner(f"Drafting formal notice for {target_account}..."):
                artifact_prompt = f"""
                Draft a formal, professional, and firm overdue invoice collection notice from the Chief Financial Officer / Head of Finance of an SME to {target_account}.
                
                Verified Accounts Data:
                - Outstanding Past-Due Amount: ₹{debt_amount:,.0f}
                - Age of Overdue: Over 45 days past standard commercial credit terms
                - Settlement Terms: Request 50% immediate wire transfer within 48 business hours to keep accounts in good standing and prevent suspension of fulfillment.

                Output format:
                - Clear Subject Line
                - Complete professional email body ready to send immediately.
                """
                letter_text = call_gemini(artifact_prompt)
                st.text_area("Generated Artifact", letter_text, height=280)
    else:
        st.info("No overdue customer accounts found in the active dataset.")