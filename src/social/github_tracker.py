"""GitHub tracker for paper implementations."""
from github import Github
import os
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class GitHubTracker:
    """Track paper implementations on GitHub."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.min_stars = config.get('min_stars', 100)

        if self.enabled:
            token = os.getenv('GITHUB_TOKEN')
            try:
                self.github = Github(token) if token else Github()
            except Exception as e:
                logger.error(f"Failed to initialize GitHub client: {e}")
                self.enabled = False

    def track_papers(self, papers: List[Any]) -> Dict[str, Dict[str, Any]]:
        """Track implementations for papers on GitHub."""
        if not self.enabled:
            return {}

        social_signals = {}

        for paper in papers:
            if not paper.arxiv_id:
                continue

            try:
                # Search for repositories mentioning the paper
                query = f"arxiv {paper.arxiv_id}"
                repos = self.github.search_repositories(query=query, sort='stars')

                repo_list = []
                for repo in repos[:5]:  # Top 5 repos
                    if repo.stargazers_count < self.min_stars:
                        continue

                    repo_list.append({
                        'name': repo.full_name,
                        'url': repo.html_url,
                        'stars': repo.stargazers_count,
                        'description': repo.description
                    })

                if repo_list:
                    social_signals[paper.paper_id] = {
                        'github': {
                            'implementations': repo_list,
                            'total_stars': sum(r['stars'] for r in repo_list)
                        }
                    }

            except Exception as e:
                logger.warning(f"Error tracking GitHub for paper {paper.arxiv_id}: {e}")

        logger.info(f"Tracked {len(social_signals)} papers on GitHub")
        return social_signals

    def get_trending_repos(self) -> List[Dict[str, Any]]:
        """Get trending ML repositories that might reference papers."""
        if not self.enabled:
            return []

        repos = []
        topics = self.config.get('topics', ['machine-learning'])

        for topic in topics:
            try:
                query = f"topic:{topic} stars:>100"
                results = self.github.search_repositories(
                    query=query,
                    sort='updated',
                    order='desc'
                )

                arxiv_pattern = re.compile(r'arxiv\.org/abs/(\d+\.\d+)')

                for repo in results[:20]:  # Top 20 per topic
                    readme_text = ""
                    try:
                        readme = repo.get_readme()
                        readme_text = readme.decoded_content.decode('utf-8')
                    except:
                        pass

                    text = f"{repo.description} {readme_text}"
                    arxiv_match = arxiv_pattern.search(text)

                    if arxiv_match or any(kw in text.lower() for kw in ['paper', 'research', 'arxiv']):
                        repos.append({
                            'name': repo.full_name,
                            'url': repo.html_url,
                            'stars': repo.stargazers_count,
                            'description': repo.description,
                            'arxiv_id': arxiv_match.group(1) if arxiv_match else None,
                            'topic': topic
                        })

            except Exception as e:
                logger.error(f"Error fetching trending repos for {topic}: {e}")

        logger.info(f"Found {len(repos)} trending GitHub repos")
        return repos
