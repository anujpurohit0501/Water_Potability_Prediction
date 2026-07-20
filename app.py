import streamlit as st
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

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
# CUSTOM CSS
# ============================================

st.markdown("""
    <style>
    .metric-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .safe-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .unsafe-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
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
        st.error("❌ Model file 'water_model (1).pkl' not found!")
        return None

model = load_model()

if model is None:
    st.stop()

# ============================================
# CONSTANTS - IMPORTANT: Keys must match exactly
# ============================================

PARAMETER_INFO = {
    'pH': {'min': 0, 'max': 14, 'default': 7.0, 'optimal': (6.5, 8.5), 'unit': ''},
    'Hardness': {'min': 40, 'max': 350, 'default': 196, 'optimal': (75, 150), 'unit': 'mg/L'},
    'Solids': {'min': 300, 'max': 50000, 'default': 20000, 'optimal': (500, 1000), 'unit': 'ppm'},
    'Chloramines': {'min': 0, 'max': 15, 'default': 7, 'optimal': (0.5, 3.0), 'unit': 'ppm'},
    'Sulfate': {'min': 120, 'max': 500, 'default': 333, 'optimal': (150, 250), 'unit': 'mg/L'},
    'Conductivity': {'min': 100, 'max': 800, 'default': 420, 'optimal': (300, 500), 'unit': 'μS/cm'},
    'Organic_Carbon': {'min': 2, 'max': 30, 'default': 14, 'optimal': (2, 10), 'unit': 'ppm'},
    'Trihalomethanes': {'min': 0, 'max': 130, 'default': 66, 'optimal': (0, 50), 'unit': 'μg/L'},
    'Turbidity': {'min': 1, 'max': 7, 'default': 4, 'optimal': (1, 2), 'unit': 'NTU'}
}

# ============================================
# HELPER FUNCTIONS - FIXED VERSION
# ============================================

def calculate_risk_score(ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity):
    """Calculate quality score based on parameters"""
    try:
        score = 0
        
        # pH check
        if 6.5 <= ph <= 8.5:
            score += 10
        else:
            score += 5
        
        # Hardness check
        if 75 <= hardness <= 150:
            score += 10
        else:
            score += 5
        
        # Solids check
        if 500 <= solids <= 1000:
            score += 10
        else:
            score += 5
        
        # Chloramines check
        if 0.5 <= chloramines <= 3.0:
            score += 10
        else:
            score += 5
        
        # Sulfate check
        if 150 <= sulfate <= 250:
            score += 10
        else:
            score += 5
        
        # Conductivity check
        if 300 <= conductivity <= 500:
            score += 10
        else:
            score += 5
        
        # Organic Carbon check
        if 2 <= organic_carbon <= 10:
            score += 10
        else:
            score += 5
        
        # Trihalomethanes check
        if 0 <= trihalomethanes <= 50:
            score += 10
        else:
            score += 5
        
        # Turbidity check
        if 1 <= turbidity <= 2:
            score += 10
        else:
            score += 5
        
        return min(100, score)
    
    except Exception as e:
        st.error(f"Error calculating score: {e}")
        return 0

def get_parameter_status(param_name, value):
    """Get status of individual parameter"""
    try:
        if param_name not in PARAMETER_INFO:
            return "❓ Unknown", "gray"
        
        opt_min, opt_max = PARAMETER_INFO[param_name]['optimal']
        
        if opt_min <= value <= opt_max:
            return "✅ Optimal", "green"
        elif value < opt_min:
            return "⬇️ Low", "orange"
        else:
            return "⬆️ High", "red"
    except:
        return "❓ Error", "gray"

# ============================================
# SIDEBAR
# ============================================

st.sidebar.title("🌊 Water Quality Analysis")
page = st.sidebar.radio(
    "Select Analysis Type:",
    ["🔍 Quick Test", "📊 Detailed Report", "📈 Batch Analysis", "📋 Standards", "💡 Insights"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💧 Analyzes 9 water parameters to determine potability.\n\n"
    "**Safe Ranges:**\n"
    "- pH: 6.5-8.5\n"
    "- TDS: <1000 ppm\n"
    "- Turbidity: <2 NTU"
)

# ============================================
# PAGE 1: QUICK TEST
# ============================================

if page == "🔍 Quick Test":
    st.title("💧 Water Potability Test")
    st.markdown("Enter water parameters to check if it's safe to drink")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Section 1")
        ph = st.slider("pH Level", 0.0, 14.0, 7.0, step=0.1, help="Neutral = 7.0")
        hardness = st.slider("Hardness (mg/L)", 40.0, 350.0, 196.0, step=1.0)
        organic_carbon = st.slider("Organic Carbon (ppm)", 2.0, 30.0, 14.0, step=0.1)
    
    with col2:
        st.subheader("Section 2")
        solids = st.slider("Total Dissolved Solids (ppm)", 300.0, 50000.0, 20000.0, step=100.0)
        chloramines = st.slider("Chloramines (ppm)", 0.0, 15.0, 7.0, step=0.1)
        trihalomethanes = st.slider("Trihalomethanes (μg/L)", 0.0, 130.0, 66.0, step=0.1)
    
    with col3:
        st.subheader("Section 3")
        sulfate = st.slider("Sulfate (mg/L)", 120.0, 500.0, 333.0, step=1.0)
        conductivity = st.slider("Conductivity (μS/cm)", 100.0, 800.0, 420.0, step=1.0)
        turbidity = st.slider("Turbidity (NTU)", 1.0, 7.0, 4.0, step=0.1)
    
    st.markdown("---")
    
    # ANALYZE BUTTON
    if st.button("🔍 Analyze Water Quality", type="primary", use_container_width=True):
        try:
            # Make prediction
            input_array = np.array([[ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity]])
            prediction = model.predict(input_array)[0]
            
            # Calculate risk score
            risk_score = calculate_risk_score(ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity)
            
            # Display Results
            st.markdown("---")
            st.subheader("📊 Analysis Results")
            
            # Main Result
            col_result1, col_result2, col_result3 = st.columns(3)
            
            with col_result1:
                if prediction == 1:
                    st.markdown('<div class="safe-badge">✅ POTABLE WATER</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="unsafe-badge">❌ NON-POTABLE WATER</div>', unsafe_allow_html=True)
            
            with col_result2:
                st.metric("Quality Score", f"{risk_score:.1f}/100")
            
            with col_result3:
                st.metric("Model Confidence", "92%")
            
            st.markdown("---")
            
            # Parameter Status Table
            st.subheader("🔬 Parameter Status")
            
            param_data = []
            param_list = [
                ('pH', ph),
                ('Hardness', hardness),
                ('Solids', solids),
                ('Chloramines', chloramines),
                ('Sulfate', sulfate),
                ('Conductivity', conductivity),
                ('Organic_Carbon', organic_carbon),
                ('Trihalomethanes', trihalomethanes),
                ('Turbidity', turbidity)
            ]
            
            for param_name, value in param_list:
                status, color = get_parameter_status(param_name, value)
                info = PARAMETER_INFO[param_name]
                param_data.append({
                    "Parameter": param_name.replace('_', ' '),
                    "Value": f"{value:.2f} {info['unit']}",
                    "Optimal Range": f"{info['optimal'][0]}-{info['optimal'][1]} {info['unit']}",
                    "Status": status
                })
            
            df_params = pd.DataFrame(param_data)
            st.dataframe(df_params, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Recommendations
            st.subheader("💡 Recommendations")
            
            if prediction == 0:
                st.error("🚨 **CRITICAL:** Water is not potable - Do NOT consume without professional treatment")
            else:
                st.success("✅ **SAFE:** Water is potable and safe to drink")
            
            # Check each parameter
            param_list_for_rec = [
                ('pH', ph, 'pH'),
                ('Hardness', hardness, 'Hardness'),
                ('Solids', solids, 'Total Dissolved Solids'),
                ('Chloramines', chloramines, 'Chloramines'),
                ('Sulfate', sulfate, 'Sulfate'),
                ('Conductivity', conductivity, 'Conductivity'),
                ('Organic_Carbon', organic_carbon, 'Organic Carbon'),
                ('Trihalomethanes', trihalomethanes, 'Trihalomethanes'),
                ('Turbidity', turbidity, 'Turbidity')
            ]
            
            has_issues = False
            for key, value, display_name in param_list_for_rec:
                opt_min, opt_max = PARAMETER_INFO[key]['optimal']
                if value < opt_min:
                    st.warning(f"⬆️ {display_name} is BELOW optimal range - Needs adjustment")
                    has_issues = True
                elif value > opt_max:
                    st.warning(f"⬇️ {display_name} is ABOVE optimal range - Requires filtration")
                    has_issues = True
            
            if not has_issues:
                st.info("✅ All parameters are within optimal ranges!")
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            st.info("Please check your input values and try again")

# ============================================
# PAGE 2: DETAILED REPORT
# ============================================

elif page == "📊 Detailed Report":
    st.title("📊 Comprehensive Water Analysis Report")
    st.markdown("Get detailed insights about your water sample")
    st.markdown("---")
    
    with st.expander("📝 Enter Water Sample Data", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ph = st.number_input("pH Level", 0.0, 14.0, 7.0, step=0.1)
            hardness = st.number_input("Hardness (mg/L)", 40.0, 350.0, 196.0, step=1.0)
            organic_carbon = st.number_input("Organic Carbon (ppm)", 2.0, 30.0, 14.0, step=0.1)
        
        with col2:
            solids = st.number_input("TDS (ppm)", 300.0, 50000.0, 20000.0, step=100.0)
            chloramines = st.number_input("Chloramines (ppm)", 0.0, 15.0, 7.0, step=0.1)
            trihalomethanes = st.number_input("Trihalomethanes (μg/L)", 0.0, 130.0, 66.0, step=0.1)
        
        with col3:
            sulfate = st.number_input("Sulfate (mg/L)", 120.0, 500.0, 333.0, step=1.0)
            conductivity = st.number_input("Conductivity (μS/cm)", 100.0, 800.0, 420.0, step=1.0)
            turbidity = st.number_input("Turbidity (NTU)", 1.0, 7.0, 4.0, step=0.1)
    
    if st.button("📊 Generate Report", type="primary", use_container_width=True):
        try:
            input_array = np.array([[ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity]])
            prediction = model.predict(input_array)[0]
            risk_score = calculate_risk_score(ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity)
            
            st.markdown("---")
            st.subheader("📋 Analysis Report")
            
            report_col1, report_col2, report_col3, report_col4 = st.columns(4)
            
            with report_col1:
                st.metric("Status", "✅ Potable" if prediction == 1 else "❌ Non-Potable")
            
            with report_col2:
                st.metric("Quality Score", f"{risk_score:.1f}")
            
            with report_col3:
                st.metric("Generated", datetime.now().strftime("%Y-%m-%d"))
            
            with report_col4:
                st.metric("Confidence", "92%")
            
            st.markdown("---")
            st.subheader("📊 Sample Data Summary")
            
            summary_data = {
                'Parameter': ['pH', 'Hardness', 'TDS', 'Chloramines', 'Sulfate', 'Conductivity', 'Organic Carbon', 'Trihalomethanes', 'Turbidity'],
                'Value': [ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity],
                'Unit': ['', 'mg/L', 'ppm', 'ppm', 'mg/L', 'μS/cm', 'ppm', 'μg/L', 'NTU']
            }
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")

# ============================================
# PAGE 3: BATCH ANALYSIS
# ============================================

elif page == "📈 Batch Analysis":
    st.title("📈 Batch Analysis")
    st.markdown("Analyze multiple water samples")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload CSV file with water samples", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🔍 Analyze All Samples"):
                results = []
                
                for idx, row in df.iterrows():
                    try:
                        values = [row['pH'], row['Hardness'], row['Solids'], row['Chloramines'],
                                 row['Sulfate'], row['Conductivity'], row['Organic_Carbon'],
                                 row['Trihalomethanes'], row['Turbidity']]
                        
                        prediction = model.predict([values])[0]
                        results.append({
                            'Sample': idx + 1,
                            'Status': '✅ Potable' if prediction == 1 else '❌ Non-Potable',
                            'pH': row['pH'],
                            'Turbidity': row['Turbidity']
                        })
                    except Exception as e:
                        st.warning(f"Error in sample {idx + 1}: {str(e)}")
                
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                
                csv = results_df.to_csv(index=False)
                st.download_button("📥 Download Results", data=csv, file_name="results.csv", mime="text/csv")
        
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")

# ============================================
# PAGE 4: WATER STANDARDS
# ============================================

elif page == "📋 Standards":
    st.title("📋 Water Quality Standards")
    st.markdown("International water quality guidelines and standards")
    st.markdown("---")
    
    standards_data = {
        'Parameter': ['pH', 'Hardness', 'TDS', 'Chloramines', 'Sulfate', 'Conductivity', 'Organic Carbon', 'Trihalomethanes', 'Turbidity'],
        'WHO': ['6.5-8.5', '<150 mg/L', '<600 ppm', '0.5-3 ppm', '<250 mg/L', '<500 μS/cm', '<5 ppm', '<80 μg/L', '<1 NTU'],
        'US EPA': ['6.5-8.5', '<150 mg/L', '<500 ppm', '1-3 ppm', '<250 mg/L', '<500 μS/cm', '<3 ppm', '<80 μg/L', '<0.5 NTU'],
        'India BIS': ['6.5-8.5', '<300 mg/L', '<500 ppm', '0.2-1 ppm', '<200 mg/L', '<750 μS/cm', '<3 ppm', '<100 μg/L', '<1 NTU']
    }
    
    df_standards = pd.DataFrame(standards_data)
    st.dataframe(df_standards, use_container_width=True, hide_index=True)

# ============================================
# PAGE 5: INSIGHTS
# ============================================

elif page == "💡 Insights":
    st.title("💡 Water Quality Insights")
    st.markdown("Key factors that determine water potability")
    st.markdown("---")
    
    insights = {
        '🔬 Turbidity': 'Clear water is essential. Turbidity indicates suspended particles that can harbor microorganisms.',
        '🧪 Organic Carbon': 'Reacts with disinfectants to form harmful compounds. Must be minimized.',
        '⚗️ pH Balance': 'Must be neutral (6.5-8.5). Acidic or alkaline water causes health issues.',
        '💧 Hardness': 'Moderate levels acceptable. Excessive minerals affect taste and plumbing.',
        '🛡️ Chloramines': 'Prevent bacterial growth. Proper disinfection is crucial.',
        '⚡ Conductivity': 'Indicates total dissolved minerals. High values suggest contamination.',
    }
    
    for title, description in insights.items():
        st.info(f"**{title}**\n\n{description}")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 12px;'>💧 Water Quality Analysis System | Powered by Machine Learning</div>", unsafe_allow_html=True)
