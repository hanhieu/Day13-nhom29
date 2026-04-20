from __future__ import annotations

import time
from dataclasses import dataclass

from . import metrics
from .openai_llm import create_llm
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import (
    get_current_observation_id,
    get_current_trace_id,
    langfuse_context,
    observe,
    propagate_attributes,
    trace_id_from_correlation_id,
)


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model
        self.llm = create_llm(model=model)

    @observe()
    def run(
        self,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
        correlation_id: str = "",
        langfuse_trace_id: str | None = None,
    ) -> AgentResult:
        # Reserved kwarg used by @observe() to set custom trace IDs.
        _ = langfuse_trace_id

        user_id_hash = hash_user_id(user_id)

        with propagate_attributes(session_id=session_id, user_id=user_id_hash):
            langfuse_context.update_current_trace(
                name=correlation_id or "chat-request",
                session_id=session_id,
                user_id=user_id_hash,
                tags=[feature, self.model],
                metadata={"correlation_id": correlation_id},
            )

            started = time.perf_counter()
            docs = retrieve(message)
            context = "\n".join(docs) if docs else "No relevant context found."
            prompt = (
                f"Context: {context}\n\n"
                f"User Question: {message}\n\n"
                "Please provide a helpful and accurate response based on the context provided. "
                "If the context doesn't contain relevant information, please say so and provide general guidance if appropriate."
            )
            current_trace_id = get_current_trace_id() or trace_id_from_correlation_id(correlation_id)
            current_observation_id = get_current_observation_id()
            response = self.llm.generate(
                prompt,
                correlation_id=correlation_id,
                session_id=session_id,
                user_id=user_id_hash,
                feature=feature,
                trace_id=current_trace_id,
                parent_observation_id=current_observation_id,
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
            cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens, response.model)
            quality_score = self._heuristic_quality(message, response.text, docs)

            langfuse_context.update_current_span(
                metadata={
                    "correlation_id": correlation_id,
                    "user_id_hash": user_id_hash,
                    "doc_count": len(docs),
                    "query_preview": summarize_text(message),
                    "tokens_in": response.usage.input_tokens,
                    "tokens_out": response.usage.output_tokens,
                    "cost_usd": cost_usd,
                },
            )

            metrics.record_request(
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                quality_score=quality_score,
            )

            return AgentResult(
                answer=response.text,
                latency_ms=latency_ms,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                cost_usd=cost_usd,
                quality_score=quality_score,
            )

    def _estimate_cost(self, tokens_in: int, tokens_out: int, model: str) -> float:
        pricing = {
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        }
        model_key = next((k for k in pricing if k in model.lower()), "gpt-3.5-turbo")
        rates = pricing[model_key]
        return round(
            (tokens_in / 1_000_000) * rates["input"] + (tokens_out / 1_000_000) * rates["output"],
            6,
        )

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if 50 <= len(answer) <= 500:
            score += 0.1
        elif len(answer) > 20:
            score += 0.05
        overlap = len(set(question.lower().split()) & set(answer.lower().split()))
        if overlap >= 2:
            score += 0.1
        elif overlap >= 1:
            score += 0.05
        if any(p in answer.lower() for p in ["mock response", "api key is not configured", "error"]):
            score -= 0.2
        if "[REDACTED" in answer:
            score -= 0.1
        return round(max(0.0, min(1.0, score)), 2)
