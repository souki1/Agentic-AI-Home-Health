"""
Script to ingest example health documents (guidelines, patient care info) into RAG.
Run from backend/ directory: python scripts/ingest_health_documents.py
Requires: GOOGLE_CLOUD_PROJECT set, database connected, admin user exists.
"""
import sys
from pathlib import Path

# Add parent to path so we can import from backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import SessionLocal
from models import User
from rag.chunking import chunk_by_fixed_size
from rag.config import CHUNK_SIZE, CHUNK_OVERLAP
from rag.embeddings import chunks_to_embeddings
from models import RAGChunk
import requests

HEALTH_DOCUMENTS = [
    {
        "source": "health_guidelines_home_care",
        "title": "Home Health Care Guidelines",
        "text": """
Home Health Care Guidelines

1. Medication Management
   - Take medications exactly as prescribed by your doctor.
   - Never skip doses or double up on missed doses.
   - Store medications in a cool, dry place away from children.
   - Use a pill organizer to track daily medications.
   - Report any side effects or adverse reactions immediately.

2. Vital Signs Monitoring
   - Check blood pressure daily if you have hypertension or heart conditions.
   - Monitor blood glucose levels if you have diabetes (as directed by your doctor).
   - Track your weight weekly and report significant changes (>5 lbs in a week).
   - Measure oxygen saturation (SpO2) if you have respiratory conditions.
   - Normal ranges: BP <120/80, SpO2 >95%, resting heart rate 60-100 bpm.

3. Symptom Tracking
   - Document symptoms daily: pain level (0-10), fatigue, breathlessness, cough, nausea, dizziness.
   - Note when symptoms occur, their severity, and any triggers.
   - Report new or worsening symptoms to your healthcare provider immediately.
   - Red flags requiring immediate medical attention: chest pain, severe shortness of breath, confusion, high fever (>101.3°F).

4. Wound Care
   - Keep wounds clean and dry.
   - Change dressings as instructed by your nurse.
   - Watch for signs of infection: redness, swelling, pus, increased pain, fever.
   - Report any wound changes promptly.

5. Nutrition and Hydration
   - Maintain a balanced diet with adequate protein for healing.
   - Stay hydrated: aim for 6-8 glasses of water daily unless restricted.
   - If appetite is poor, try smaller, more frequent meals.
   - Report significant weight loss or inability to eat/drink.

6. Activity and Mobility
   - Follow your prescribed activity level and exercise plan.
   - Use assistive devices (walker, cane) as recommended.
   - Avoid overexertion; rest when tired.
   - Report falls or balance problems immediately.

7. When to Seek Emergency Care
   - Chest pain or pressure
   - Severe difficulty breathing
   - Signs of stroke (sudden weakness, speech problems, facial drooping)
   - Severe allergic reaction
   - Uncontrolled bleeding
   - Loss of consciousness
   - Severe pain that doesn't respond to medication
""",
    },
    {
        "source": "health_guidelines_chronic_conditions",
        "title": "Managing Chronic Conditions at Home",
        "text": """
Managing Chronic Conditions at Home

Diabetes Management:
- Monitor blood glucose levels as prescribed (typically before meals and at bedtime).
- Maintain a consistent meal schedule and carbohydrate intake.
- Recognize signs of hypoglycemia (low blood sugar): shakiness, sweating, confusion, rapid heartbeat. Treat with 15g fast-acting sugar.
- Recognize signs of hyperglycemia (high blood sugar): excessive thirst, frequent urination, fatigue. Contact your doctor if consistently high.
- Foot care: inspect feet daily for cuts, blisters, or sores. Keep feet clean and dry.

Heart Disease and Hypertension:
- Monitor blood pressure daily and keep a log.
- Take medications at the same time each day.
- Limit sodium intake to <2g per day.
- Recognize warning signs: chest pain, shortness of breath, irregular heartbeat, swelling in legs/feet.
- Follow a heart-healthy diet: fruits, vegetables, whole grains, lean proteins, limit saturated fats.

Chronic Obstructive Pulmonary Disease (COPD):
- Use inhalers and oxygen therapy as prescribed.
- Monitor oxygen saturation levels; use supplemental oxygen if SpO2 drops below 88-90%.
- Practice pursed-lip breathing and diaphragmatic breathing techniques.
- Avoid triggers: smoke, strong odors, dust, cold air.
- Recognize exacerbation signs: increased cough, more sputum, worsening breathlessness, fever. Contact doctor promptly.

Chronic Pain Management:
- Take pain medications as prescribed; don't wait until pain is severe.
- Use non-pharmacological methods: heat/cold therapy, gentle stretching, relaxation techniques.
- Keep a pain diary: location, intensity (0-10), triggers, what helps.
- Report if pain medications are ineffective or if you need more frequent dosing.

Mental Health:
- Maintain social connections and engage in activities you enjoy.
- Practice stress management: deep breathing, meditation, light exercise.
- Recognize signs of depression or anxiety: persistent sadness, loss of interest, excessive worry, sleep problems.
- Don't hesitate to seek professional mental health support.
""",
    },
    {
        "source": "health_guidelines_post_surgery",
        "title": "Post-Surgery Recovery Guidelines",
        "text": """
Post-Surgery Recovery Guidelines

Immediate Post-Op (First 24-48 hours):
- Rest but avoid complete bed rest; move legs and change positions to prevent blood clots.
- Follow dietary restrictions (clear liquids initially, then advance as tolerated).
- Manage pain with prescribed medications; don't let pain get out of control.
- Monitor incision site for signs of infection: redness, swelling, drainage, warmth, increased pain.
- Keep incision clean and dry; follow specific wound care instructions.

First Week:
- Gradually increase activity as tolerated; walking is usually encouraged.
- Avoid heavy lifting (typically >10 lbs) and strenuous activities.
- Take all prescribed medications, including antibiotics if given.
- Monitor for complications: fever >101°F, severe pain, excessive bleeding, signs of infection.
- Follow up with surgeon as scheduled.

Weeks 2-4:
- Continue gradual increase in activity; follow specific restrictions from your surgeon.
- Watch for signs of deep vein thrombosis (DVT): leg swelling, pain, warmth, redness (especially one leg).
- Maintain good nutrition and hydration to support healing.
- Don't drive until cleared by your doctor (often 1-2 weeks, longer if on narcotics).

Long-term Recovery:
- Attend all follow-up appointments.
- Complete any prescribed physical therapy or rehabilitation.
- Report any concerns: persistent pain, wound issues, functional limitations.
- Gradually return to normal activities as approved by your healthcare team.

Warning Signs Requiring Immediate Medical Attention:
- Signs of infection: fever, chills, increasing redness/swelling at incision, pus drainage.
- Signs of blood clot: sudden leg swelling/pain, chest pain, shortness of breath.
- Excessive bleeding that doesn't stop with pressure.
- Severe pain not controlled by medication.
- Signs of allergic reaction to medications.
""",
    },
]


def ingest_documents():
    """Ingest health documents into RAG chunks table."""
    db = SessionLocal()
    try:
        # Check if admin exists (for API calls later)
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("Warning: No admin user found. You may need to create one for API access.")

        total_chunks = 0
        for doc in HEALTH_DOCUMENTS:
            from rag.chunking import chunk_by_fixed_size
            from rag.config import CHUNK_SIZE, CHUNK_OVERLAP

            chunks = chunk_by_fixed_size(
                doc["text"],
                source_id=doc["source"],
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )

            for chunk in chunks:
                existing = db.query(RAGChunk).filter(RAGChunk.id == chunk.id).first()
                if existing:
                    existing.text = chunk.text
                    existing.source = doc["source"]
                    existing.chunk_metadata = chunk.metadata
                else:
                    db_chunk = RAGChunk(
                        id=chunk.id,
                        text=chunk.text,
                        source=doc["source"],
                        chunk_metadata=chunk.metadata,
                    )
                    db.add(db_chunk)
            db.commit()
            total_chunks += len(chunks)
            print(f"✓ Ingested '{doc['source']}': {len(chunks)} chunks")

        print(f"\n✓ Total: {total_chunks} chunks stored in database")
        print("\nNext steps:")
        print("1. Build/update your Vector Search index with these chunks (use embeddings)")
        print("2. Query RAG: POST /rag/query with questions about health guidelines")
        return total_chunks
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Ingesting health documents into RAG...")
    ingest_documents()
