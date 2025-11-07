"""Generate research insights and identify hot topics."""
import logging
from typing import Dict, Any, List
from collections import Counter
import os
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
import requests

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """Generates research ideas and identifies hot topics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get('provider', 'claude')
        self.research_ideas_config = config.get('research_ideas', {})
        self.hot_topics_config = config.get('hot_topics', {})

        # Initialize LLM client (same as analyzer)
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

        logger.info(f"Initialized insights generator with provider: {self.provider}")

    def generate_research_ideas(self, papers: List[Any]) -> List[Dict[str, str]]:
        """Generate novel research ideas based on papers."""
        if not papers:
            return []

        # Prepare paper summaries
        paper_summaries = []
        for i, paper in enumerate(papers[:20], 1):  # Top 20 papers
            summary = f"{i}. {paper.title}\n"
            if paper.summary:
                summary += f"   {paper.summary}\n"
            else:
                summary += f"   {paper.abstract[:200]}...\n"
            paper_summaries.append(summary)

        prompt = self.research_ideas_config.get('prompt', '')
        count = self.research_ideas_config.get('count', 5)

        full_prompt = f"""Based on these recent research papers, generate {count} novel research ideas:

{chr(10).join(paper_summaries)}

{prompt}

Format each idea as:
**Idea Title**
Description: 2-3 sentences explaining the idea
Why it matters: 1 sentence on potential impact"""

        try:
            response = self._generate(full_prompt, max_tokens=1500)
            ideas = self._parse_research_ideas(response)
            logger.info(f"Generated {len(ideas)} research ideas")
            return ideas

        except Exception as e:
            logger.error(f"Error generating research ideas: {e}")
            return []

    def identify_hot_topics(self, papers: List[Any]) -> List[Dict[str, Any]]:
        """Identify emerging hot topics from papers."""
        if not papers:
            return []

        # Extract keywords and patterns
        all_keywords = []
        for paper in papers:
            all_keywords.extend(paper.keywords)
            # Simple keyword extraction from title
            words = paper.title.lower().split()
            all_keywords.extend([w for w in words if len(w) > 5])

        # Find most common topics
        keyword_counts = Counter(all_keywords)
        common_keywords = keyword_counts.most_common(20)

        # Prepare paper list for LLM
        paper_list = []
        for i, paper in enumerate(papers[:30], 1):
            paper_list.append(f"{i}. {paper.title}")

        prompt = self.hot_topics_config.get('prompt', '')
        count = self.hot_topics_config.get('count', 3)

        full_prompt = f"""Identify the top {count} emerging trends and hot topics from these research papers:

{chr(10).join(paper_list)}

Common keywords appearing: {', '.join([kw for kw, _ in common_keywords[:15]])}

{prompt}

Format each topic as:
**Topic Name**
Summary: 2-3 sentences explaining the trend
Evidence: Number of papers and key examples"""

        try:
            response = self._generate(full_prompt, max_tokens=1500)
            topics = self._parse_hot_topics(response)
            logger.info(f"Identified {len(topics)} hot topics")
            return topics

        except Exception as e:
            logger.error(f"Error identifying hot topics: {e}")
            return []

    def _generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using configured LLM provider."""
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
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=120
                )
                response.raise_for_status()
                return response.json()['response']

        except Exception as e:
            logger.error(f"Error generating with {self.provider}: {e}")
            return ""

    def _parse_research_ideas(self, response: str) -> List[Dict[str, str]]:
        """Parse research ideas from LLM response."""
        ideas = []
        lines = response.split('\n')

        current_idea = {}
        for line in lines:
            line = line.strip()

            if line.startswith('**') and line.endswith('**'):
                if current_idea:
                    ideas.append(current_idea)
                current_idea = {'title': line.strip('*').strip()}

            elif line.startswith('Description:'):
                current_idea['description'] = line.replace('Description:', '').strip()

            elif line.startswith('Why it matters:'):
                current_idea['impact'] = line.replace('Why it matters:', '').strip()

        if current_idea:
            ideas.append(current_idea)

        return ideas

    def _parse_hot_topics(self, response: str) -> List[Dict[str, Any]]:
        """Parse hot topics from LLM response."""
        topics = []
        lines = response.split('\n')

        current_topic = {}
        for line in lines:
            line = line.strip()

            if line.startswith('**') and line.endswith('**'):
                if current_topic:
                    topics.append(current_topic)
                current_topic = {'name': line.strip('*').strip()}

            elif line.startswith('Summary:'):
                current_topic['summary'] = line.replace('Summary:', '').strip()

            elif line.startswith('Evidence:'):
                current_topic['evidence'] = line.replace('Evidence:', '').strip()

        if current_topic:
            topics.append(current_topic)

        return topics
