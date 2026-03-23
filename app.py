import streamlit as st
import pandas as pd

st.set_page_config(page_title="Same-Day Fraud Detection", layout="wide")

# 🎨 GLOW UI
st.markdown("""
<style>
html, body, [class*="css"] {
    background: radial-gradient(circle at 20% 0%, rgba(139,92,246,.15), transparent),
                radial-gradient(circle at 80% 20%, rgba(110,231,255,.15), transparent),
                #070a12;
    color: #eaf0ff;
    font-family: 'Segoe UI', sans-serif;
}

.title {
    font-size: 40px;
    font-weight: bold;
    background: linear-gradient(135deg,#6ee7ff,#8b5cf6);
    -webkit-background-clip: text;
    color: transparent;
}

.card {
    padding: 20px;
    border-radius: 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
}

.kpi {
    padding: 18px;
    border-radius: 16px;
    background: rgba(255,255,255,0.05);
    text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}
.kpi h1 {
    margin: 0;
    font-size: 28px;
    background: linear-gradient(135deg,#6ee7ff,#8b5cf6);
    -webkit-background-clip: text;
    color: transparent;
}
.kpi p {
    margin: 5px 0 0;
    color: #a9b6dd;
}

.stButton>button {
    border-radius: 50px;
    background: linear-gradient(135deg,#6ee7ff,#8b5cf6);
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 🌟 TITLE
st.markdown('<p class="title">⚡ Same-Day Admission & Discharge Fraud</p>', unsafe_allow_html=True)

# 📂 Upload
uploaded_file = st.file_uploader("📂 Upload Patient Dataset", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df['Admission_Time'] = pd.to_datetime(df['Admission_Time'])
    df['Discharge_Time'] = pd.to_datetime(df['Discharge_Time'])

    # Layout
    col1, col2 = st.columns([2,1])

    # 📊 Dataset
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Dataset Preview")
        st.dataframe(df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 📈 Insights
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 Data Insights")

        same_day_count = (df['Admission_Time'].dt.date == df['Discharge_Time'].dt.date).sum()

        k1, k2 = st.columns(2)

        with k1:
            st.markdown(f"""
            <div class="kpi">
                <h1>📄 {len(df)}</h1>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)

        with k2:
            st.markdown(f"""
            <div class="kpi">
                <h1>⚡ {same_day_count}</h1>
                <p>Same-Day Cases</p>
            </div>
            """, unsafe_allow_html=True)

        k3, k4 = st.columns(2)

        with k3:
            st.markdown(f"""
            <div class="kpi">
                <h1>🧑 {df['Patient_ID'].nunique()}</h1>
                <p>Patients</p>
            </div>
            """, unsafe_allow_html=True)

        with k4:
            avg_stay = (df['Discharge_Time'] - df['Admission_Time']).dt.days.mean()
            st.markdown(f"""
            <div class="kpi">
                <h1>⏱️ {avg_stay:.1f}</h1>
                <p>Avg Stay (Days)</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 🔍 Detection Function
    def detect_same_day(df):
        result = df[
            df['Admission_Time'].dt.date == df['Discharge_Time'].dt.date
        ].copy()

        result["Fraud_Flag"] = "⚠️ Same-Day Discharge"

        return result

    # 🚀 Button
    if st.button("⚡ Detect Same-Day Fraud"):
        result_df = detect_same_day(df)

        if result_df.empty:
            st.success("✅ No same-day fraud detected")
        else:
            st.error("⚠️ Same-day fraud cases detected!")

            col3, col4 = st.columns(2)

            with col3:
                st.markdown("### ⚡ Flagged Cases")
                st.dataframe(result_df, use_container_width=True)

                # Download
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Results", csv, "same_day_fraud.csv")

            with col4:
                st.markdown("### 📊 Insights")
                st.metric("Total Cases", len(result_df))
                st.metric("Unique Patients", result_df['Patient_ID'].nunique())

            # Summary
            st.markdown("### 🔎 Summary")
            summary = result_df.groupby("Patient_ID").size().reset_index(name="Case_Count")
            st.dataframe(summary, use_container_width=True)