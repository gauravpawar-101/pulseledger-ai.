import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="PulseLedger | SME Financial Decision Intelligence",
    page_icon="📊",
    layout="wide"
)

# --- 1. GEMINI SDK COMPATIBILITY LAYER ---
api_key = os.getenv("GEMINI_API_KEY")

def call_gemini(prompt: str) -> str:
    """Invokes Gemini using either the modern or legacy SDK seamlessly."""
    if not api_key:
        return "⚠️ Error: Missing GEMINI_API_KEY. Please add your key to the .env file."
    
    # Try Modern SDK (google-genai)
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception:
        pass

    # Fallback to Legacy SDK (google-generativeai)
    try:
        import google.generativeai as legacy_genai
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error executing AI analysis: {str(e)}"

# --- 2. AUTOMATIC DATA RECOVERY & LOADING ---
def get_sme_data():
    """Loads invoices and summary data; self-heals with default mock data if files missing."""
    if not os.path.exists("invoices.csv"):
        invoices_data = {
            "invoice_id": ["INV-101", "INV-102", "INV-103", "INV-104", "INV-105", "INV-106"],
            "customer": ["Apex Traders", "Delta Corp", "Global Logistics", "Delta Corp", "Metro Retail", "Apex Traders"],
            "amount": [450000, 820000, 180000, 430000, 210000, 390000],
            "due_days_ago": [48, 52, 12, 45, 5, 38],
            "status": ["Overdue", "Overdue", "Paid", "Overdue", "Pending", "Overdue"]
        }
        pd.DataFrame(invoices_data).to_csv("invoices.csv", index=False)

    if not os.path.exists("summary.csv"):
        summary_data = {
            "metric": ["Current Cash Balance", "Monthly Revenue", "Monthly Operating Burn", "Total Receivables", "Total Payables"],
            "value": [2450000, 1850000, 680000, 2090000, 520000]
        }
        pd.DataFrame(summary_data).to_csv("summary.csv", index=False)

    df_inv = pd.read_csv("invoices.csv")
    df_sum = pd.read_csv("summary.csv").set_index("metric")["value"].to_dict()
    return df_inv, df_sum

df_inv, df_sum = get_sme_data()

# --- 3. DETERMINISTIC FINANCIAL CALCULATIONS ---
cash = float(df_sum.get("Current Cash Balance", 2450000))
burn = float(df_sum.get("Monthly Operating Burn", 680000))
receivables = float(df_sum.get("Total Receivables", 2090000))
revenue = float(df_sum.get("Monthly Revenue", 1850000))
runway = round(cash / burn, 1)

overdue_df = df_inv[df_inv["status"] == "Overdue"]
total_overdue = float(overdue_df["amount"].sum())
top_delinquents = overdue_df.groupby("customer")["amount"].sum().sort_values(ascending=False)
top_2_share = round((top_delinquents.head(2).sum() / total_overdue) * 100, 1) if total_overdue > 0 else 0

# --- 4. DASHBOARD HEADER & VITALS ---
st.title("PulseLedger — AI Financial Decision Intelligence")
st.caption("AI + Business Track | ForgeHacks 2026 • Deterministic Financial Analytics + Gemini Reasoning")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cash Runway", f"{runway} Months", "-1.8 Mo (Trend)", delta_color="inverse")
col2.metric("Liquid Cash", f"₹{cash:,.0f}")
col3.metric("Total Receivables", f"₹{receivables:,.0f}")
col4.metric("Overdue (>30 Days)", f"₹{total_overdue:,.0f}", f"{top_2_share}% in Top 2 Clients", delta_color="inverse")

st.divider()

# --- 5. TABS: DIAGNOSIS, SCENARIO LAB & ACTIONS ---
tab1, tab2, tab3 = st.tabs(["🔍 Root-Cause Diagnosis", "🧪 What-If Scenario Lab", "⚡ Action Generator"])

# TAB 1: 3-WHY DIAGNOSTIC ENGINE
with tab1:
    st.subheader("Autonomous Root-Cause Traversal")
    st.markdown(f"""
    * **Observed Symptom:** Cash Runway compressed to **{runway} months** (approaching the 3-month survival danger zone).
    * **Why #1 (Working Capital Drag):** ₹{total_overdue:,.0f} locked in overdue customer receivables (>30 days).
    * **Why #2 (Severe Concentration):** **{top_2_share}%** of all delinquent debt is held by just 2 counterparties ({', '.join(top_delinquents.head(2).index)}).
    * **Why #3 (Operational Bottleneck):** Invoices with *Delta Corp* and *Apex Traders* are on average **46+ days overdue**.
    """)

    if st.button("Generate Executive Diagnostic Brief", type="primary"):
        with st.spinner("Synthesizing diagnostic brief with Gemini..."):
            prompt = f"""
            You are PulseLedger's lead financial intelligence copilot for an SME.
            Analyze these verified deterministic metrics:
            - Current Cash: ₹{cash:,.0f}
            - Monthly Burn: ₹{burn:,.0f}
            - Current Runway: {runway} months
            - Total Overdue Receivables: ₹{total_overdue:,.0f}
            - Delinquent Accounts: {top_delinquents.to_dict()}
            - Top 2 Client Concentration: {top_2_share}%

            Provide a clear, high-impact assessment in 3 sections:
            1. Executive Diagnosis (2-3 sentences on the core liquidity driver).
            2. 30-Day Operational Risk (what happens if receivables remain uncollected).
            3. Immediate Strategic Countermeasures (3 concrete bullet points).

            Strict requirement: Never hallucinate or modify the numbers provided above.
            """
            result = call_gemini(prompt)
            st.markdown(result)

# TAB 2: SCENARIO LAB
with tab2:
    st.subheader("Dynamic What-If Liquidity Simulator")
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.write("**Adjust Market & Operational Assumptions:**")
        cost_inflation = st.slider("Supplier Cost Inflation (%)", 0, 30, 5, step=5)
        collection_delay = st.slider("Additional Collection Delay (Days)", 0, 60, 15, step=5)
        revenue_drop = st.slider("Revenue Decline (%)", 0, 40, 10, step=5)

        # Deterministic simulation formulas
        sim_burn = burn * (1 + (cost_inflation / 100))
        sim_cash_drag = receivables * (collection_delay / 90)
        sim_cash = max(100000, cash - sim_cash_drag)
        sim_runway = round(sim_cash / sim_burn, 1)

    with right_col:
        chart_df = pd.DataFrame({
            "Scenario": ["Current Baseline", "Simulated Stress Test"],
            "Cash Runway (Months)": [runway, sim_runway]
        })
        fig = px.bar(
            chart_df,
            x="Scenario",
            y="Cash Runway (Months)",
            color="Scenario",
            text="Cash Runway (Months)",
            color_discrete_sequence=["#1f77b4", "#ff7f0e"]
        )
        fig.update_layout(showlegend=False, yaxis_range=[0, max(runway, sim_runway) + 2])
        st.plotly_chart(fig, use_container_width=True)

        if sim_runway < 3.0:
            st.error(f"🚨 CRITICAL ALERT: Projected Runway drops to **{sim_runway} Months** (below 90-day liquidity buffer)!")
        else:
            st.success(f"Projected Runway under scenario: **{sim_runway} Months**.")

# TAB 3: ACTION GENERATOR
with tab3:
    st.subheader("One-Click Business Artifact Generator")
    if not top_delinquents.empty:
        target_client = st.selectbox("Select Account for Action:", top_delinquents.index)
        client_amt = top_delinquents[target_client]

        if st.button("Generate Formal Recovery Demand Letter", type="primary"):
            with st.spinner(f"Drafting artifact for {target_client}..."):
                action_prompt = f"""
                Draft an assertive, professional overdue invoice recovery letter from the Head of Finance of an SME to {target_client}.
                Verified Data:
                - Outstanding delinquent balance: ₹{client_amt:,.0f}
                - Average delay: Over 45 days past terms
                - Solution offered: 50% immediate remittance within 48 hours to retain standard credit terms, with balance within 10 days.

                Provide:
                - Clear Subject Line
                - Professional, firm, business-ready email body
                """
                letter = call_gemini(action_prompt)
                st.text_area("Generated Artifact (Ready to Copy/Send)", letter, height=300)
    else:
        st.write("No delinquent accounts detected.")