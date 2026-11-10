
import streamlit as st
import math

st.set_page_config(
    page_title="Dairy Cow Conception Probability Calculator",
    page_icon="🐄",
    layout="centered"
)

st.title("🐄 Dairy Cow Conception Probability Calculator")

st.write(
    "Estimate the probability of conception using one of three "
    "regression models."
)

# ============================================================
# SHARED INPUTS
# ============================================================

st.subheader("Cow and Herd Characteristics")

col1, col2 = st.columns(2)

with col1:
    herd_pai = st.number_input(
        "Herd Pregnancy per AI (decimal)",
        min_value=0.10,
        max_value=1.00,
        value=0.30,
        step=0.01,
        format="%.2f"
    )

with col2:
    dim = st.number_input(
        "Days in Milk (DIM)",
        min_value=30,
        max_value=500,
        value=100,
        step=1
    )

col3, col4, col5 = st.columns(3)

with col3:
    parity = st.selectbox(
        "Parity",
        ["1", "2", "3", "≥4"]
    )

with col4:
    season = st.selectbox(
        "Insemination Season",
        ["Winter", "Spring", "Summer", "Fall"]
    )

with col5:
    isi = st.selectbox(
        "Interservice Interval (days)",
        [
            "First bred",
            "<=17",
            "18-24",
            "25-35",
            "36-48",
            ">=49"
        ]
    )

st.divider()

# ============================================================
# SHARED COEFFICIENTS: PARITY, SEASON, INTERSERVICE INTERVAL
# ============================================================

parity_coef_1 = {
    "1": 0,
    "2": -0.203,
    "3": -0.220,
    "≥4": -0.394
}

season_coef_1 = {
    "Winter": 0,
    "Spring": -0.241,
    "Summer": -0.075,
    "Fall": 0.225
}

isi_coef_1 = {
    "First bred": 0,
    "<=17": -0.534,
    "18-24": 0.120,
    "25-35": -0.165,
    "36-48": -0.107,
    ">=49": -0.125
}

# Model 2 coefficients
parity_coef_2 = {
    "1": 0,
    "2": -0.087,
    "3": -0.183,
    "≥4": -0.249
}

season_coef_2 = {
    "Winter": 0,
    "Spring": -0.016,
    "Summer": 0.262,
    "Fall": 0.284
}

isi_coef_2 = {
    "First bred": 0,
    "<=17": -0.247,
    "18-24": 0.283,
    "25-35": 0.038,
    "36-48": 0.111,
    ">=49": -0.056
}

# Model 3 coefficients
parity_coef_3 = {
    "1": 0,
    "2": -0.094,
    "3": -0.183,
    "≥4": -0.229
}

season_coef_3 = {
    "Winter": 0,
    "Spring": -0.022,
    "Summer": 0.244,
    "Fall": 0.267
}

isi_coef_3 = {
    "First bred": 0,
    "<=17": -0.250,
    "18-24": 0.263,
    "25-35": 0.035,
    "36-48": 0.066,
    ">=49": -0.109
}

# ============================================================
# MODEL-SPECIFIC COEFFICIENTS
# ============================================================

# MODEL 1: Health-Related Events
model1 = {
    "intercept": -4.064,
    "beta_herd": 3.367,
    "beta_logdim": 1.095,
    "beta_logdim2": -0.116,
    "parity": parity_coef_1,
    "season": season_coef_1,
    "isi": isi_coef_1
}

health_coef = {
    "Healthy": 0,
    "Lameness": -0.141,
    "Mastitis": -0.052,
    "Metabolic": -0.205,
    "Reproductive": -0.474,
    "2 events": -0.396,
    "≥3 events": -0.526
}

# MODEL 2: Relative Estrus Intensity (REI)
model2 = {
    "intercept": 0.076,
    "beta_herd": 4.610,
    "beta_logdim": -1.208,
    "beta_logdim2": 0.137,
    "parity": parity_coef_2,
    "season": season_coef_2,
    "isi": isi_coef_2
}

rei_coef = {
    "≤200%": 0,
    ">200–400%": 0.012,
    ">400–600%": 0.117,
    ">600%": 0.115
}

# MODEL 3: Combined HRE + REI
model3 = {
    "intercept": -0.065,
    "beta_herd": 4.336,
    "beta_logdim": -1.038,
    "beta_logdim2": 0.122,
    "parity": parity_coef_3,
    "season": season_coef_3,
    "isi": isi_coef_3
}

combo_coef = {
    "Healthy and ≤200% REI": -0.134,
    "Healthy and >200–400% REI": -0.118,
    "Healthy and >400–600% REI": -0.089,
    "Healthy and >600% REI": 0,

    "One HRE and ≤200% REI": -0.291,
    "One HRE and >200–400% REI": -0.237,
    "One HRE and >400–600% REI": -0.185,
    "One HRE and >600% REI": -0.279,

    "≥2 HRE and ≤200% REI": -0.552,
    "≥2 HRE and >200–400% REI": -0.654,
    "≥2 HRE and >400–600% REI": -0.030,
    "≥2 HRE and >600% REI": -0.170
}

# ============================================================
# PREDICTION FUNCTIONS
# ============================================================

def calculate_probability(model, additional_effect=0):
    log_dim = math.log(dim)

    eta = (
        model["intercept"]
        + model["beta_herd"] * herd_pai
        + model["beta_logdim"] * log_dim
        + model["beta_logdim2"] * (log_dim ** 2)
        + model["parity"][parity]
        + model["season"][season]
        + model["isi"][isi]
        + additional_effect
    )

    # Numerically stable logistic transformation
    if eta >= 0:
        probability = 1 / (1 + math.exp(-eta))
    else:
        exp_eta = math.exp(eta)
        probability = exp_eta / (1 + exp_eta)

    return eta, probability


def display_result(eta, probability):
    st.subheader("Predicted Conception Probability")

    st.metric(
        label="Probability",
        value=f"{probability * 100:.1f}%"
    )

    if probability >= 0.40:
        st.success("High predicted probability of conception.")
    elif probability >= 0.30:
        st.info("Moderate predicted probability of conception.")
    else:
        st.error("Low predicted probability of conception.")

    st.divider()

    with st.expander("Model Details"):
        st.write(f"Linear predictor (η): **{eta:.3f}**")
        st.write(
            "Logistic transformation: "
            "**P = 1 / (1 + exp(-η))**"
        )



# ============================================================
# CUSTOM CSS: INCREASE TAB FONT SIZE
# ============================================================

st.markdown("""
<style>
    /* Increase font size of tab labels */
    button[data-baseweb="tab"] {
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    /* Increase font size of tab text */
    button[data-baseweb="tab"] div p {
        font-size: 18px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# THREE MODEL TABS
# ============================================================

st.markdown(
    "<p style='font-size:20px; font-weight:600; margin-bottom:10px;'>"
    "Choose the model tab below"
    "</p>",
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "Model 1: Health–Related Events (HRE)",
    "Model 2: Relative Estrus Intensity (REI)",
    "Model 3: Combined (COMBO)"
])

# ------------------------------------------------------------
# TAB 1: HEALTH-RELATED EVENTS
# ------------------------------------------------------------

with tab1:
    st.header("Model 1: Health-Related Events")

    st.write(
        "This model accounts for health and reproductive events."
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
            "≥3 events"
        ],
        key="health_model1"
    )

    if st.button(
        "Calculate Probability",
        key="calculate_model1",
        type="primary"
    ):
        eta, probability = calculate_probability(
            model1,
            health_coef[health]
        )

        display_result(eta, probability)


# ------------------------------------------------------------
# TAB 2: RELATIVE ESTRUS INTENSITY
# ------------------------------------------------------------

with tab2:
    st.header("Model 2: Relative Estrus Intensity (REI)")

    st.write(
        "This model accounts for relative estrus intensity "
        "without including health-event categories."
    )

    rei = st.selectbox(
        "Relative Estrus Intensity (REI)",
        [
            "≤200%",
            ">200–400%",
            ">400–600%",
            ">600%"
        ],
        key="rei_model2"
    )

    if st.button(
        "Calculate Probability",
        key="calculate_model2",
        type="primary"
    ):
        eta, probability = calculate_probability(
            model2,
            rei_coef[rei]
        )

        display_result(eta, probability)


# ------------------------------------------------------------
# TAB 3: COMBINED HRE + REI
# ------------------------------------------------------------

with tab3:
    st.header("Model 3: Combined HRE + REI")

    st.write(
        "This model accounts for the combination of health-related "
        "events and relative estrus intensity."
    )

    combo = st.selectbox(
        "Health Events and Relative Estrus Intensity",
        [
            "Healthy and ≤200% REI",
            "Healthy and >200–400% REI",
            "Healthy and >400–600% REI",
            "Healthy and >600% REI",

            "One HRE and ≤200% REI",
            "One HRE and >200–400% REI",
            "One HRE and >400–600% REI",
            "One HRE and >600% REI",

            "≥2 HRE and ≤200% REI",
            "≥2 HRE and >200–400% REI",
            "≥2 HRE and >400–600% REI",
            "≥2 HRE and >600% REI"
        ],
        key="combo_model3"
    )

    if st.button(
        "Calculate Probability",
        key="calculate_model3",
        type="primary"
    ):
        eta, probability = calculate_probability(
            model3,
            combo_coef[combo]
        )

        display_result(eta, probability)

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "This calculator provides model-based estimates of conception "
    "probability. Predictions depend on the model coefficients "
    "and the characteristics entered. This web application was "
    "created from Niño de Guzmán et al. (2026). Dairy 7 (4), 58. "
    "https://doi.org/10.3390/dairy7040058" 
)
