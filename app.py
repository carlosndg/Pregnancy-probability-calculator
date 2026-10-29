import streamlit as st
import math

st.set_page_config(
    page_title="Conception Probability Calculator",
    page_icon="🐄",
    layout="centered"
)

st.title("🐄 Dairy Cow Conception Probability Calculator")

st.write(
    "Enter the cow characteristics below to estimate the probability of conception."
)

# -----------------------
# Inputs
# -----------------------

herd_pai = st.number_input(
    "Herd Pregnancy per AI (decimal)",
    min_value=0.10,
    max_value=1.00,
    value=0.35,
    step=0.01
)

dim = st.number_input(
    "Days in Milk (DIM)",
    min_value=30,
    max_value=500,
    value=100
)

parity = st.selectbox(
    "Parity",
    ["1", "2", "3", "≥4"]
)

season = st.selectbox(
    "Season of insemination",
    ["Winter", "Spring", "Summer", "Fall"]
)

isi = st.selectbox(
    "Interservice interval",
    [
        "First bred",
        "<=17",
        "18-24",
        "25-35",
        "36-48",
        ">=49"
    ]
)

health = st.selectbox(
    "Health/Reproductive Event",
    [
        "Healthy",
        "Lameness",
        "Mastitis",
        "Metabolic",
        "Reproductive",
        "2 events",
        ">=3 events"
    ]
)

# -----------------------
# Coefficients
# -----------------------

intercept = -4.064

beta_herd = 3.367

beta_logdim = 1.095
beta_logdim2 = -0.116

parity_coef = {
    "1": 0,
    "2": -0.203,
    "3": -0.220,
    "≥4": -0.394
}

season_coef = {
    "Winter": 0,
    "Spring": -0.241,
    "Summer": -0.075,
    "Fall": 0.225
}

isi_coef = {
    "First bred": 0,
    "<=17": -0.534,
    "18-24": 0.120,
    "25-35": -0.165,
    "36-48": -0.107,
    ">=49": -0.125
}

health_coef = {
    "Healthy": 0,
    "Lameness": -0.141,
    "Mastitis": -0.052,
    "Metabolic": -0.205,
    "Reproductive": -0.474,
    "2 events": -0.396,
    ">=3 events": -0.526
}

# -----------------------
# Prediction
# -----------------------

if st.button("Calculate Probability"):

    log_dim = math.log(dim)

    eta = (
        intercept
        + beta_herd * herd_pai
        + beta_logdim * log_dim
        + beta_logdim2 * (log_dim ** 2)
        + parity_coef[parity]
        + season_coef[season]
        + isi_coef[isi]
        + health_coef[health]
    )

    probability = 1 / (1 + math.exp(-eta))

    st.subheader("Predicted Conception Probability")

    st.metric(
        label="Probability",
        value=f"{probability*100:.1f}%"
    )

    if probability >= 0.50:
        st.success("High predicted probability of conception.")
    elif probability >= 0.35:
        st.info("Moderate predicted probability of conception.")
    else:
        st.error("Low predicted probability of conception.")

    st.write("---")
    st.write("### Model Details")
    st.write(f"Linear predictor = **{eta:.3f}**")