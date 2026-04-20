from __future__ import annotations

import time
from dataclasses import dataclass

from . import metrics
from .openai_llm import create_llm
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import langfuse_context, observe


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
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        started = time.perf_counter()
        docs = retrieve(message)
        
        # Create a more realistic prompt with retrieved context
        context = "\n".join(docs) if docs else "No relevant context found."
        prompt = f"""Context: {context}

User Question: {message}

Please provide a helpful and accurate response based on the context provided. If the context doesn't contain relevant information, please say so and provide general guidance if appropriate."""

        response = self.llm.generate(prompt)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens, response.model)

        # Update Langfuse context with metadata
        langfuse_context.update_current_span(
            metadata={
                "user_id_hash": hash_user_id(user_id),
                "session_id": session_id,
                "feature": feature,
                "model": response.model,
                "doc_count": len(docs), 
                "query_preview": summarize_text(message),
                "tokens_in": response.usage.input_tokens,
                "tokens_out": response.usage.output_tokens,
                "cost_usd": cost_usd,
                "quality_score": quality_score,
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
        """Estimate cost based on actual OpenAI pricing"""
        
        # OpenAI pricing (as of 2024) - per 1M tokens
        pricing = {
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        }
        
        # Default to gpt-3.5-turbo pricing if model not found
        model_key = "gpt-3.5-turbo"
        for key in pricing.keys():
            if key in model.lower():
                model_key = key
                break
        
        rates = pricing[model_key]
        input_cost = (tokens_in / 1_000_000) * rates["input"]
        output_cost = (tokens_out / 1_000_000) * rates["output"]
        
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        """Improved quality scoring for real responses"""
        score = 0.5
        
        # Bonus for having context
        if docs:
            score += 0.2
        
        # Bonus for reasonable length (not too short, not too long)
        if 50 <= len(answer) <= 500:
            score += 0.1
        elif len(answer) > 20:
            score += 0.05
        
        # Bonus for question relevance (simple keyword matching)
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(question_words.intersection(answer_words))
        if overlap >= 2:
            score += 0.1
        elif overlap >= 1:
            score += 0.05
        
        # Penalty for obvious errors or mock responses
        if any(phrase in answer.lower() for phrase in ["mock response", "api key is not configured", "error"]):
            score -= 0.2
        
        # Penalty for PII leakage
        if "[REDACTED" in answer:
            score -= 0.1
        
        return round(max(0.0, min(1.0, score)), 2)
