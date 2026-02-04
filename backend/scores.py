"""Same scoring logic as frontend utils/scores.ts."""

SYMPTOM_KEYS = [
    "fatigue", "breathlessness", "cough", "pain", "nausea", "dizziness",
    "swelling", "anxiety", "headache", "chest_tightness", "joint_stiffness",
    "skin_issues", "constipation", "bloating",
]


def compute_symptom_score(c: dict) -> float:
    total = sum(c.get(k, 0) or 0 for k in SYMPTOM_KEYS)
    return round((total / len(SYMPTOM_KEYS)) * 10) / 10


def compute_risk_score(c: dict) -> float:
    symptom = compute_symptom_score(c)
    meds_penalty = 0 if c.get("meds_taken") else 1.5
    sleep = c.get("sleep_hours") or 0
    sleep_penalty = 1 if sleep < 5 else (0.5 if sleep < 7 else 0)
    score = min(10, symptom + meds_penalty + sleep_penalty)
    return round(score * 10) / 10


def compute_status(risk_score: float) -> str:
    if risk_score < 4:
        return "Normal"
    if risk_score <= 7:
        return "Needs Follow-up"
    return "Escalated"
