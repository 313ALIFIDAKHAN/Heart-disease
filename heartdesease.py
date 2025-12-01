"""Heart Disease forward-chaining rule engine and Streamlit UI."""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Any

# ---------------------------
# Rule representation
# ---------------------------
@dataclass
class InferenceRule:
    identifier: str
    conditions: List[Tuple[str, str, Any]]  # (fact_key, operator, value)
    conclusion: Tuple[str, Any]            # (new_fact_key, new_value)
    priority: int = 0

# ---------------------------
# Condition checker
# ---------------------------
def check_condition(condition: Tuple[str, str, Any], facts: Dict[str, Any]) -> bool:
    key, operator, value = condition
    if key not in facts:
        return False
    current_value = facts[key]

    ops = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        ">":  lambda a, b: a > b,
        "<":  lambda a, b: a < b,
    }

    fn = ops.get(operator)
    if fn is None:
        return False
    return fn(current_value, value)

# ---------------------------
# Forward Chaining Engine
# ---------------------------
class HeartDiseaseEngine:
    def __init__(self, rules: List[InferenceRule]):
        # Highest priority rules are evaluated first
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)

    def run(self, initial_facts: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        facts = dict(initial_facts)
        triggered_rules = []
        new_fact_added = True

        while new_fact_added:
            new_fact_added = False
            for rule in self.rules:
                if rule.identifier in triggered_rules:
                    continue
                if all(check_condition(cond, facts) for cond in rule.conditions):
                    fact_key, fact_value = rule.conclusion
                    if facts.get(fact_key) != fact_value:
                        facts[fact_key] = fact_value
                        triggered_rules.append(rule.identifier)
                        new_fact_added = True

        return facts, triggered_rules

# ---------------------------
# Heart Disease Knowledge Base
# ---------------------------
def heart_disease_rules() -> List[InferenceRule]:
    """
    Stages:
    Stage1 -> Symptom check
    Stage2 -> Risk factor check
    Stage3 -> Lab and imaging confirmation
    Stage4 -> Confirmed diagnosis
    Stage5 -> Treatment plan
    Fallback rules ensure some final advice always exists.
    """
    rules = [

        # Stage 1: Symptom screening
        InferenceRule(
            identifier="S1: core symptoms => suspect",
            conditions=[("core_symptoms", "==", 1)],
            conclusion=("stage1", 1),
            priority=10
        ),
        InferenceRule(
            identifier="S2: multiple symptoms >=3",
            conditions=[("symptom_count", ">=", 3)],
            conclusion=("stage1", 1),
            priority=9
        ),

        # Stage 2: Risk assessment
        InferenceRule(
            identifier="R1: high risk factors present",
            conditions=[
                ("stage1", "==", 1),
                ("risk_count", ">=", 2),
                ("strong_risk", "==", 1)
            ],
            conclusion=("stage2", 1),
            priority=8
        ),

        # Stage 3: Lab and imaging confirmation
        InferenceRule(
            identifier="L1: positive tests + duration",
            conditions=[
                ("stage2", "==", 1),
                ("duration", "==", 1),
                ("positive_lab_count", ">=", 1)
            ],
            conclusion=("stage3", 1),
            priority=7
        ),

        # Stage 4: Confirmed diagnosis
        InferenceRule(
            identifier="C1: repeat positive + ruled out other",
            conditions=[
                ("stage3", "==", 1),
                ("repeat", "==", 1),
                ("ruled_out_other", "==", 1)
            ],
            conclusion=("stage4", 1),
            priority=6
        ),

        # Stage 5: Treatment plan
        InferenceRule(
            identifier="T1: confirmed + no contraindication",
            conditions=[("stage4", "==", 1), ("contra", "==", 0)],
            conclusion=("final", "Confirmed Heart Disease. Start ACE inhibitors + lifestyle management."),
            priority=5
        ),
        InferenceRule(
            identifier="T2: confirmed + contraindication",
            conditions=[("stage4", "==", 1), ("contra", "==", 1)],
            conclusion=("final", "Confirmed Heart Disease. ACE inhibitors contraindicated, use alternative therapy."),
            priority=5
        ),

        # -------------------------
        # Fallback plans
        # -------------------------
        InferenceRule(
            identifier="Plan-Stage3: likely but not confirmed",
            conditions=[("stage3", "==", 1), ("stage4", "!=", 1)],
            conclusion=("final", "Heart disease likely. Repeat tests and begin lifestyle modifications."),
            priority=4
        ),
        InferenceRule(
            identifier="Plan-Stage2: high risk but labs inconclusive",
            conditions=[("stage2", "==", 1), ("stage3", "!=", 1)],
            conclusion=("final", "High risk of heart disease. Order ECG, echocardiography, and labs."),
            priority=3
        ),
        InferenceRule(
            identifier="Plan-Stage1: symptoms only",
            conditions=[("stage1", "==", 1), ("stage2", "!=", 1)],
            conclusion=("final", "Symptoms suggest screening. Advise ECG and lifestyle evaluation."),
            priority=2
        ),
        InferenceRule(
            identifier="Plan-0: low suspicion",
            conditions=[("stage1", "!=", 1)],
            conclusion=("final", "Low suspicion. Monitor and reassess if symptoms increase."),
            priority=1
        ),
    ]
    return rules
# Precompute rules once to avoid rebuilding on every UI render
RULES: List[InferenceRule] = heart_disease_rules()


def build_graph_dot(rules: List[InferenceRule], fired_rules: List[str] | None = None) -> str:
    fired_rules = fired_rules or []
    lines = ["digraph G {", "rankdir=LR;", 'node [shape=box, style="rounded,filled", fillcolor="#ffffff"];']

    # Collect unique fact keys
    fact_keys = set()
    for r in rules:
        for c in r.conditions:
            fact_keys.add(c[0])
        fact_keys.add(r.conclusion[0])

    for fk in sorted(fact_keys):
        lines.append(f'"{fk}" [shape=oval, fillcolor="#ffffe0"];')

    for i, r in enumerate(rules):
        rn = f"rule_{i}"
        label = r.identifier.replace('"', "\\\"")
        color = "#b3e6b3" if r.identifier in fired_rules else "#e6f0ff"
        lines.append(f'"{rn}" [label="{label}", shape=box, style="filled", fillcolor="{color}"];')
        for cond in r.conditions:
            fk = cond[0]
            lines.append(f'"{fk}" -> "{rn}";')
        concl = r.conclusion[0]
        lines.append(f'"{rn}" -> "{concl}";')

    lines.append("}")
    return "\n".join(lines)
# ---------------------------
# Streamlit app entrypoint (only executed when run via `streamlit run`)
# ---------------------------
def run_streamlit_app():
    import streamlit as st

    st.set_page_config(page_title="Heart Disease Diagnosis", page_icon="❤️", layout="centered")
    st.title("🫀 Heart Disease Diagnostic System")

    # ---------------------------
    # User Input Section
    # ---------------------------
    st.header("Patient Information")

    # List of common symptoms for selection
    symptom_options = [
        "Chest pain",
        "Shortness of breath",
        "Dizziness",
        "Palpitations",
        "Fatigue",
        "Syncope",
        "Nausea",
        "Sweating",
        "Arm/neck/jaw pain",
    ]

    # Use precomputed rules for graph and execution
    rules_for_graph = RULES

    with st.form("heart_form"):
        st.subheader("Symptoms")
        selected_symptoms = st.multiselect("Select present symptoms", symptom_options)
        # Core symptoms cluster: require both Chest pain and Shortness of breath
        core_symptoms = 1 if {"Chest pain", "Shortness of breath"}.issubset(set(selected_symptoms)) else 0
        symptom_count = len(selected_symptoms)

        st.subheader("Risk Factors")
        risk_count = st.slider("Number of risk factors", 0, 10, 0)
        strong_risk = st.checkbox("Any strong risk factor present?")

        st.subheader("Lab & Test Data")
        duration = st.checkbox("Symptoms or conditions present for more than 6 months?")
        positive_lab_count = st.slider("Number of positive lab results", 0, 5, 0)
        repeat = st.checkbox("Repeat positive tests confirmed?")
        ruled_out_other = st.checkbox("Other causes ruled out?")

        st.subheader("Treatment Considerations")
        contra = st.checkbox("Contraindication to first-line therapy?")

        submitted = st.form_submit_button("Run Diagnosis")

    # Knowledge Graph Visualization uses module-level `build_graph_dot` for efficiency

    st.subheader("Knowledge Graph")
    st.info("Rules and fact-flow for the forward-chaining engine. After running diagnosis, fired rules will be highlighted.")
    st.graphviz_chart(build_graph_dot(rules_for_graph))

    # ---------------------------
    # Run Forward Chaining
    # ---------------------------
    if submitted:
        # Convert boolean inputs to int (1=yes, 0=no)
        facts = {
            "core_symptoms": int(core_symptoms),
            "symptom_count": symptom_count,
            "risk_count": risk_count,
            "strong_risk": int(strong_risk),
            "duration": int(duration),
            "positive_lab_count": positive_lab_count,
            "repeat": int(repeat),
            "ruled_out_other": int(ruled_out_other),
            "contra": int(contra)
        }

        # Load rules and run engine
        rules = RULES
        engine = HeartDiseaseEngine(rules)
        final_facts, fired_rules = engine.run(facts)

        # Display Results
        st.header("🩺 Diagnosis Result")
        st.success(final_facts.get("final", "No diagnosis could be made."))

        st.header("📜 Rules Fired")
        if fired_rules:
            for r in fired_rules:
                st.write(f"- {r}")
        else:
            st.write("No rules fired.")

        # Re-render graph with fired rules highlighted
        st.subheader("Forward Chaining Trace")
        st.graphviz_chart(build_graph_dot(rules, fired_rules))


if __name__ == "__main__":
    run_streamlit_app()
