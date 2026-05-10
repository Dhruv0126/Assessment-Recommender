import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import ValidationError

from app.models.schemas import ChatRequest, ChatResponse, Recommendation
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.services.retriever import format_retrieved_context, retrieve_assessments
from app.utils.text import detect_missing_slots, is_out_of_scope, normalize_text

load_dotenv()


class SHLAgentService:
    def __init__(self, vector_store) -> None:
        self.vector_store = vector_store
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
        )

    def _conversation_text(self, req: ChatRequest) -> str:
        return "\n".join([f"{m.role}: {normalize_text(m.content)}" for m in req.messages])

    def _last_user_message(self, req: ChatRequest) -> str:
        users = [m.content for m in req.messages if m.role == "user"]
        return users[-1] if users else ""

    def _clarification_response(self, missing: list[str]) -> ChatResponse:
        mapping = {
            "role": "Which role are you hiring for?",
            "seniority": "What is the target experience level (junior/mid/senior)?",
            "assessment_focus": "Do you need coding, aptitude, personality, communication, or a combination?",
        }
        questions = [mapping[m] for m in missing if m in mapping]
        return ChatResponse(
            reply="To recommend the best SHL assessments, I need a bit more detail: " + " ".join(questions),
            recommendations=[],
            end_of_conversation=False,
        )

    def handle_chat(self, req: ChatRequest) -> ChatResponse:
        last_user = self._last_user_message(req)
        conversation_text = self._conversation_text(req)

        if is_out_of_scope(last_user):
            return ChatResponse(
                reply="I can only help with SHL assessment recommendations and comparisons. Share the role and required skills, and I will suggest suitable SHL tests.",
                recommendations=[],
                end_of_conversation=False,
            )

        missing = detect_missing_slots(last_user, conversation_text)
        comparison_intent = any(w in last_user.lower() for w in ["difference", "compare", "vs", "between"])
        if missing and not comparison_intent:
            return self._clarification_response(missing)

        retrieved = retrieve_assessments(self.vector_store, conversation_text, k=10)
        context = format_retrieved_context(retrieved)

        prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{conversation_text}

Retrieved SHL catalog entries:
{context}

Return strict JSON object only. No markdown.
"""
        llm_response = self.llm.invoke(prompt).content

        try:
            parsed = json.loads(llm_response)
            recs = [Recommendation(**r) for r in parsed.get("recommendations", [])]
            return ChatResponse(
                reply=parsed.get("reply", "Here are suitable SHL assessments based on your requirements."),
                recommendations=recs,
                end_of_conversation=bool(parsed.get("end_of_conversation", False)),
            )
        except (json.JSONDecodeError, ValidationError, TypeError):
            fallback_recs = []
            for item in retrieved[:5]:
                try:
                    fallback_recs.append(
                        Recommendation(
                            name=item.get("name", "Unknown"),
                            url=item.get("url", "https://www.shl.com/"),
                            test_type=item.get("test_type", "N/A"),
                            description=item.get("description"),
                            duration=item.get("duration"),
                            category=item.get("category"),
                            skills_measured=item.get("skills_measured", []),
                        )
                    )
                except ValidationError:
                    continue

            return ChatResponse(
                reply="Based on your requirements, here are SHL assessments from the catalog.",
                recommendations=fallback_recs,
                end_of_conversation=False,
            )
