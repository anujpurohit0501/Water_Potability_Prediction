import streamlit as st
import pickle
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="Water Potability Predictor",
    page_icon="💧",
    layout="centered"
)

# Model Load karne ka function
@st.cache_resource
def load_model():
    with open("water_model(1).pkl", "rb") as file:
        model = pickle.load(file)
    return model

try:
    model = load_model()
except FileNotFoundError:
    st.error("❌ 'water_model.pkl' nahi mili! Check karo ki file GitHub repository ke main folder me hai na?")
    st.stop()

# Title
st.title("💧 Water Quality & Potability Assessment")
st.write("Enter the chemical properties below to test if the water is safe for consumption.")
st.markdown("---")

# Input Sliders
st.subheader("📊 Water Chemical Properties")
col1, col2 = st.columns(2)

with col1:
    ph = st.slider("pH Level (0 - 14)", 0.0, 14.0, 7.0, step=0.1)
    hardness = st.slider("Hardness (mg/L)", 40.0, 350.0, 196.0, step=1.0)
    solids = st.slider("Total Dissolved Solids - TDS (ppm)", 300.0, 50000.0, 20000.0, step=100.0)
    chloramines = st.slider("Chloramines (ppm)", 0.0, 15.0, 7.0, step=0.1)

with col2:
    sulfate = st.slider("Sulfate (mg/L)", 120.0, 500.0, 333.0, step=1.0)
    conductivity = st.slider("Conductivity (μS/cm)", 100.0, 800.0, 420.0, step=1.0)
    organic_carbon = st.slider("Organic Carbon (ppm)", 2.0, 30.0, 14.0, step=0.1)
    trihalomethanes = st.slider("Trihalomethanes (μg/L)", 0.0, 130.0, 66.0, step=0.1)
    turbidity = st.slider("Turbidity (NTU)", 1.0, 7.0, 4.0, step=0.1)

st.markdown("---")

# Prediction
if st.button("🔍 Check Water Potability", type="primary"):
    # Features ka sequence input array me daalna
    input_data = np.array([[ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity]])
    
    prediction = model.predict(input_data)
    
    st.subheader("Analysis Result:")
    if prediction[0] == 1:
        st.success("✅ **Safe to Drink!** The water sample is potable.")
        st.balloons()
    else:
        st.error("❌ **Unsafe to Drink!** The water sample is contaminated and not potable.")
