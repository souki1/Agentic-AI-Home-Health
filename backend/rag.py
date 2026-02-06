"""RAG chat implementation: Ollama (local) and Vertex AI (cloud)."""
from typing import List, Optional

import httpx

from config import settings
from database import CheckIn, Conversation, Patient, DbSession
from database import ChatMessage as ChatMessageModel
from embeddings import get_embedding


class RAGChat:
    """RAG chat handler that uses Ollama locally or Vertex AI in cloud."""
    
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        if self.provider == "vertex":
            self._init_vertex()
        elif self.provider == "ollama":
            self._init_ollama()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _init_ollama(self):
        """Ollama: use HTTP API (no ollama package to avoid httpx conflict)."""
        self.ollama_base_url = settings.ollama_base_url.rstrip("/")
        self.ollama_model = settings.ollama_model
    
    def _init_vertex(self):
        """Initialize Vertex AI client."""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            if not settings.google_cloud_project:
                raise ValueError("GOOGLE_CLOUD_PROJECT must be set for Vertex AI")
            
            vertexai.init(project=settings.google_cloud_project, location=settings.google_cloud_location)
            self.model = GenerativeModel(settings.vertex_model)
        except ImportError:
            raise ImportError("google-cloud-aiplatform not installed. Run: pip install google-cloud-aiplatform")
    
    def _retrieve_context(self, query: str, user_id: str, db: DbSession) -> str:
        """Retrieve relevant context from patient check-ins, notes, and past chat (vector search)."""
        context_parts = []

        # Patient info and check-ins
        patient = db.query(Patient).filter(Patient.id == user_id).first()
        if patient:
            context_parts.append(f"Patient: {patient.name}, Age: {patient.age}, Condition: {patient.condition}")
            check_ins = db.query(CheckIn).filter(CheckIn.patient_id == user_id).order_by(CheckIn.date.desc()).limit(10).all()
            for ci in check_ins:
                symptoms = []
                if ci.fatigue > 0:
                    symptoms.append(f"fatigue ({ci.fatigue:.1f})")
                if ci.breathlessness > 0:
                    symptoms.append(f"breathlessness ({ci.breathlessness:.1f})")
                if ci.cough > 0:
                    symptoms.append(f"cough ({ci.cough:.1f})")
                if ci.pain > 0:
                    symptoms.append(f"pain ({ci.pain:.1f})")
                if ci.notes:
                    symptoms.append(f"notes: {ci.notes}")
                if symptoms:
                    date_str = ci.date.strftime("%Y-%m-%d") if ci.date else "unknown"
                    context_parts.append(f"Check-in {date_str}: {', '.join(symptoms)}")

        # Vector search over past chat messages (when embeddings available)
        query_embedding = get_embedding(query)
        if query_embedding:
            limit = getattr(settings, "chat_vector_search_limit", 5) or 5
            try:
                nearest = (
                    db.query(ChatMessageModel)
                    .join(Conversation, Conversation.id == ChatMessageModel.conversation_id)
                    .filter(Conversation.user_id == user_id)
                    .filter(ChatMessageModel.embedding.isnot(None))
                    .order_by(ChatMessageModel.embedding.cosine_distance(query_embedding))
                    .limit(limit)
                    .all()
                )
            except Exception:
                nearest = []
            for msg in nearest:
                context_parts.append(f"Past chat ({msg.role}): {msg.content[:500]}{'...' if len(msg.content or '') > 500 else ''}")

        return "\n".join(context_parts) if context_parts else "No recent check-in or chat data available."
    
    def chat(self, query: str, user_id: str, db: DbSession, conversation_history: Optional[List[dict]] = None) -> str:
        """Generate RAG response using retrieved context."""
        context = self._retrieve_context(query, user_id, db)
        
        system_prompt = """You are a helpful health assistant. Answer questions based on the patient's health data provided in the context.
Be empathetic, clear, and professional. If the context doesn't contain relevant information, say so politely.
Do not make medical diagnoses or provide treatment advice beyond general wellness guidance."""
        
        if self.provider == "ollama":
            return self._chat_ollama(query, context, system_prompt, conversation_history)
        else:
            return self._chat_vertex(query, context, system_prompt, conversation_history)
    
    def _chat_ollama(self, query: str, context: str, system_prompt: str, history: Optional[List[dict]]) -> str:
        """Chat using Ollama HTTP API."""
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history[-5:])  # Last 5 messages for context
        
        messages.append({
            "role": "user",
            "content": f"Context about patient's health:\n{context}\n\nUser question: {query}"
        })
        
        url = f"{self.ollama_base_url}/api/chat"
        payload = {"model": self.ollama_model, "messages": messages}
        
        try:
            with httpx.Client(timeout=120.0) as client:
                r = client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
                return data.get("message", {}).get("content", "No response.")
        except Exception as e:
            return f"Error calling Ollama: {str(e)}. Make sure Ollama is running at {settings.ollama_base_url}"
    
    def _chat_vertex(self, query: str, context: str, system_prompt: str, history: Optional[List[dict]]) -> str:
        """Chat using Vertex AI Gemini."""
        prompt_parts = [f"{system_prompt}\n\nContext:\n{context}\n\nUser: {query}\n\nAssistant:"]
        
        try:
            response = self.model.generate_content(prompt_parts)
            return response.text if response.text else "No response generated."
        except Exception as e:
            return f"Error calling Vertex AI: {str(e)}"


def get_rag_chat() -> RAGChat:
    """Get or create RAG chat instance."""
    if not hasattr(get_rag_chat, "_instance"):
        get_rag_chat._instance = RAGChat()
    return get_rag_chat._instance
