# Paper Feed Template

Automated pipeline for tracking research papers and publishing daily reports as GitHub issues.

## Core Structure

```
/
├── src/
│   ├── fetchers/          # Paper source fetchers (arXiv, Google Scholar, Semantic Scholar, PubMed)
│   ├── processor.py       # Filter and process papers
│   ├── formatter.py       # Generate Markdown reports
│   └── publisher.py       # Create GitHub issues
├── config/
│   ├── queries.yaml       # Search queries and keywords
│   └── sources.yaml       # Paper source configurations
├── .github/workflows/
│   └── daily_feed.yml     # Scheduled GitHub Action
└── requirements.txt       # Python dependencies
```

## Paper Sources

- **arXiv**: Preprint server (API: `arxiv`)
- **Google Scholar**: Web scraping via `scholarly` or `serpapi`
- **Semantic Scholar**: Academic search API
- **PubMed**: Biomedical literature (API: `biopython`)

## Key Files

**src/fetchers/base.py**
```python
class PaperFetcher(ABC):
    @abstractmethod
    def fetch(self, query: str, days: int) -> List[Paper]
```

**src/processor.py**
```python
def filter_papers(papers: List[Paper], config: dict) -> List[Paper]
def deduplicate(papers: List[Paper]) -> List[Paper]
```

**src/formatter.py**
```python
def format_report(papers: List[Paper], template: str) -> str
```

**src/publisher.py**
```python
def create_issue(repo: str, title: str, body: str, token: str)
```

**config/queries.yaml**
```yaml
queries:
  - keywords: ["machine learning", "neural networks"]
    sources: ["arxiv", "google_scholar"]
    filters:
      min_citations: 5
```

## Configuration

**Environment Variables:**
- `GITHUB_TOKEN`: GitHub API token
- `SERPAPI_KEY`: Google Scholar API key (if using SerpAPI)
- `SEMANTIC_SCHOLAR_KEY`: Semantic Scholar API key (optional)

## GitHub Action

**.github/workflows/daily_feed.yml**
```yaml
name: Daily Paper Feed
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Setup

1. Fork repository
2. Add secrets: `GITHUB_TOKEN`, `SERPAPI_KEY`
3. Configure `config/queries.yaml`
4. Enable GitHub Actions
5. Run manually or wait for scheduled execution

## Security

- Store API keys in GitHub Secrets
- Use minimal token permissions (`issues: write`)
- Validate external data before processing
