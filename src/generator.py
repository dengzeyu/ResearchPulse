"""Static site generator for research blog."""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
import json

logger = logging.getLogger(__name__)


class StaticSiteGenerator:
    """Generates static HTML site from papers and insights."""

    def __init__(self, template_dir: str = 'templates', output_dir: str = 'output'):
        self.template_dir = template_dir
        self.output_dir = output_dir

        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters['datetime'] = self._format_datetime

    def generate_daily_feed(
        self,
        papers: List[Any],
        research_ideas: List[Dict[str, str]],
        hot_topics: List[Dict[str, Any]],
        date: datetime = None
    ) -> str:
        """Generate daily feed page."""

        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y-%m-%d')
        output_path = os.path.join(self.output_dir, date_str)
        os.makedirs(output_path, exist_ok=True)

        # Load template
        template = self.env.get_template('daily_feed.html')

        # Render HTML
        html = template.render(
            date=date,
            papers=papers,
            research_ideas=research_ideas,
            hot_topics=hot_topics,
            total_papers=len(papers)
        )

        # Write to file
        output_file = os.path.join(output_path, 'index.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Generated daily feed: {output_file}")

        # Also update the main index to point to latest
        self._update_main_index(date_str)

        # Save JSON data for API access
        self._save_json_data(papers, research_ideas, hot_topics, output_path)

        return output_file

    def _update_main_index(self, latest_date: str):
        """Update main index.html to redirect to latest date."""
        template = self.env.get_template('index.html')

        html = template.render(
            latest_date=latest_date,
            site_title="ResearchPulse"
        )

        output_file = os.path.join(self.output_dir, 'index.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Updated main index: {output_file}")

    def _save_json_data(
        self,
        papers: List[Any],
        research_ideas: List[Dict[str, str]],
        hot_topics: List[Dict[str, Any]],
        output_path: str
    ):
        """Save data as JSON for programmatic access."""
        data = {
            'papers': [self._paper_to_dict(p) for p in papers],
            'research_ideas': research_ideas,
            'hot_topics': hot_topics,
            'generated_at': datetime.now().isoformat()
        }

        json_file = os.path.join(output_path, 'data.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved JSON data: {json_file}")

    def _paper_to_dict(self, paper: Any) -> Dict[str, Any]:
        """Convert paper object to dictionary for JSON serialization."""
        social_signals = getattr(paper, 'social_signals', {})

        return {
            'title': paper.title,
            'authors': paper.authors,
            'abstract': paper.abstract,
            'url': paper.url,
            'published_date': paper.published_date.isoformat(),
            'source': paper.source,
            'arxiv_id': paper.arxiv_id,
            'doi': paper.doi,
            'citations': paper.citations,
            'venue': paper.venue,
            'pdf_url': paper.pdf_url,
            'summary': paper.summary,
            'contributions': getattr(paper, 'contributions', []),
            'social_score': getattr(paper, 'social_score', 0.0),
            'relevance_score': getattr(paper, 'relevance_score', 0.0),
            'social_signals': social_signals
        }

    def _format_datetime(self, value: datetime, format: str = '%Y-%m-%d') -> str:
        """Jinja2 filter for formatting datetime."""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)

    def copy_static_assets(self):
        """Copy CSS, JS, and other static assets to output directory."""
        static_dir = os.path.join(self.template_dir, 'static')
        output_static = os.path.join(self.output_dir, 'static')

        if os.path.exists(static_dir):
            import shutil
            if os.path.exists(output_static):
                shutil.rmtree(output_static)
            shutil.copytree(static_dir, output_static)
            logger.info(f"Copied static assets to {output_static}")
