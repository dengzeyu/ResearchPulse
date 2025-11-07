# ResearchPulse

**AI-powered research paper aggregator that captures the pulse of scientific research.**

ResearchPulse automatically collects papers from multiple sources (arXiv, Google Scholar, PubMed, journals), analyzes them with LLMs (Claude, GPT-4, Gemini, Ollama), tracks social media buzz (Twitter, LinkedIn, WeChat, Reddit), and generates a beautiful static blog with daily insights, research ideas, and trending topics.

## Features

- 📚 **Multi-source aggregation**: arXiv, Google Scholar, Semantic Scholar, PubMed, Nature, Science
- 🤖 **AI-powered analysis**: Summarization, key contributions, research ideas (5/day), hot topics
- 🌐 **Social media tracking**: Reddit, HackerNews, GitHub trending (all free APIs)
- 👥 **Author tracking**: Follow specific researchers and their publications
- 📄 **Citation tracking**: Monitor papers citing influential works
- 🎨 **Static blog generation**: Beautiful, fast, deployable anywhere
- 🐳 **Docker deployment**: Easy setup and scaling

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd research-pulse
cp .env.example .env
# Edit .env with your API keys

# 2. Configure tracking
# Edit config/tracking.yaml with your research interests

# 3. Run with Docker
docker-compose up -d

# 4. View your feed
open http://localhost:8080
```

See `Claude.md` for detailed documentation.
