# ResearchPulse Test Suite

Comprehensive unit tests for the ResearchPulse project.

## Test Coverage

### Core Components (tests/unit/)
- **test_paper_model.py** - Tests for the Paper data model
  - Paper creation and initialization
  - Serialization (to_dict)
  - String representation
  - Default values

- **test_processor.py** - Tests for PaperProcessor (business logic)
  - Deduplication (by ID, arXiv ID, DOI, normalized title)
  - Filtering (by keywords, citations, age)
  - Ranking algorithms
  - Relevance scoring
  - Social signal merging

- **test_analyzer.py** - Tests for LLMAnalyzer
  - Multi-provider initialization (Claude, OpenAI, Gemini, Ollama)
  - Paper summarization
  - Contribution extraction
  - Batch processing
  - Error handling

- **test_insights.py** - Tests for InsightsGenerator
  - Research idea generation
  - Hot topic identification
  - Response parsing
  - Multi-provider support

### Fetchers (tests/unit/fetchers/)
- **test_arxiv_fetcher.py** - Tests for ArxivFetcher
  - Keyword search
  - Author search
  - Date filtering
  - Query formatting

- **test_semantic_scholar_fetcher.py** - Tests for SemanticScholarFetcher
  - Keyword search
  - Author search
  - Citation tracking
  - API response handling

- **test_fetcher_coordinator.py** - Tests for FetcherCoordinator
  - Multi-source aggregation
  - Configuration-based fetching
  - Source selection

## Running Tests

### Install Dependencies
```bash
# Install with test dependencies
pip install -e ".[test]"

# Or install all dev dependencies
pip install -e ".[dev]"

# Note: arXiv tests are skipped if arxiv package is not installed
# This is intentional as arxiv has dependency issues on some systems
# To include arXiv tests: pip install -e ".[arxiv,test]"
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Files
```bash
# Run paper model tests
pytest tests/unit/test_paper_model.py -v

# Run processor tests
pytest tests/unit/test_processor.py -v

# Run analyzer tests
pytest tests/unit/test_analyzer.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Tests by Category
```bash
# Run only fetcher tests
pytest tests/unit/fetchers/ -v

# Run only core component tests
pytest tests/unit/test_*.py -v
```

## Test Statistics

Total test count: **86 tests** (2 optional arXiv tests skipped without arxiv package)
- Paper model: 12 tests
- Processor: 24 tests
- Analyzer: 18 tests
- Insights: 18 tests
- ArxivFetcher: ~10 tests (optional, skipped without arxiv package)
- SemanticScholarFetcher: 14 tests
- FetcherCoordinator: ~10 tests (optional, skipped without arxiv package)

## Key Testing Patterns

### Mocking External Dependencies
- API calls are mocked using `unittest.mock` and `responses`
- Time-based tests use `freezegun` for consistent datetime testing
- LLM provider clients are mocked to avoid real API calls

### Fixtures (conftest.py)
- `sample_paper` - Single paper for testing
- `sample_papers` - List of papers for batch testing
- `basic_config` - Standard configuration objects
- `tracking_config` - Tracking configuration for relevance scoring

### Test Organization
- Each test class corresponds to a source class
- Tests are named descriptively: `test_<functionality>_<specific_case>`
- Both happy path and error cases are tested

## CI/CD Integration

These tests are designed to run in CI/CD pipelines without external dependencies:
- No API keys required (all mocked)
- No network calls (mocked with `responses`)
- Deterministic time (using `freezegun`)

## Future Test Additions

Potential areas for expansion:
- Integration tests (tests/integration/)
- End-to-end pipeline tests
- Performance/load tests
- Social media tracker tests
- Static site generator tests
