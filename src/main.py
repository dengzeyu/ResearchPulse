"""Main entry point for ResearchPulse."""
import os
import sys
import logging
import yaml
from datetime import datetime
from dotenv import load_dotenv
import schedule
import time
import colorlog

from fetchers.coordinator import FetcherCoordinator
from social.coordinator import SocialCoordinator
from analyzer import LLMAnalyzer
from insights import InsightsGenerator
from processor import PaperProcessor
from generator import StaticSiteGenerator


def setup_logging():
    """Setup colored logging."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')

    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))


def load_config(config_file: str):
    """Load YAML configuration file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading config {config_file}: {e}")
        sys.exit(1)


def run_pipeline():
    """Run the complete ResearchPulse pipeline."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Starting ResearchPulse pipeline")
    logger.info("=" * 60)

    try:
        # Load configurations
        logger.info("Loading configurations...")
        tracking_config = load_config('config/tracking.yaml')
        llm_config = load_config('config/llm.yaml')
        social_config = load_config('config/social.yaml')

        # Step 1: Fetch papers
        logger.info("Step 1: Fetching papers from academic sources...")
        fetcher_coordinator = FetcherCoordinator(tracking_config)
        papers = fetcher_coordinator.fetch_all_papers()

        if not papers:
            logger.warning("No papers fetched! Check your API keys and configuration.")
            return

        # Step 2: Process papers (deduplicate, filter)
        logger.info("Step 2: Processing papers (deduplication, filtering)...")
        processor = PaperProcessor(tracking_config)
        papers = processor.deduplicate(papers)
        papers = processor.filter_papers(papers)

        if not papers:
            logger.warning("No papers after filtering!")
            return

        # Step 3: Track social signals
        logger.info("Step 3: Tracking social media signals...")
        social_coordinator = SocialCoordinator(social_config)
        social_signals = social_coordinator.track_all_papers(papers)

        # Merge social signals into papers
        processor.merge_social_signals(papers, social_signals)

        # Step 4: Rank papers
        logger.info("Step 4: Ranking papers by relevance and social engagement...")
        papers = processor.rank_papers(papers, social_signals, tracking_config)

        # Get top papers for analysis
        top_papers = processor.get_top_papers(papers, limit=50)

        # Step 5: Analyze papers with LLM
        logger.info("Step 5: Analyzing papers with LLM...")
        analyzer = LLMAnalyzer(llm_config)
        analyzer.batch_analyze(top_papers, max_papers=30)  # Limit to save costs

        # Step 6: Generate insights
        logger.info("Step 6: Generating research insights...")
        insights_generator = InsightsGenerator(llm_config)
        research_ideas = insights_generator.generate_research_ideas(top_papers)
        hot_topics = insights_generator.identify_hot_topics(top_papers)

        # Step 7: Generate static site
        logger.info("Step 7: Generating static site...")
        generator = StaticSiteGenerator()
        generator.copy_static_assets()
        output_file = generator.generate_daily_feed(
            papers=top_papers,
            research_ideas=research_ideas,
            hot_topics=hot_topics
        )

        logger.info("=" * 60)
        logger.info(f"Pipeline completed successfully!")
        logger.info(f"Output: {output_file}")
        logger.info(f"Total papers: {len(papers)}")
        logger.info(f"Top papers analyzed: {len(top_papers)}")
        logger.info(f"Research ideas: {len(research_ideas)}")
        logger.info(f"Hot topics: {len(hot_topics)}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Setup logging
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("ResearchPulse starting...")

    # Check if running in scheduled mode
    run_once = os.getenv('RUN_ONCE', 'false').lower() == 'true'

    if run_once:
        # Run once and exit
        logger.info("Running in one-shot mode")
        run_pipeline()
    else:
        # Run on schedule
        logger.info("Running in scheduled mode")

        # Run immediately on startup
        run_pipeline()

        # Schedule daily runs at 6 AM
        schedule.every().day.at("06:00").do(run_pipeline)

        logger.info("Scheduler active. Waiting for scheduled runs...")
        logger.info("Daily run scheduled at 06:00")

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == '__main__':
    main()
