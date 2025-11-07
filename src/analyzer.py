"""LLM-powered paper analyzer supporting multiple providers."""
import os
import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
import requests

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analyzes papers using various LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'claude')
        self.tasks = config.get('tasks', {})

        # Initialize the appropriate client
        if self.provider == 'claude':
            self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.model = config.get('claude', {}).get('model', 'claude-3-5-sonnet-20241022')

        elif self.provider == 'openai':
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.model = config.get('openai', {}).get('model', 'gpt-4-turbo-preview')

        elif self.provider == 'gemini':
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            self.model = config.get('gemini', {}).get('model', 'gemini-pro')

        elif self.provider == 'ollama':
            self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            self.model = config.get('ollama', {}).get('model', 'llama2')

        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

        logger.info(f"Initialized LLM analyzer with provider: {self.provider}")

    def analyze_paper(self, paper: Any) -> Dict[str, Any]:
        """Analyze a single paper."""
        analysis = {}

        try:
            # Summarization
            if self.tasks.get('summarization', True):
                analysis['summary'] = self._summarize_paper(paper)

            # Key contributions
            if self.tasks.get('key_contributions', True):
                analysis['contributions'] = self._extract_contributions(paper)

        except Exception as e:
            logger.error(f"Error analyzing paper '{paper.title}': {e}")

        return analysis

    def _summarize_paper(self, paper: Any) -> str:
        """Generate a concise summary of the paper."""
        prompt = f"""Summarize this research paper in 2-3 sentences for a technical audience.

Title: {paper.title}
Authors: {', '.join(paper.authors[:5])}
Abstract: {paper.abstract[:1000]}

Focus on: What problem does it solve? What's the key innovation? What are the main results?"""

        return self._generate(prompt)

    def _extract_contributions(self, paper: Any) -> List[str]:
        """Extract key contributions from the paper."""
        prompt = f"""List the 3-5 key contributions of this research paper as bullet points.

Title: {paper.title}
Abstract: {paper.abstract[:1000]}

Format each contribution as a single concise bullet point."""

        response = self._generate(prompt)

        # Parse bullet points
        contributions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                contributions.append(line.lstrip('•-* ').strip())

        return contributions[:5]

    def _generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate response using the configured LLM provider."""
        try:
            if self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

            elif self.provider == 'gemini':
                model = genai.GenerativeModel(self.model)
                response = model.generate_content(prompt)
                return response.text

            elif self.provider == 'ollama':
                response = requests.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60
                )
                response.raise_for_status()
                return response.json()['response']

        except Exception as e:
            logger.error(f"Error generating with {self.provider}: {e}")
            return ""

    def batch_analyze(self, papers: List[Any], max_papers: int = 50) -> Dict[str, Dict[str, Any]]:
        """Analyze multiple papers."""
        analyses = {}

        for i, paper in enumerate(papers[:max_papers]):
            logger.info(f"Analyzing paper {i+1}/{min(len(papers), max_papers)}: {paper.title[:50]}...")

            try:
                analysis = self.analyze_paper(paper)
                analyses[paper.paper_id] = analysis

                # Update paper object
                paper.summary = analysis.get('summary')
                paper.contributions = analysis.get('contributions', [])

            except Exception as e:
                logger.error(f"Error analyzing paper {paper.paper_id}: {e}")

        logger.info(f"Completed analysis of {len(analyses)} papers")
        return analyses
