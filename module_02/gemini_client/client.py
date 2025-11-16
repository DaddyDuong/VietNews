"""
Gemini API client with structured output support
"""
import time
from typing import Dict, Any, Optional
from google import genai
from google.genai import types


class GeminiClient:
    """Client for interacting with Gemini API with structured outputs"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        fallback_model: Optional[str] = None,
        generation_config: Optional[Dict] = None,
        thinking_config: Optional[Dict] = None,
        max_retries: int = 3,
        retry_delay: int = 2,
        retry_backoff: int = 2
    ):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key
            model: Model name to use
            fallback_model: Fallback model if primary fails
            generation_config: Generation configuration dict
            thinking_config: Thinking configuration dict
            max_retries: Maximum number of retries on failure
            retry_delay: Initial retry delay in seconds
            retry_backoff: Backoff multiplier for retries
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.fallback_model = fallback_model
        self.generation_config = generation_config or {}
        self.thinking_config = thinking_config or {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.current_model = model  # Track which model is currently in use
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_instruction: Optional[str] = None,
        include_thoughts: bool = False
    ) -> Dict[str, Any]:
        """
        Generate structured output matching the provided schema
        
        Args:
            prompt: User prompt
            schema: JSON schema for output structure
            system_instruction: Optional system instruction
            include_thoughts: Whether to include thought summaries
        
        Returns:
            Dictionary containing:
                - result: Parsed JSON result matching schema
                - thoughts: Thought summary (if include_thoughts=True)
                - usage: Token usage metadata
        
        Raises:
            Exception: If generation fails after all retries
        """
        # Build generation config
        config = types.GenerateContentConfig(
            temperature=self.generation_config.get("temperature", 0.7),
            top_p=self.generation_config.get("top_p", 0.95),
            top_k=self.generation_config.get("top_k", 40),
            max_output_tokens=self.generation_config.get("max_output_tokens", 8192),
            response_mime_type="application/json",
            response_schema=schema,
            system_instruction=system_instruction
        )
        
        # Add thinking config if available
        if self.thinking_config:
            thinking_budget = self.thinking_config.get("thinking_budget", -1)
            include_thoughts = include_thoughts or self.thinking_config.get("include_thoughts", False)
            
            config.thinking_config = types.ThinkingConfig(
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts
            )
        
        # Retry logic
        last_exception = None
        delay = self.retry_delay
        
        for attempt in range(self.max_retries):
            try:
                # Generate content
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )
                
                # Extract result
                import json
                
                # Get text from response
                if hasattr(response, 'text') and response.text:
                    result_text = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    # Try to get text from candidates
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        parts_text = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text and not getattr(part, 'thought', False):
                                parts_text.append(part.text)
                        result_text = ''.join(parts_text)
                    else:
                        result_text = None
                else:
                    result_text = None
                
                if not result_text:
                    raise Exception("No text in response")
                
                # Parse JSON (Gemini guarantees valid JSON with structured output)
                result = json.loads(result_text)
                
                # Extract thoughts if requested
                thoughts = None
                if include_thoughts and hasattr(response, 'candidates'):
                    thought_parts = []
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'thought') and part.thought and hasattr(part, 'text'):
                                    thought_parts.append(part.text)
                    if thought_parts:
                        thoughts = "\n".join(thought_parts)
                
                # Extract usage metadata
                usage = {
                    "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "total_token_count": getattr(response.usage_metadata, 'total_token_count', 0),
                }
                
                if hasattr(response.usage_metadata, 'thoughts_token_count'):
                    usage["thoughts_token_count"] = response.usage_metadata.thoughts_token_count
                
                return {
                    "result": result,
                    "thoughts": thoughts,
                    "usage": usage
                }
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    time.sleep(delay)
                    delay *= self.retry_backoff
                else:
                    # If all retries failed and we have a fallback model, try it
                    if self.fallback_model and self.current_model != self.fallback_model:
                        print(f"\n⚠ {self.model} failed after {self.max_retries} attempts.")
                        print(f"  Switching to fallback model: {self.fallback_model}")
                        print(f"  Disabling thinking mode for stability...")
                        print(f"  Error: {str(e)}\n")
                        
                        # Switch to fallback model
                        self.current_model = self.fallback_model
                        
                        # Build config without thinking mode
                        fallback_config = types.GenerateContentConfig(
                            temperature=self.generation_config.get("temperature", 0.7),
                            top_p=self.generation_config.get("top_p", 0.95),
                            top_k=self.generation_config.get("top_k", 40),
                            max_output_tokens=self.generation_config.get("max_output_tokens", 8192),
                            response_mime_type="application/json",
                            response_schema=schema,
                            system_instruction=system_instruction
                        )
                        # Note: No thinking config for fallback
                        
                        # Retry with fallback model (reset retry counter)
                        for fallback_attempt in range(self.max_retries):
                            try:
                                response = self.client.models.generate_content(
                                    model=self.fallback_model,
                                    contents=prompt,
                                    config=fallback_config
                                )
                                
                                # Same extraction logic
                                import json
                                
                                if hasattr(response, 'text') and response.text:
                                    result_text = response.text
                                elif hasattr(response, 'candidates') and response.candidates:
                                    candidate = response.candidates[0]
                                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                        parts_text = []
                                        for part in candidate.content.parts:
                                            if hasattr(part, 'text') and part.text and not getattr(part, 'thought', False):
                                                parts_text.append(part.text)
                                        result_text = ''.join(parts_text)
                                    else:
                                        result_text = None
                                else:
                                    result_text = None
                                
                                if not result_text:
                                    raise Exception("No text in response")
                                
                                result = json.loads(result_text)
                                
                                # Extract thoughts if requested
                                thoughts = None
                                if include_thoughts and hasattr(response, 'candidates'):
                                    thought_parts = []
                                    for candidate in response.candidates:
                                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                            for part in candidate.content.parts:
                                                if hasattr(part, 'thought') and part.thought and hasattr(part, 'text'):
                                                    thought_parts.append(part.text)
                                    if thought_parts:
                                        thoughts = "\n".join(thought_parts)
                                
                                usage = {
                                    "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', 0),
                                    "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', 0),
                                    "total_token_count": getattr(response.usage_metadata, 'total_token_count', 0),
                                }
                                
                                if hasattr(response.usage_metadata, 'thoughts_token_count'):
                                    usage["thoughts_token_count"] = response.usage_metadata.thoughts_token_count
                                
                                print(f"✓ Fallback successful with {self.fallback_model}\n")
                                return {
                                    "result": result,
                                    "thoughts": thoughts,
                                    "usage": usage
                                }
                                
                            except Exception as fallback_error:
                                if fallback_attempt < self.max_retries - 1:
                                    time.sleep(delay)
                                else:
                                    raise Exception(
                                        f"Both {self.model} and {self.fallback_model} failed. "
                                        f"Primary error: {str(e)}, Fallback error: {str(fallback_error)}"
                                    ) from fallback_error
                    else:
                        raise Exception(
                            f"Failed to generate content after {self.max_retries} attempts. "
                            f"Last error: {str(e)}"
                        ) from e
        
        # This should never be reached, but just in case
        raise last_exception
    
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        use_thinking: bool = False
    ) -> Dict[str, Any]:
        """
        Generate plain text response (non-structured)
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            use_thinking: Whether to enable thinking mode
        
        Returns:
            Dictionary containing:
                - result: Generated text
                - thoughts: Thought summary (if use_thinking=True)
                - usage: Token usage metadata
        """
        # Build generation config
        config = types.GenerateContentConfig(
            temperature=self.generation_config.get("temperature", 0.7),
            top_p=self.generation_config.get("top_p", 0.95),
            top_k=self.generation_config.get("top_k", 40),
            max_output_tokens=self.generation_config.get("max_output_tokens", 8192),
            system_instruction=system_instruction
        )
        
        # Add thinking config if requested
        if use_thinking and self.thinking_config:
            thinking_budget = self.thinking_config.get("thinking_budget", -1)
            include_thoughts = self.thinking_config.get("include_thoughts", False)
            
            config.thinking_config = types.ThinkingConfig(
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts
            )
        
        # Generate
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        
        # Extract thoughts if available
        thoughts = None
        if use_thinking and hasattr(response, 'candidates'):
            thought_parts = []
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'thought') and part.thought and hasattr(part, 'text'):
                            thought_parts.append(part.text)
            if thought_parts:
                thoughts = "\n".join(thought_parts)
        
        # Extract usage
        usage = {
            "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', 0),
            "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', 0),
            "total_token_count": getattr(response.usage_metadata, 'total_token_count', 0),
        }
        
        if hasattr(response.usage_metadata, 'thoughts_token_count'):
            usage["thoughts_token_count"] = response.usage_metadata.thoughts_token_count
        
        return {
            "result": response.text,
            "thoughts": thoughts,
            "usage": usage
        }
