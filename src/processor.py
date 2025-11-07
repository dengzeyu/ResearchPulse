"""Process, filter, rank, and deduplicate papers."""
import logging
from typing import List, Dict, Any, Set
from collections import defaultdict
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class PaperProcessor:
    """Processes and ranks papers based on various criteria."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.filters = config.get('filters', {})
        self.min_citations = self.filters.get('min_citations', 5)
        self.exclude_keywords = [kw.lower() for kw in self.filters.get('exclude_keywords', [])]

    def deduplicate(self, papers: List[Any]) -> List[Any]:
        """Remove duplicate papers based on various identifiers."""
        seen_ids = set()
        seen_titles = set()
        unique_papers = []

        for paper in papers:
            # Check by paper ID
            if paper.paper_id in seen_ids:
                continue

            # Check by arXiv ID
            if paper.arxiv_id and paper.arxiv_id in seen_ids:
                continue

            # Check by DOI
            if paper.doi and paper.doi in seen_ids:
                continue

            # Check by normalized title
            normalized_title = self._normalize_title(paper.title)
            if normalized_title in seen_titles:
                continue

            # Add to seen sets
            seen_ids.add(paper.paper_id)
            if paper.arxiv_id:
                seen_ids.add(paper.arxiv_id)
            if paper.doi:
                seen_ids.add(paper.doi)
            seen_titles.add(normalized_title)

            unique_papers.append(paper)

        logger.info(f"Deduplicated {len(papers)} -> {len(unique_papers)} papers")
        return unique_papers

    def filter_papers(self, papers: List[Any]) -> List[Any]:
        """Filter papers based on configured criteria."""
        filtered = []

        for paper in papers:
            # Filter by keywords
            if self._contains_excluded_keywords(paper.title, paper.abstract):
                logger.debug(f"Filtered out (excluded keywords): {paper.title[:50]}")
                continue

            # Filter by citations for older papers
            age_days = (datetime.now() - paper.published_date).days
            if age_days > 7 and paper.citations < self.min_citations:
                logger.debug(f"Filtered out (low citations): {paper.title[:50]}")
                continue

            filtered.append(paper)

        logger.info(f"Filtered {len(papers)} -> {len(filtered)} papers")
        return filtered

    def rank_papers(
        self,
        papers: List[Any],
        social_signals: Dict[str, Dict[str, Any]],
        tracking_config: Dict[str, Any]
    ) -> List[Any]:
        """Rank papers by relevance and social engagement."""

        for paper in papers:
            # Calculate relevance score
            relevance = self._calculate_relevance(paper, tracking_config)
            paper.relevance_score = relevance

            # Get social score
            if paper.paper_id in social_signals:
                paper.social_score = social_signals[paper.paper_id].get('total_score', 0.0)
            else:
                paper.social_score = 0.0

            # Combined score (weighted)
            paper.combined_score = (
                paper.relevance_score * 0.6 +
                paper.social_score * 0.3 +
                (paper.citations / 100.0) * 0.1
            )

        # Sort by combined score
        ranked = sorted(papers, key=lambda p: p.combined_score, reverse=True)

        logger.info(f"Ranked {len(ranked)} papers")
        return ranked

    def _calculate_relevance(self, paper: Any, tracking_config: Dict[str, Any]) -> float:
        """Calculate relevance score based on keyword matching."""
        score = 0.0

        title_lower = paper.title.lower()
        abstract_lower = paper.abstract.lower() if paper.abstract else ""

        # Check keyword matches
        for keyword_group in tracking_config.get('keywords', []):
            terms = keyword_group.get('terms', [])

            for term in terms:
                term_lower = term.lower()

                # Title match (higher weight)
                if term_lower in title_lower:
                    score += 5.0

                # Abstract match
                if term_lower in abstract_lower:
                    score += 2.0

        # Check author matches
        tracked_authors = [a['name'].lower() for a in tracking_config.get('authors', [])]
        for author in paper.authors:
            author_lower = author.lower()
            for tracked_author in tracked_authors:
                if tracked_author in author_lower or author_lower in tracked_author:
                    score += 10.0
                    break

        # Boost recent papers
        age_days = (datetime.now() - paper.published_date).days
        if age_days <= 1:
            score *= 1.5
        elif age_days <= 3:
            score *= 1.3
        elif age_days <= 7:
            score *= 1.1

        return score

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        # Remove special characters, lowercase, remove extra spaces
        normalized = re.sub(r'[^\w\s]', '', title.lower())
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()

    def _contains_excluded_keywords(self, title: str, abstract: str) -> bool:
        """Check if paper contains excluded keywords."""
        text = f"{title} {abstract}".lower()

        for keyword in self.exclude_keywords:
            if keyword in text:
                return True

        return False

    def merge_social_signals(self, papers: List[Any], social_signals: Dict[str, Dict[str, Any]]):
        """Merge social signals into paper objects."""
        for paper in papers:
            if paper.paper_id in social_signals:
                paper.social_signals = social_signals[paper.paper_id]
                paper.social_score = social_signals[paper.paper_id].get('total_score', 0.0)

    def get_top_papers(self, papers: List[Any], limit: int = 50) -> List[Any]:
        """Get top N papers."""
        return papers[:limit]
