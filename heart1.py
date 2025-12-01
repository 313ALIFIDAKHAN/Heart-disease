import streamlit as st
import heapq

# ------------------------------------------------------------------
#                    HEART DISEASE A* DIAGNOSTIC SYSTEM
# ------------------------------------------------------------------

st.set_page_config(page_title="Heart Disease A* Diagnostic", page_icon="❤️", layout="wide")

# ---------------------------- CUSTOM PAGE UI -----------------------
st.markdown("""
<style>
    body { background-color:#eef2f7; }
    .title { text-align:center; font-size:42px; font-weight:800; color:#d93644; margin-top:15px; }
    .subtitle { text-align:center; font-size:18px; color:#555; margin-bottom:40px;}
    .card {
        background:white; padding:30px; margin-bottom:18px;
        border-radius:16px; box-shadow:0 4px 14px rgba(0,0,0,0.1);
    }
    .result-card{
        background:#fff; padding:25px; border-radius:14px;
        margin:15px 0; border-left:6px solid #d93644;
        box-shadow:0 2px 10px rgba(0,0,0,0.06);
    }
    .d-title{font-size:22px;font-weight:800;color:#d93644;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>❤️ A* Heart Disease Diagnostic Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-Guided Risk Ranking using Symptom-Probability Heuristic</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
#                HEART DISEASE MEDICAL GRAPH (SEARCH NODES)
# ------------------------------------------------------------------

heart_graph = {
    "Coronary Artery Disease": {
        "symptoms": ["chest pain", "shortness of breath", "fatigue", "nausea", "sweating"],
        "severity": 0.92,
        "advice": "Immediate evaluation recommended. ECG, lipid profile, aspirin therapy if prescribed."
    },
    "Heart Failure": {
        "symptoms": ["swelling legs", "fatigue", "shortness of breath", "rapid heartbeat", "persistent cough"],
        "severity": 0.87,
        "advice": "Limit salt, diuretics may be needed. Echocardiography evaluation is required."
    },
    "Arrhythmia": {
        "symptoms": ["irregular heartbeat", "dizziness", "fainting", "fluttering chest"],
        "severity": 0.75,
        "advice": "Avoid caffeine & stress. ECG monitoring recommended."
    },
    "Hypertension (High BP)": {
        "symptoms": ["headache", "dizziness", "nosebleeds", "vision problems"],
        "severity": 0.70,
        "advice": "Reduce salt, maintain weight, regular BP checks. Medication may be needed."
    },
    "Heart Attack (Myocardial Infarction)": {
        "symptoms": ["severe chest pain", "left arm pain", "sweating", "nausea", "breathlessness"],
        "severity": 0.98,
        "advice": "EMERGENCY. Call emergency services immediately."
    }
}


# ------------------------------------------------------------------
#                   A* HEURISTIC RISK ESTIMATOR
# ------------------------------------------------------------------
def heuristic(match_count, total, severity):
    if total == 0: return 0
    symptom_match_weight = (match_count / total) * 0.65
    severity_weight = severity * 0.35
    return symptom_match_weight + severity_weight


def a_star_assess(user_symptoms):
    pq = []
    results = []

    for disease, data in heart_graph.items():
        matches = len(set(user_symptoms) & set(data["symptoms"]))
        score = heuristic(matches, len(data["symptoms"]), data["severity"])
        heapq.heappush(pq, (-score, disease))

    while pq:
        score, disease = heapq.heappop(pq)
        results.append((disease, -score))

    return results


# ------------------------------------------------------------------
#                          USER INPUT PANEL
# ------------------------------------------------------------------

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.write("### 🔍 Enter your symptoms (comma separated)")
    symptoms_input = st.text_area("e.g. chest pain, sweating, left arm pain", height=100)

    analyze = st.button("Analyze Heart Risk ❤️", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
#                           RESULT DISPLAY
# ------------------------------------------------------------------

if analyze and symptoms_input.strip() != "":
    user_symptoms = [x.strip().lower() for x in symptoms_input.split(",")]
    results = a_star_assess(user_symptoms)

    st.markdown("## 🧭 Diagnostic Ranking")
    st.write("Higher score = stronger match based on symptom similarity + severity risk")

    for disease, score in results:
        data = heart_graph[disease]
        match = len(set(user_symptoms) & set(data["symptoms"]))

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='d-title'>{disease}</div>", unsafe_allow_html=True)
        st.progress(score)  # smooth probability bar
        st.write(f"**Risk Score:** {round(score*100,2)}%")
        st.write(f"**Matched Symptoms:** `{match}`")
        st.write(f"**Typical Symptoms:** {', '.join(data['symptoms'])}")
        st.write(f"**Recommended Action:** {data['advice']}")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("Enter symptoms to begin assessment.")
