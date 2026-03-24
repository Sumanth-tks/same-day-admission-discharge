import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io
import base64
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Same-Day Admission Fraud Detection", layout="wide", page_icon="🛡️")

# Custom CSS - Matching the HTML Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg: #070a12;
        --panel: #0d1220;
        --text: #eaf0ff;
        --muted: #a9b6dd;
        --border: rgba(255,255,255,.08);
        --accent: #6ee7ff;
        --accent2: #8b5cf6;
        --radius: 18px;
        --glow: 0 0 40px rgba(110,231,255,.15);
    }

    * {
        font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif;
    }

    html, body, .stApp {
        background: radial-gradient(1200px 900px at 18% 0%, rgba(139,92,246,.18), transparent 60%),
                    radial-gradient(900px 700px at 85% 20%, rgba(110,231,255,.15), transparent 60%),
                    var(--bg) !important;
        color: var(--text);
    }

    /* Header Styles */
    .header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px 0;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255,255,255,.06);
    }

    .logo-container {
        width: 56px;
        height: 56px;
        border-radius: 18px;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, rgba(110,231,255,.14), rgba(139,92,246,.16));
        border: 1px solid rgba(255,255,255,.10);
        box-shadow: var(--glow);
    }

    .logo-container i {
        font-size: 1.5rem;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .header-text h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .header-text p {
        margin: 4px 0 0;
        color: var(--muted);
        font-size: 0.9rem;
    }

    /* Card Styles */
    .card {
        border-radius: var(--radius);
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.08);
        box-shadow: 0 18px 55px rgba(0,0,0,.45);
        padding: 24px;
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: "";
        position: absolute;
        inset: -80px;
        background: radial-gradient(circle at 15% 15%, rgba(110,231,255,.12), transparent 60%),
                    radial-gradient(circle at 85% 70%, rgba(139,92,246,.12), transparent 60%);
        filter: blur(22px);
        opacity: .6;
        z-index: 0;
        pointer-events: none;
    }

    .card > * {
        position: relative;
        z-index: 1;
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .card-title i {
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    /* KPI Styles */
    .kpi-card {
        border-radius: 16px;
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.08);
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease, border 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(110,231,255,.25);
    }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        line-height: 1;
        margin-bottom: 8px;
    }

    .kpi-label {
        color: var(--muted);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Button Styles */
    .stButton > button {
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.25s ease !important;
        border: 1px solid rgba(255,255,255,.1) !important;
        background: linear-gradient(135deg, rgba(110,231,255,.12), rgba(139,92,246,.12)) !important;
        color: var(--text) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        border-color: rgba(110,231,255,.4) !important;
        box-shadow: 0 8px 30px rgba(110,231,255,.2) !important;
        background: linear-gradient(135deg, rgba(110,231,255,.2), rgba(139,92,246,.2)) !important;
    }

    .stButton > button[data-baseweb="tab"] {
        border-radius: 12px 12px 0 0 !important;
    }

    /* Analysis Button Grid */
    .analysis-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }

    /* Download Button */
    .download-btn {
        background: linear-gradient(135deg, rgba(110,231,255,.2), rgba(139,92,246,.2)) !important;
        border: 1px solid rgba(110,231,255,.3) !important;
        color: var(--accent) !important;
    }

    /* Alert Styles */
    .success-alert {
        border-radius: 14px;
        padding: 16px 20px;
        background: rgba(34, 197, 94,.1);
        border: 1px solid rgba(34, 197, 94,.2);
        color: #4ade80;
    }

    .warning-alert {
        border-radius: 14px;
        padding: 16px 20px;
        background: rgba(251, 191, 36,.1);
        border: 1px solid rgba(251, 191, 36,.2);
        color: #fbbf24;
    }

    .danger-alert {
        border-radius: 14px;
        padding: 16px 20px;
        background: rgba(239, 68, 68,.1);
        border: 1px solid rgba(239, 68, 68,.2);
        color: #f87171;
    }

    /* DataFrame Styling */
    .dataframe {
        border: none !important;
    }

    .dataframe thead th {
        background: rgba(110,231,255,.1) !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
        border: none !important;
    }

    .dataframe tbody tr:hover {
        background: rgba(110,231,255,.05) !important;
    }

    /* Section Divider */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.1), transparent);
        margin: 32px 0;
    }

    /* Word Cloud Container */
    .wordcloud-container {
        background: rgba(0,0,0,.3);
        border-radius: 16px;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 350px;
    }

    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,.02);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(110,231,255,.2);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(110,231,255,.3);
    }

    /* Plot Container */
    .plot-container {
        background: rgba(255,255,255,.02);
        border-radius: 14px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,.06);
    }

    /* Stat Box */
    .stat-box {
        background: linear-gradient(135deg, rgba(110,231,255,.08), rgba(139,92,246,.08));
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,.08);
    }

    .stat-box h4 {
        margin: 0 0 8px;
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stat-box .value {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,.02);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.06);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(110,231,255,.15), rgba(139,92,246,.15)) !important;
    }
</style>
""", unsafe_allow_html=True)

# Font Awesome Icons
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)

# ============ HEADER ============
st.markdown("""
<div class="header">
    <div class="logo-container">
        <i class="fa-solid fa-shield-halved"></i>
    </div>
    <div class="header-text">
        <h1>⚡ Same-Day Admission & Discharge Fraud</h1>
        <p>Detect suspicious same-day discharge patterns in patient records</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============ UPLOAD SECTION ============
st.markdown("""
<div class="card" style="margin-bottom: 24px;">
    <div class="card-title">
        <i class="fa-solid fa-upload"></i> Upload Patient Dataset
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drag and drop your CSV file here",
    type=["csv"],
    help="Upload a CSV file containing patient admission and discharge data"
)

# ============ MAIN APPLICATION ============
if uploaded_file:
    # Load and process data
    df = pd.read_csv(uploaded_file)

    # Convert datetime columns
    df['Admission_Time'] = pd.to_datetime(df['Admission_Time'])
    df['Discharge_Time'] = pd.to_datetime(df['Discharge_Time'])

    # Calculate same-day flag
    df['Is_Same_Day'] = df['Admission_Time'].dt.date == df['Discharge_Time'].dt.date
    df['Stay_Duration_Days'] = (df['Discharge_Time'] - df['Admission_Time']).dt.total_seconds() / (24 * 3600)

    # ============ DATA INSIGHTS SECTION ============
    st.markdown("### 📊 Dataset Overview", unsafe_allow_html=True)

    col_insights = st.columns([1, 1, 1, 1])

    same_day_count = df['Is_Same_Day'].sum()
    unique_patients = df['Patient_ID'].nunique() if 'Patient_ID' in df.columns else 0
    unique_hospitals = df['Hospital_ID'].nunique() if 'Hospital_ID' in df.columns else 0
    avg_stay = df['Stay_Duration_Days'].mean()

    with col_insights[0]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">📄 {len(df):,}</div>
            <div class="kpi-label">Total Records</div>
        </div>
        """, unsafe_allow_html=True)

    with col_insights[1]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">⚡ {same_day_count:,}</div>
            <div class="kpi-label">Same-Day Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col_insights[2]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">🏥 {unique_hospitals:,}</div>
            <div class="kpi-label">Hospitals</div>
        </div>
        """, unsafe_allow_html=True)

    with col_insights[3]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">⏱️ {avg_stay:.1f}</div>
            <div class="kpi-label">Avg Stay (Days)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ PREVIEW SECTION ============
    st.markdown("""
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-title">
            <i class="fa-solid fa-table"></i> Dataset Preview
        </div>
    </div>
    """, unsafe_allow_html=True)

    preview_cols = st.columns([3, 1])

    with preview_cols[0]:
        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True
        )

    with preview_cols[1]:
        st.markdown("#### 📋 Column Info")
        col_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            col_info.append(f"**{col}**")
            col_info.append(f"_{dtype}_\n")
        st.markdown("\n".join(col_info))

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ============ ANALYSIS BUTTONS ============
    st.markdown("""
    <div class="card" style="margin-bottom: 24px;">
        <div class="card-title">
            <i class="fa-solid fa-magnifying-glass-chart"></i> Fraud Analysis Options
        </div>
        <p style="color: var(--muted); margin-bottom: 16px;">
            Select an analysis type to explore different fraud patterns in the data
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create tabs for different analysis options
    analysis_tabs = st.tabs([
        "🏥 Hospital Analysis",
        "📈 Time Patterns",
        "👥 Patient Patterns",
        "🔍 Detailed Detection",
        "📊 Visual Analytics"
    ])

    with analysis_tabs[0]:
        st.markdown("#### 🔎 Hospital Word Cloud Analysis")
        st.markdown("*Identify suspicious hospitals based on same-day discharge frequency*")

        col_h1, col_h2 = st.columns([1, 1])

        with col_h1:
            # Generate hospital word cloud
            if 'Hospital_ID' in df.columns and same_day_count > 0:
                same_day_df = df[df['Is_Same_Day'] == True]
                hospital_counts = same_day_df['Hospital_ID'].value_counts().to_dict()

                if hospital_counts:
                    # Create word cloud
                    fig, ax = plt.subplots(figsize=(10, 6))
                    plt.style.use('dark_background')

                    wordcloud = WordCloud(
                        width=800,
                        height=400,
                        background_color='#0d1220',
                        max_words=50,
                        colormap='viridis',
                        prefer_horizontal=0.7,
                        min_font_size=10,
                        max_font_size=100,
                        relative_scaling=0.5
                    ).generate_from_frequencies(hospital_counts)

                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    ax.set_title('Hospital Fraud Indicators - Word Cloud', fontsize=14, color='#6ee7ff', pad=20)

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='#0d1220')
                    buf.seek(0)
                    plt.close()

                    st.image(buf, use_container_width=True)
                else:
                    st.info("No same-day cases to analyze for hospital patterns")
            else:
                st.warning("Hospital data not available or no same-day cases found")

        with col_h2:
            st.markdown("##### 📊 Hospital Statistics")

            if 'Hospital_ID' in df.columns:
                # Calculate hospital fraud metrics
                hospital_stats = df.groupby('Hospital_ID').agg({
                    'Patient_ID': 'count',
                    'Is_Same_Day': 'sum'
                }).reset_index()
                hospital_stats.columns = ['Hospital_ID', 'Total_Cases', 'Same_Day_Cases']
                hospital_stats['Fraud_Rate_%'] = (hospital_stats['Same_Day_Cases'] / hospital_stats['Total_Cases'] * 100).round(2)
                hospital_stats = hospital_stats.sort_values('Fraud_Rate_%', ascending=False)

                # Highlight suspicious hospitals (>10% same-day rate)
                suspicious_hospitals = hospital_stats[hospital_stats['Fraud_Rate_%'] > 10]

                st.markdown(f"""
                <div class="stat-box" style="margin-bottom: 16px;">
                    <h4>Suspicious Hospitals (Fraud Rate {'>'}10%)</h4>
                    <div class="value">{len(suspicious_hospitals)}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Top 10 High-Risk Hospitals:**")
                st.dataframe(
                    suspicious_hospitals.head(10),
                    use_container_width=True,
                    hide_index=True
                )

                # Download hospital analysis
                csv_hospital = hospital_stats.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Hospital Analysis",
                    csv_hospital,
                    "hospital_fraud_analysis.csv",
                    key="hospital_download"
                )

    with analysis_tabs[1]:
        st.markdown("#### ⏰ Time Pattern Analysis")
        st.markdown("*Detect temporal fraud patterns based on admission/discharge times*")

        col_t1, col_t2 = st.columns([1, 1])

        with col_t1:
            # Time of day analysis
            df['Admission_Hour'] = df['Admission_Time'].dt.hour
            df['Discharge_Hour'] = df['Discharge_Time'].dt.hour

            # Create hour distribution
            fig = make_subplots(rows=1, cols=2,
                              subplot_titles=('Same-Day Admission Hours', 'Same-Day Discharge Hours'),
                              horizontal_spacing=0.15)

            same_day_df = df[df['Is_Same_Day'] == True]

            if len(same_day_df) > 0:
                # Admission hours
                admission_counts = same_day_df['Admission_Hour'].value_counts().sort_index()
                fig.add_trace(
                    go.Bar(x=admission_counts.index, y=admission_counts.values,
                          marker=dict(color='#6ee7ff', opacity=0.8)),
                    row=1, col=1
                )

                # Discharge hours
                discharge_counts = same_day_df['Discharge_Hour'].value_counts().sort_index()
                fig.add_trace(
                    go.Bar(x=discharge_counts.index, y=discharge_counts.values,
                          marker=dict(color='#8b5cf6', opacity=0.8)),
                    row=1, col=2
                )

                fig.update_xaxes(title_text="Hour of Day", row=1, col=1)
                fig.update_xaxes(title_text="Hour of Day", row=1, col=2)
                fig.update_yaxes(title_text="Count", row=1, col=1)
                fig.update_yaxes(title_text="Count", row=1, col=2)

                fig.update_layout(
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#eaf0ff'),
                    height=350,
                    margin=dict(l=40, r=40, t=40, b=40)
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No same-day cases for time analysis")

        with col_t2:
            st.markdown("##### 🔍 Time Pattern Insights")

            if len(same_day_df) > 0:
                # Morning vs evening analysis
                morning_admissions = len(same_day_df[(same_day_df['Admission_Hour'] >= 6) &
                                                     (same_day_df['Admission_Hour'] < 12)])
                evening_discharges = len(same_day_df[(same_day_df['Discharge_Hour'] >= 17) &
                                                      (same_day_df['Discharge_Hour'] < 21)])

                st.markdown(f"""
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Morning Admissions (6AM-12PM)</h4>
                    <div class="value">{morning_admissions} ({morning_admissions/len(same_day_df)*100:.1f}%)</div>
                </div>
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Evening Discharges (5PM-9PM)</h4>
                    <div class="value">{evening_discharges} ({evening_discharges/len(same_day_df)*100:.1f}%)</div>
                </div>
                """, unsafe_allow_html=True)

                # Suspicious patterns
                if morning_admissions > len(same_day_df) * 0.5:
                    st.markdown("""
                    <div class="danger-alert">
                        <strong>⚠️ High-Risk Pattern Detected</strong><br>
                        Majority of same-day admissions occur in morning hours
                    </div>
                    """, unsafe_allow_html=True)

    with analysis_tabs[2]:
        st.markdown("#### 👥 Patient Pattern Analysis")
        st.markdown("*Identify patients with multiple same-day admissions indicating potential fraud rings*")

        col_p1, col_p2 = st.columns([2, 1])

        with col_p1:
            if 'Patient_ID' in df.columns:
                # Patient fraud analysis
                patient_analysis = df[df['Is_Same_Day'] == True].groupby('Patient_ID').agg({
                    'Admission_Time': ['count', 'min', 'max'],
                    'Hospital_ID': lambda x: list(x.unique())
                }).reset_index()
                patient_analysis.columns = ['Patient_ID', 'Same_Day_Count', 'First_Admission', 'Last_Admission', 'Hospitals_Visited']

                # Flag patients with multiple same-day admissions
                repeat_offenders = patient_analysis[patient_analysis['Same_Day_Count'] > 1]

                if len(repeat_offenders) > 0:
                    st.markdown(f"**🚨 Found {len(repeat_offenders)} repeat offenders** (patients with multiple same-day admissions)")

                    st.dataframe(
                        repeat_offenders.sort_values('Same_Day_Count', ascending=False).head(15),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("No repeat offenders detected - each patient has at most one same-day admission")
            else:
                st.warning("Patient ID column not found in dataset")

        with col_p2:
            if 'Patient_ID' in df.columns:
                st.markdown("##### 📊 Patient Statistics")

                total_same_day_patients = len(patient_analysis)
                multi_occurrence = len(repeat_offenders) if len(repeat_offenders) > 0 else 0

                st.markdown(f"""
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Patients with Same-Day Cases</h4>
                    <div class="value">{total_same_day_patients}</div>
                </div>
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Repeat Offenders</h4>
                    <div class="value">{multi_occurrence}</div>
                </div>
                """, unsafe_allow_html=True)

                # Download patient analysis
                if len(patient_analysis) > 0:
                    csv_patient = patient_analysis.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "📥 Download Patient Analysis",
                        csv_patient,
                        "patient_fraud_analysis.csv",
                        key="patient_download"
                    )

    with analysis_tabs[3]:
        st.markdown("#### 🎯 Detailed Fraud Detection")
        st.markdown("*Comprehensive same-day fraud case detection with detailed metrics*")

        # Detection function
        def detect_same_day_fraud(df):
            result = df[df['Is_Same_Day'] == True].copy()
            result['Fraud_Flag'] = '⚠️ Same-Day Discharge'
            result['Duration_Hours'] = (result['Discharge_Time'] - result['Admission_Time']).dt.total_seconds() / 3600

            # Add risk score
            result['Risk_Score'] = 0
            if 'Hospital_ID' in result.columns:
                hospital_fraud_rate = df.groupby('Hospital_ID')['Is_Same_Day'].mean()
                result['Hospital_Fraud_Rate'] = result['Hospital_ID'].map(hospital_fraud_rate)
                result['Risk_Score'] = result['Hospital_Fraud_Rate'] * 100

            return result

        result_df = detect_same_day_fraud(df)

        col_d1, col_d2 = st.columns([2, 1])

        with col_d2:
            # Summary metrics
            st.markdown("##### 📊 Detection Summary")

            if len(result_df) > 0:
                st.markdown(f"""
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Total Same-Day Cases</h4>
                    <div class="value">{len(result_df):,}</div>
                </div>
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Unique Patients</h4>
                    <div class="value">{result_df['Patient_ID'].nunique():,}</div>
                </div>
                <div class="stat-box" style="margin-bottom: 12px;">
                    <h4>Avg Duration (Hours)</h4>
                    <div class="value">{result_df['Duration_Hours'].mean():.1f}h</div>
                </div>
                """, unsafe_allow_html=True)

                if 'Hospital_ID' in result_df.columns:
                    st.markdown(f"""
                    <div class="stat-box">
                        <h4>Suspicious Hospitals</h4>
                        <div class="value">{result_df['Hospital_ID'].nunique():,}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Download flagged cases
                csv = result_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Download All Flagged Cases",
                    csv,
                    "same_day_fraud_cases.csv",
                    key="fraud_download"
                )
            else:
                st.markdown("""
                <div class="success-alert">
                    ✅ No same-day fraud detected in the dataset
                </div>
                """, unsafe_allow_html=True)

        with col_d1:
            if len(result_df) > 0:
                st.markdown("##### 🚨 Flagged Cases")

                # Display with risk highlighting
                display_cols = ['Patient_ID', 'Admission_Time', 'Discharge_Time', 'Duration_Hours', 'Fraud_Flag']
                if 'Hospital_ID' in display_cols:
                    display_cols = ['Patient_ID', 'Hospital_ID', 'Admission_Time', 'Discharge_Time', 'Duration_Hours', 'Fraud_Flag']

                available_cols = [c for c in display_cols if c in result_df.columns]
                st.dataframe(
                    result_df[available_cols].sort_values('Duration_Hours', ascending=True).head(20),
                    use_container_width=True,
                    hide_index=True
                )

                if len(result_df) > 20:
                    st.info(f"Showing top 20 of {len(result_df):,} flagged cases. Download for complete data.")

    with analysis_tabs[4]:
        st.markdown("#### 📈 Visual Analytics Dashboard")
        st.markdown("*Interactive visualizations of fraud patterns*")

        col_v1, col_v2 = st.columns([1, 1])

        with col_v1:
            # Stay duration distribution
            fig = px.histogram(
                df,
                x='Stay_Duration_Days',
                nbins=30,
                title='Stay Duration Distribution',
                color_discrete_sequence=['#6ee7ff']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#eaf0ff'),
                height=350,
                showlegend=False,
                xaxis_title='Duration (Days)',
                yaxis_title='Count'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_v2:
            # Same-day vs multi-day
            stay_types = df['Is_Same_Day'].value_counts()
            fig = px.pie(
                values=[stay_types.get(False, 0), stay_types.get(True, 0)],
                names=['Multi-Day Stays', 'Same-Day Stays'],
                title='Stay Type Distribution',
                color=['#8b5cf6', '#6ee7ff'],
                hole=0.6
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#eaf0ff'),
                height=350,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        col_v3, col_v4 = st.columns([1, 1])

        with col_v3:
            # Monthly trend
            df['Month'] = df['Admission_Time'].dt.to_period('M')
            monthly = df.groupby('Month').agg({
                'Is_Same_Day': ['sum', 'count']
            }).reset_index()
            monthly.columns = ['Month', 'Same_Day', 'Total']
            monthly['Month'] = monthly['Month'].astype(str)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly['Month'],
                y=monthly['Total'],
                name='Total Admissions',
                line=dict(color='#8b5cf6', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=monthly['Month'],
                y=monthly['Same_Day'],
                name='Same-Day Cases',
                line=dict(color='#6ee7ff', width=2),
                fill='tozeroy'
            ))

            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#eaf0ff'),
                height=350,
                xaxis_title='Month',
                yaxis_title='Count',
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_v4:
            if 'Hospital_ID' in df.columns:
                # Hospital fraud rates
                hospital_metrics = df.groupby('Hospital_ID').agg({
                    'Is_Same_Day': ['sum', 'mean', 'count']
                }).reset_index()
                hospital_metrics.columns = ['Hospital_ID', 'Same_Day_Count', 'Fraud_Rate', 'Total_Cases']
                hospital_metrics = hospital_metrics.sort_values('Fraud_Rate', ascending=False).head(15)

                fig = px.bar(
                    hospital_metrics,
                    x='Hospital_ID',
                    y='Fraud_Rate',
                    title='Top 15 Hospitals by Fraud Rate',
                    color='Fraud_Rate',
                    color_continuous_scale='thermal'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#eaf0ff'),
                    height=350,
                    xaxis_title='Hospital ID',
                    yaxis_title='Fraud Rate',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Alternative chart - daily pattern
                df['DayOfWeek'] = df['Admission_Time'].dt.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_counts = df.groupby('DayOfWeek').size().reindex(day_order)

                fig = px.bar(
                    x=day_counts.index,
                    y=day_counts.values,
                    title='Admissions by Day of Week',
                    color=day_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#eaf0ff'),
                    height=350,
                    xaxis_title='Day of Week',
                    yaxis_title='Count',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

    # ============ COMMON OUTPUT SECTION ============
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <div class="card-title">
            <i class="fa-solid fa-flag-checkered"></i> Consolidated Fraud Report
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Summary Report
    if len(result_df) > 0:
        st.error(f"⚠️ **{len(result_df):,} same-day fraud cases detected!** Review the summary below.")

        col_r1, col_r2, col_r3, col_r4 = st.columns([1, 1, 1, 1])

        with col_r1:
            fraud_rate = len(result_df) / len(df) * 100
            st.metric("Fraud Rate", f"{fraud_rate:.1f}%")

        with col_r2:
            st.metric("Flagged Cases", len(result_df))

        with col_r3:
            st.metric("Patients Involved", result_df['Patient_ID'].nunique())

        with col_r4:
            if 'Hospital_ID' in result_df.columns:
                st.metric("Hospitals Involved", result_df['Hospital_ID'].nunique())
            else:
                st.metric("Avg Duration", f"{result_df['Duration_Hours'].mean():.1f}h")

        st.markdown("---")

        # Summary table
        st.markdown("#### 📋 Summary by Patient")
        patient_summary = result_df.groupby('Patient_ID').agg({
            'Admission_Time': 'count',
            'Hospital_ID': lambda x: x.nunique() if 'Hospital_ID' in df.columns else 0,
            'Duration_Hours': 'mean'
        }).reset_index()
        patient_summary.columns = ['Patient_ID', 'Same_Day_Visits', 'Hospitals_Visited', 'Avg_Duration_Hours']
        patient_summary = patient_summary.sort_values('Same_Day_Visits', ascending=False)

        st.dataframe(patient_summary, use_container_width=True, hide_index=True)

        # Final download
        st.markdown("---")
        csv_final = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Export Complete Analysis Report (CSV)",
            csv_final,
            f"fraud_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            key="final_download"
        )
    else:
        st.success("✅ **No fraud detected!** The dataset shows no suspicious same-day admission-discharge patterns.")

else:
    # Empty state
    st.markdown("""
    <div class="card" style="text-align: center; padding: 60px 20px;">
        <div style="margin-bottom: 24px;">
            <i class="fa-solid fa-shield-halved" style="font-size: 4rem; background: linear-gradient(135deg, var(--accent), var(--accent2)); -webkit-background-clip: text; background-clip: text; color: transparent;"></i>
        </div>
        <h2 style="margin: 0 0 12px; font-size: 1.5rem;">Upload Dataset to Begin Analysis</h2>
        <p style="color: var(--muted); margin: 0; max-width: 500px; margin-left: auto; margin-right: auto;">
            Upload a CSV file containing patient admission and discharge data to detect same-day fraud patterns
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sample data format
    st.markdown("""
    <div class="card" style="margin-top: 24px;">
        <div class="card-title">
            <i class="fa-solid fa-info-circle"></i> Expected Data Format
        </div>
        <p style="color: var(--muted); margin-bottom: 16px;">
            Your CSV should contain the following columns:
        </p>
        <code style="display: block; background: rgba(0,0,0,.3); padding: 16px; border-radius: 8px; overflow-x: auto;">
Patient_ID, Hospital_ID, Admission_Time, Discharge_Time<br>
P001, H001, 2024-01-15 08:00:00, 2024-01-15 18:00:00<br>
P002, H002, 2024-01-16 09:30:00, 2024-01-18 10:00:00<br>
...
        </code>
    </div>
    """, unsafe_allow_html=True)
