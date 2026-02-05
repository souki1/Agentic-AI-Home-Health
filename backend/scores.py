"""Compute symptom/risk scores and status for check-ins (same logic as frontend)."""
import json

from database import CheckIn

SYMPTOM_KEYS = (
    "fatigue", "breathlessness", "cough", "pain", "nausea", "dizziness",
    "swelling", "anxiety", "headache", "chest_tightness", "joint_stiffness",
    "skin_issues", "constipation", "bloating",
)


def _symptom_score(row: CheckIn) -> float:
    n = len(SYMPTOM_KEYS)
    total = sum(getattr(row, k, 0) or 0 for k in SYMPTOM_KEYS)
    return round((total / n) * 10) / 10


def _risk_score(row: CheckIn) -> float:
    s = _symptom_score(row)
    s += 0 if row.meds_taken else 1.5
    h = row.sleep_hours or 0
    s += 1 if h < 5 else (0.5 if h < 7 else 0)
    return min(10.0, round(s * 10) / 10)


def _status(risk: float) -> str:
    if risk < 4:
        return "Normal"
    if risk <= 7:
        return "Needs Follow-up"
    return "Escalated"


def check_in_to_response(row: CheckIn) -> dict:
    devices = None
    if row.devices:
        try:
            devices = json.loads(row.devices)
        except (TypeError, ValueError):
            pass
    risk = _risk_score(row)
    return {
        "id": row.id,
        "patient_id": row.patient_id,
        "date": row.date.isoformat() if hasattr(row.date, "isoformat") else str(row.date),
        "fatigue": row.fatigue or 0,
        "breathlessness": row.breathlessness or 0,
        "cough": row.cough or 0,
        "pain": row.pain or 0,
        "nausea": row.nausea or 0,
        "dizziness": row.dizziness or 0,
        "swelling": row.swelling or 0,
        "anxiety": row.anxiety or 0,
        "headache": row.headache or 0,
        "chest_tightness": row.chest_tightness or 0,
        "joint_stiffness": row.joint_stiffness or 0,
        "skin_issues": row.skin_issues or 0,
        "constipation": row.constipation or 0,
        "bloating": row.bloating or 0,
        "sleep_hours": row.sleep_hours or 0,
        "meds_taken": row.meds_taken if row.meds_taken is not None else True,
        "appetite": row.appetite or "Normal",
        "mobility": row.mobility or "Normal",
        "devices": devices,
        "notes": row.notes,
        "symptom_score": _symptom_score(row),
        "risk_score": risk,
        "status": _status(risk),
    }
