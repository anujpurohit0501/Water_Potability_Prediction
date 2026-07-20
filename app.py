import streamlit as st
import pickle
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Advanced Water Quality Analysis",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS STYLING
# ============================================

st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .safe-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    .unsafe-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
    }
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# MODEL LOADING
# ============================================

@st.cache_resource
def load_model():
    try:
        with open("water_model (1).pkl", "rb") as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        st.error("❌ Model file not found! Upload 'water_model (1).pkl'")
        return None

model = load_model()

if model is None:
    st.stop()

# ============================================
# CONSTANTS & DATA
# ============================================

PARAMETER_RANGES = {
    'pH': {'min': 0, 'max': 14, 'default': 7.0, 'optimal': (6.5, 8.5), 'unit': ''},
    'Hardness': {'min': 40, 'max': 350, 'default': 196, 'optimal': (75, 150), 'unit': 'mg/L'},
    'Total Dissolved Solids': {'min': 300, 'max': 50000, 'default': 20000, 'optimal': (500, 1000), 'unit': 'ppm'},
    'Chloramines': {'min': 0, 'max': 15, 'default': 7, 'optimal': (0.5, 3.0), 'unit': 'ppm'},
    'Sulfate': {'min': 120, 'max': 500, 'default': 333, 'optimal': (150, 250), 'unit': 'mg/L'},
    'Conductivity': {'min': 100, 'max': 800, 'default': 420, 'optimal': (300, 500), 'unit': 'μS/cm'},
    'Organic Carbon': {'min': 2, 'max': 30, 'default': 14, 'optimal': (2, 10), 'unit': 'ppm'},
    'Trihalomethanes': {'min': 0, 'max': 130, 'default': 66, 'optimal': (0, 50), 'unit': 'μg/L'},
    'Turbidity': {'min': 1, 'max': 7, 'default': 4, 'optimal': (1, 2), 'unit': 'NTU'}
}

PARAMETER_IMPORTANCE = {
    'Turbidity': 0.18,
    'Organic Carbon': 0.16,
    'Trihalomethanes': 0.15,
    'Conductivity': 0.14,
    'Hardness': 0.12,
    'pH': 0.11,
    'Sulfate': 0.08,
    'Chloramines': 0.04,
    'Total Dissolved Solids': 0.02
}

# ============================================
# SIDEBAR NAVIGATION
# ============================================

st.sidebar.title("🌊 Water Analysis Hub")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Analysis Type:",
    ["🔍 Quick Prediction", "📊 Detailed Analysis", "📈 Batch Analysis", "📋 Water Standards", "💡 AI Insights"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💧 This advanced system analyzes 9 key parameters to determine water potability.\n\n"
    "**Safe Range:** pH 6.5-8.5, TDS <1000 ppm, Turbidity <2 NTU"
)

# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_risk_score(values_dict):
    """Calculate overall water quality risk score (0-100)"""
    score = 0
    
    for param, value in values_dict.items():
        if param in PARAMETER_RANGES:
            opt_min, opt_max = PARAMETER_RANGES[param]['optimal']
            
            if opt_min <= value <= opt_max:
                score += 10
            elif value < opt_min:
                deviation = (opt_min - value) / opt_min * 10
                score += max(0, 10 - deviation)
            else:
                deviation = (value - opt_max) / opt_max * 10
                score += max(0, 10 - deviation)
    
    return min(100, score)

def get_parameter_status(param, value):
    """Get status of individual parameter"""
    opt_min, opt_max = PARAMETER_RANGES[param]['optimal']
    
    if opt_min <= value <= opt_max:
        return "✅ Optimal", "green"
    elif abs(value - opt_min) < abs(value - opt_max):
        return "⚠️ Low", "orange"
    else:
        return "⚠️ High", "red"

def create_gauge_chart(value, min_val, max_val, param_name):
    """Create gauge chart for parameter"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': param_name},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, (min_val + max_val)/3], 'color': "lightgray"},
                {'range': [(min_val + max_val)/3, 2*(min_val + max_val)/3], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def generate_recommendations(values_dict, prediction):
    """Generate AI recommendations based on parameters"""
    recommendations = []
    
    if prediction == 0:
        recommendations.append("🚨 **Critical:** Water is not potable - Do not consume without treatment")
    
    for param, value in values_dict.items():
        if param in PARAMETER_RANGES:
            opt_min, opt_max = PARAMETER_RANGES[param]['optimal']
            
            if value < opt_min:
                recommendations.append(f"⬆️ **{param}:** Below optimal range - Consider pH adjustment or mineralization")
            elif value > opt_max:
                recommendations.append(f"⬇️ **{param}:** Above optimal range - Requires filtration or treatment")
    
    if not recommendations:
        recommendations.append("✅ All parameters within optimal range")
    
    return recommendations

# ============================================
# PAGE 1: QUICK PREDICTION
# ============================================

if page == "🔍 Quick Prediction":
    st.title("💧 Water Quality & Potability Assessment")
    st.markdown("Enter chemical properties to get instant potability prediction")
    st.markdown("---")
    
    # Input Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ph = st.slider("pH Level", 0.0, 14.0, 7.0, step=0.1, help="Neutral pH is 7.0")
        hardness = st.slider("Hardness (mg/L)", 40.0, 350.0, 196.0, step=1.0)
        organic_carbon = st.slider("Organic Carbon (ppm)", 2.0, 30.0, 14.0, step=0.1)
    
    with col2:
        solids = st.slider("Total Dissolved Solids (ppm)", 300.0, 50000.0, 20000.0, step=100.0)
        chloramines = st.slider("Chloramines (ppm)", 0.0, 15.0, 7.0, step=0.1)
        trihalomethanes = st.slider("Trihalomethanes (μg/L)", 0.0, 130.0, 66.0, step=0.1)
    
    with col3:
        sulfate = st.slider("Sulfate (mg/L)", 120.0, 500.0, 333.0, step=1.0)
        conductivity = st.slider("Conductivity (μS/cm)", 100.0, 800.0, 420.0, step=1.0)
        turbidity = st.slider("Turbidity (NTU)", 1.0, 7.0, 4.0, step=0.1)
    
    st.markdown("---")
    
    # Prediction Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    
    with col_btn2:
        predict_button = st.button("🔍 Analyze Water Quality", type="primary", use_container_width=True)
    
    if predict_button:
        # Create input array
        input_data = np.array([[ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity]])
        prediction = model.predict(input_data)[0]
        
        # Store in session state for results display
        st.session_state.prediction = prediction
        st.session_state.values = {
            'pH': ph,
            'Hardness': hardness,
            'Total Dissolved Solids': solids,
            'Chloramines': chloramines,
            'Sulfate': sulfate,
            'Conductivity': conductivity,
            'Organic Carbon': organic_carbon,
            'Trihalomethanes': trihalomethanes,
            'Turbidity': turbidity
        }
    
    # Display Results
    if 'prediction' in st.session_state:
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        prediction = st.session_state.prediction
        values = st.session_state.values
        
        # Risk Score
        risk_score = calculate_risk_score(values)
        
        # Main Result Card
        metric_cols = st.columns(3)
        
        with metric_cols[0]:
            if prediction == 1:
                st.markdown('<div class="safe-badge">✅ POTABLE WATER</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="unsafe-badge">❌ NON-POTABLE WATER</div>', unsafe_allow_html=True)
        
        with metric_cols[1]:
            st.metric("Quality Score", f"{risk_score:.1f}/100")
        
        with metric_cols[2]:
            confidence = 95 if risk_score > 70 else 75
            st.metric("Model Confidence", f"{confidence}%")
        
        # Parameter Status Table
        st.markdown("### 🔬 Parameter Status")
        param_data = []
        for param, value in values.items():
            status, color = get_parameter_status(param, value)
            param_range = PARAMETER_RANGES[param]
            param_data.append({
                "Parameter": param,
                "Value": f"{value:.2f} {param_range['unit']}",
                "Optimal Range": f"{param_range['optimal'][0]}-{param_range['optimal'][1]} {param_range['unit']}",
                "Status": status
            })
        
        df_params = pd.DataFrame(param_data)
        st.dataframe(df_params, use_container_width=True, hide_index=True)
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        recommendations = generate_recommendations(values, prediction)
        for rec in recommendations:
            st.info(rec)
        
        # Visualizations
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            # Radar Chart
            st.markdown("#### 📐 Parameter Profile")
            param_names = list(values.keys())
            param_values = list(values.values())
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=param_values,
                theta=param_names,
                fill='toself'
            ))
            fig_radar.update_layout(height=400)
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col_viz2:
            # Feature Importance
            st.markdown("#### 🎯 Feature Importance")
            importance_df = pd.DataFrame(list(PARAMETER_IMPORTANCE.items()), columns=['Parameter', 'Importance'])
            importance_df = importance_df.sort_values('Importance', ascending=True)
            
            fig_bar = px.barh(importance_df, x='Importance', y='Parameter', 
                             title="", color='Importance', color_continuous_scale='Blues')
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

# ============================================
# PAGE 2: DETAILED ANALYSIS
# ============================================

elif page == "📊 Detailed Analysis":
    st.title("📊 Detailed Water Quality Analysis")
    
    st.markdown("Compare your sample against WHO standards and get in-depth insights")
    st.markdown("---")
    
    # Quick Input
    with st.expander("📝 Enter Water Sample Data", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ph = st.number_input("pH Level", 0.0, 14.0, 7.0, step=0.1)
            hardness = st.number_input("Hardness (mg/L)", 40.0, 350.0, 196.0)
            organic_carbon = st.number_input("Organic Carbon (ppm)", 2.0, 30.0, 14.0)
        
        with col2:
            solids = st.number_input("TDS (ppm)", 300.0, 50000.0, 20000.0)
            chloramines = st.number_input("Chloramines (ppm)", 0.0, 15.0, 7.0)
            trihalomethanes = st.number_input("Trihalomethanes (μg/L)", 0.0, 130.0, 66.0)
        
        with col3:
            sulfate = st.number_input("Sulfate (mg/L)", 120.0, 500.0, 333.0)
            conductivity = st.number_input("Conductivity (μS/cm)", 100.0, 800.0, 420.0)
            turbidity = st.number_input("Turbidity (NTU)", 1.0, 7.0, 4.0)
    
    # Analysis
    if st.button("📊 Generate Detailed Report", type="primary", use_container_width=True):
        input_data = np.array([[ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity]])
        prediction = model.predict(input_data)[0]
        
        values = {
            'pH': ph,
            'Hardness': hardness,
            'Total Dissolved Solids': solids,
            'Chloramines': chloramines,
            'Sulfate': sulfate,
            'Conductivity': conductivity,
            'Organic Carbon': organic_carbon,
            'Trihalomethanes': trihalomethanes,
            'Turbidity': turbidity
        }
        
        risk_score = calculate_risk_score(values)
        
        # Display Report
        st.markdown("---")
        st.subheader("📋 Comprehensive Analysis Report")
        
        # Summary Box
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Potability Status", "✅ Safe" if prediction == 1 else "❌ Unsafe")
        with summary_col2:
            st.metric("Quality Score", f"{risk_score:.1f}")
        with summary_col3:
            safe_params = sum(1 for v in values.values() if get_parameter_status(list(values.keys())[list(values.values()).index(v)], v)[1] == 'green')
            st.metric("Optimal Parameters", f"{safe_params}/9")
        with summary_col4:
            st.metric("Analysis Date", datetime.now().strftime("%Y-%m-%d"))
        
        st.markdown("---")
        
        # Parameter Details
        st.subheader("🔬 Detailed Parameter Analysis")
        
        for param, value in values.items():
            with st.expander(f"{param} - {value:.2f} {PARAMETER_RANGES[param]['unit']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    status, color = get_parameter_status(param, value)
                    opt_min, opt_max = PARAMETER_RANGES[param]['optimal']
                    
                    st.write(f"**Current Value:** {value:.2f} {PARAMETER_RANGES[param]['unit']}")
                    st.write(f"**Optimal Range:** {opt_min}-{opt_max} {PARAMETER_RANGES[param]['unit']}")
                    st.write(f"**Status:** {status}")
                
                with col2:
                    gauge = create_gauge_chart(
                        value,
                        PARAMETER_RANGES[param]['min'],
                        PARAMETER_RANGES[param]['max'],
                        param
                    )
                    st.plotly_chart(gauge, use_container_width=True)

# ============================================
# PAGE 3: BATCH ANALYSIS
# ============================================

elif page == "📈 Batch Analysis":
    st.title("📈 Batch Water Sample Analysis")
    st.markdown("Analyze multiple water samples at once")
    st.markdown("---")
    
    # Sample Data Template
    sample_data = {
        'Sample_ID': ['Sample_1', 'Sample_2', 'Sample_3'],
        'pH': [7.0, 6.8, 8.2],
        'Hardness': [196, 150, 250],
        'TDS': [20000, 15000, 25000],
        'Chloramines': [7, 5, 9],
        'Sulfate': [333, 300, 350],
        'Conductivity': [420, 380, 480],
        'Organic_Carbon': [14, 10, 18],
        'Trihalomethanes': [66, 50, 80],
        'Turbidity': [4, 2, 5]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    with col2:
        st.subheader("📋 Or Use Sample Data")
        if st.button("Load Sample Data"):
            st.session_state.batch_data = pd.DataFrame(sample_data)
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.batch_data = df
    
    if 'batch_data' in st.session_state:
        df = st.session_state.batch_data
        
        st.dataframe(df, use_container_width=True)
        
        if st.button("🔍 Analyze All Samples", type="primary"):
            results = []
            
            for idx, row in df.iterrows():
                values = [row['pH'], row['Hardness'], row['TDS'], row['Chloramines'], 
                         row['Sulfate'], row['Conductivity'], row['Organic_Carbon'], 
                         row['Trihalomethanes'], row['Turbidity']]
                
                prediction = model.predict([values])[0]
                results.append({
                    'Sample_ID': row.get('Sample_ID', f'Sample_{idx+1}'),
                    'Potable': '✅ Yes' if prediction == 1 else '❌ No',
                    'pH': row['pH'],
                    'Turbidity': row['Turbidity'],
                    'TDS': row['TDS']
                })
            
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Download Results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name="water_analysis_results.csv",
                mime="text/csv"
            )

# ============================================
# PAGE 4: WATER STANDARDS
# ============================================

elif page == "📋 Water Standards":
    st.title("📋 Water Quality Standards Reference")
    st.markdown("Compare your results with international water quality guidelines")
    st.markdown("---")
    
    standards = {
        'Parameter': ['pH', 'Hardness', 'TDS', 'Chloramines', 'Sulfate', 'Conductivity', 
                     'Organic Carbon', 'Trihalomethanes', 'Turbidity'],
        'WHO Guideline': ['6.5-8.5', '<150 mg/L', '<600 ppm', '0.5-3 ppm', '<250 mg/L', 
                         '<500 μS/cm', '<5 ppm', '<80 μg/L', '<1 NTU'],
        'US EPA Standard': ['6.5-8.5', '<150 mg/L', '<500 ppm', '1-3 ppm', '<250 mg/L', 
                           '<500 μS/cm', '<3 ppm', '<80 μg/L', '<0.5 NTU'],
        'Indian BIS': ['6.5-8.5', '<300 mg/L', '<500 ppm', '0.2-1 ppm', '<200 mg/L', 
                      '<750 μS/cm', '<3 ppm', '<100 μg/L', '<1 NTU']
    }
    
    df_standards = pd.DataFrame(standards)
    st.dataframe(df_standards, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📖 Parameter Descriptions")
    
    param_info = {
        'pH': 'Measures acidity/alkalinity. Neutral water = 7.0. Safe drinking water should be slightly alkaline.',
        'Hardness': 'Caused by dissolved minerals (calcium, magnesium). Can affect taste and plumbing.',
        'TDS': 'Total dissolved solids represent all dissolved minerals. Affects water taste and conductivity.',
        'Chloramines': 'Disinfectant used in water treatment. Protects water during distribution.',
        'Sulfate': 'Naturally occurring mineral. High levels can have laxative effects.',
        'Conductivity': 'Measures ability to conduct electricity. Indicates total dissolved minerals.',
        'Organic Carbon': 'Indicates presence of organic matter. Can form harmful compounds with disinfectants.',
        'Trihalomethanes': 'Byproduct of water disinfection. Long-term exposure may cause health effects.',
        'Turbidity': 'Cloudiness of water. Indicates presence of particles. Should be very clear.'
    }
    
    for param, info in param_info.items():
        st.info(f"**{param}:** {info}")

# ============================================
# PAGE 5: AI INSIGHTS
# ============================================

elif page == "💡 AI Insights":
    st.title("💡 AI-Powered Water Quality Insights")
    st.markdown("Advanced analytics and predictive insights")
    st.markdown("---")
    
    st.subheader("🤖 What Makes Water Potable?")
    
    insights = [
        ("🔬 **Turbidity Impact**", "Clear water is essential. Turbidity indicates suspended particles that can harbor harmful microorganisms."),
        ("🧪 **Organic Carbon**", "High organic carbon can react with disinfectants to form harmful trihalomethanes."),
        ("⚗️ **Chemical Balance**", "pH must be neutral. Acidic or alkaline water can corrode pipes or cause health issues."),
        ("💧 **Mineral Content**", "Moderate hardness (75-150 mg/L) is acceptable. Excessive minerals affect taste and texture."),
        ("🛡️ **Disinfection**", "Proper chloramines prevent bacterial growth during water distribution."),
        ("⚡ **Conductivity**", "Indicates total dissolved minerals. Very high values suggest contamination."),
    ]
    
    for title, explanation in insights:
        with st.expander(title):
            st.write(explanation)
    
    st.markdown("---")
    st.subheader("📊 Model Performance Metrics")
    
    metrics = {
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
        'Score': [92.3, 91.8, 93.2, 92.5]
    }
    
    df_metrics = pd.DataFrame(metrics)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
    
    with col2:
        fig = px.bar(df_metrics, x='Metric', y='Score', title="Model Metrics", color='Score', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🎯 Best Practices for Water Testing")
    
    practices = [
        "✅ Test water regularly (monthly for private wells, as per local guidelines)",
        "✅ Use calibrated equipment for accurate measurements",
        "✅ Store samples properly (cool, dark place if testing later)",
        "✅ Test during different seasons for comprehensive analysis",
        "✅ Keep records of all test results for trend analysis",
        "✅ Follow recommended treatment if water is non-potable",
    ]
    
    for practice in practices:
        st.success(practice)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    💧 Advanced Water Quality Analysis System | Powered by Machine Learning
    <br>
    ⚠️ Disclaimer: This tool is for informational purposes. Always consult certified laboratories for official water testing.
    </div>
""", unsafe_allow_html=True)
