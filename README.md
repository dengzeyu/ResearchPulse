# ResearchPulse

[![Tests](https://github.com/dengzeyu/ResearchPulse/actions/workflows/test.yml/badge.svg)](https://github.com/dengzeyu/ResearchPulse/actions/workflows/test.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**AI-powered research paper aggregator that captures the pulse of scientific research.**

ResearchPulse automatically collects papers from multiple sources (arXiv, Google Scholar, PubMed, journals), analyzes them with LLMs (Claude, GPT-4, Gemini, Ollama), tracks social media buzz using free APIs (Reddit, HackerNews, GitHub) plus Google Custom Search for LinkedIn/Twitter content, and generates a beautiful static blog with daily insights, research ideas, and trending topics.

## Features

- 📚 **Multi-source aggregation**: arXiv, Google Scholar, Semantic Scholar, PubMed, Nature, Science
- 🤖 **AI-powered analysis**: Summarization, key contributions, research ideas (5/day), hot topics
- 🌐 **Social media tracking**: Reddit, HackerNews, GitHub + Google Custom Search for LinkedIn/Twitter (100 free queries/day)
- 👥 **Author tracking**: Follow specific researchers and their publications
- 📄 **Citation tracking**: Monitor papers citing influential works
- 🎨 **Static blog generation**: Beautiful, fast, deployable anywhere
- 🐳 **Docker deployment**: Easy setup and scaling

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/dengzeyu/ResearchPulse.git
cd ResearchPulse
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
