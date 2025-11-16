"""
Bulletin generator using Gemini AI
"""
from typing import List, Dict, Optional
from gemini_client.client import GeminiClient
from gemini_client.schemas import BULLETIN_SCHEMA, CLUSTERING_SCHEMA
from gemini_client.prompts import (
    BULLETIN_GENERATOR_SYSTEM,
    create_bulletin_prompt,
    create_clustering_prompt
)


class BulletinGenerator:
    """Generates news bulletins using Gemini AI"""
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize bulletin generator
        
        Args:
            gemini_client: Configured GeminiClient instance
        """
        self.client = gemini_client
    
    def cluster_articles(
        self,
        articles: List[Dict],
        include_thoughts: bool = False
    ) -> Dict:
        """
        Cluster articles by topic and identify duplicates
        
        Args:
            articles: List of article dictionaries
            include_thoughts: Whether to include AI thought process
        
        Returns:
            Clustering result with topics and duplicates
        """
        if not articles:
            return {"clusters": [], "duplicates": []}
        
        # Create clustering prompt
        prompt = create_clustering_prompt(articles)
        
        # Generate structured output
        response = self.client.generate_structured(
            prompt=prompt,
            schema=CLUSTERING_SCHEMA,
            system_instruction=BULLETIN_GENERATOR_SYSTEM,
            include_thoughts=include_thoughts
        )
        
        return response
    
    def generate_bulletin(
        self,
        articles: List[Dict],
        date_vietnamese: str,
        min_stories: int = 3,
        max_stories: int = 7,
        include_thoughts: bool = True
    ) -> Dict:
        """
        Generate complete bulletin from articles
        
        Args:
            articles: List of article dictionaries
            date_vietnamese: Date in Vietnamese format
            min_stories: Minimum number of stories
            max_stories: Maximum number of stories
            include_thoughts: Whether to include AI thought process
        
        Returns:
            Dictionary containing:
                - result: Bulletin data matching BULLETIN_SCHEMA
                - thoughts: AI thought summary (if requested)
                - usage: Token usage information
        """
        if not articles:
            raise ValueError("No articles provided for bulletin generation")
        
        # Create bulletin generation prompt
        prompt = create_bulletin_prompt(
            articles=articles,
            date_vietnamese=date_vietnamese,
            min_stories=min_stories,
            max_stories=max_stories
        )
        
        # Generate structured bulletin
        response = self.client.generate_structured(
            prompt=prompt,
            schema=BULLETIN_SCHEMA,
            system_instruction=BULLETIN_GENERATOR_SYSTEM,
            include_thoughts=include_thoughts
        )
        
        return response
    
    def generate_bulletin_two_stage(
        self,
        articles: List[Dict],
        date_vietnamese: str,
        min_stories: int = 3,
        max_stories: int = 7,
        include_thoughts: bool = True
    ) -> Dict:
        """
        Generate bulletin using two-stage approach:
        1. Cluster and identify important topics
        2. Generate bulletin from clustered topics
        
        Args:
            articles: List of article dictionaries
            date_vietnamese: Date in Vietnamese format
            min_stories: Minimum number of stories
            max_stories: Maximum number of stories
            include_thoughts: Whether to include AI thought process
        
        Returns:
            Dictionary containing bulletin and metadata
        """
        if not articles:
            raise ValueError("No articles provided for bulletin generation")
        
        # Stage 1: Cluster articles
        clustering_response = self.cluster_articles(
            articles=articles,
            include_thoughts=include_thoughts
        )
        
        clustering_result = clustering_response["result"]
        clusters = clustering_result.get("clusters", [])
        
        # Sort clusters by importance
        clusters.sort(key=lambda x: x.get("importance_score", 0), reverse=True)
        
        # Select top clusters
        selected_clusters = clusters[:max_stories]
        
        # Get articles for selected clusters
        selected_article_ids = set()
        for cluster in selected_clusters:
            selected_article_ids.update(cluster.get("article_ids", []))
        
        # Filter articles
        filtered_articles = [
            article for article in articles
            if article.get("id") in selected_article_ids
        ]
        
        # Stage 2: Generate bulletin from filtered articles
        bulletin_response = self.generate_bulletin(
            articles=filtered_articles if filtered_articles else articles,
            date_vietnamese=date_vietnamese,
            min_stories=min_stories,
            max_stories=max_stories,
            include_thoughts=include_thoughts
        )
        
        # Combine results
        return {
            "clustering": clustering_result,
            "clustering_thoughts": clustering_response.get("thoughts"),
            "clustering_usage": clustering_response.get("usage"),
            "bulletin": bulletin_response["result"],
            "bulletin_thoughts": bulletin_response.get("thoughts"),
            "bulletin_usage": bulletin_response.get("usage"),
            "total_usage": {
                "prompt_tokens": (
                    clustering_response.get("usage", {}).get("prompt_token_count", 0) +
                    bulletin_response.get("usage", {}).get("prompt_token_count", 0)
                ),
                "output_tokens": (
                    clustering_response.get("usage", {}).get("candidates_token_count", 0) +
                    bulletin_response.get("usage", {}).get("candidates_token_count", 0)
                ),
                "thinking_tokens": (
                    (clustering_response.get("usage", {}).get("thoughts_token_count") or 0) +
                    (bulletin_response.get("usage", {}).get("thoughts_token_count") or 0)
                )
            }
        }
