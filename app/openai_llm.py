from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from langfuse.openai import openai as langfuse_openai

from .incidents import STATE


@dataclass
class LLMUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class LLMResponse:
    text: str
    usage: LLMUsage
    model: str


class OpenAILLM:
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "your-openai-api-key-here":
            print("[WARNING] OpenAI API key not configured. Using fallback mock responses.")
            self.client = None
        else:
            # Use Langfuse-instrumented OpenAI client for automatic tracing
            self.client = langfuse_openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> LLMResponse:
        """Generate a response using OpenAI API or fallback to mock"""
        
        if self.client is None:
            return self._generate_mock_response(prompt)
        
        try:
            # Apply incident scenarios
            if STATE["rag_slow"]:
                time.sleep(2.5)  # Simulate slow RAG retrieval
            
            # Prepare the messages
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Provide concise, accurate responses."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # Apply cost spike scenario by using a more expensive model
            model_to_use = self.model
            if STATE["cost_spike"]:
                model_to_use = "gpt-4" if "gpt-3.5" in self.model else self.model
            
            # Apply tool fail scenario
            if STATE["tool_fail"]:
                raise RuntimeError("Simulated tool failure - OpenAI API error")
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                max_tokens=150,
                temperature=0.7,
                # Langfuse will automatically capture this
            )
            
            # Extract response data
            content = response.choices[0].message.content or "No response generated"
            usage = response.usage
            
            return LLMResponse(
                text=content,
                usage=LLMUsage(
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens
                ),
                model=response.model
            )
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to mock response on error
            return self._generate_mock_response(prompt, error=True)

    def _generate_mock_response(self, prompt: str, error: bool = False) -> LLMResponse:
        """Fallback mock response when OpenAI API is not available"""
        
        if STATE["rag_slow"]:
            time.sleep(2.5)
        
        if STATE["tool_fail"] or error:
            raise RuntimeError("Simulated tool failure - API unavailable")
        
        # Simulate token usage
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = 100
        
        if STATE["cost_spike"]:
            output_tokens *= 4
        
        mock_response = (
            "This is a mock response since OpenAI API key is not configured. "
            "To get real OpenAI responses, please set your OPENAI_API_KEY in the .env file. "
            "The system is working correctly and would use real OpenAI API with proper configuration."
        )
        
        return LLMResponse(
            text=mock_response,
            usage=LLMUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            model=f"{self.model}-mock"
        )


# Factory function to create the appropriate LLM instance
def create_llm(model: str = "gpt-3.5-turbo") -> OpenAILLM:
    """Create an LLM instance with the specified model"""
    return OpenAILLM(model=model)