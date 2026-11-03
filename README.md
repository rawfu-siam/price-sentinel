# Price Sentinel 🛡️

![CI](https://github.com/rawfu-siam/price-sentinel/actions/workflows/ci.yml/badge.svg)

> High-Velocity E-Commerce Competitor Monitor & AI Automation Backend

Price Sentinel is an asynchronous competitor monitoring backend built for online businesses and stores. It automates headless browser data collection, validates scraped prices before saving them, caches the latest price in Redis, and exposes a FastAPI service backed by SQLAlchemy 2.0.

---

## 🎯 The Problem

E-commerce brands need to watch competitor pricing regularly, but scrapers are fragile: pages time out, networks drop, and bad data silently pollutes reports. Price Sentinel is built so that failures are retried, bad data is rejected loudly, and every price change is stored as history.

---

## ✨ Features

- **Headless browser scraping** with Playwright (Chromium) for JavaScript-rendered pages
- **Self-healing network calls**: Tenacity retries failed page loads up to 3 times with exponential backoff
- **Bad-data protection**: a missing or unparseable price raises an error instead of saving `0.0` to the database
- **Price history tracking**: every scrape writes a timestamped `PriceHistory` record linked to its `Product`
- **Redis caching**: the latest price per SKU is cached with a 1-hour TTL, and the app degrades gracefully if Redis is offline
- **Startup validation**: required environment variables are checked when the app boots, so a missing key fails fast
- **Rotating logs**: structured logging to console and a rotating `app.log` (50 KB per file, 3 backups)
- **Health endpoint** reporting database and cache status

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI, Uvicorn |
| Database & ORM | SQLite via SQLAlchemy 2.0 (swappable through `DATABASE_URL` with the matching driver) |
| Browser automation | Playwright (headless Chromium) |
| Resilience | Tenacity (exponential backoff) |
| HTML parsing | BeautifulSoup4 |
| Caching | Redis (`redis-py`) |
| Config & validation | Pydantic v2, pydantic-settings |
| Code quality | Ruff (lint + format), Bandit (security scan), pre-commit |
| Testing | pytest, pytest-asyncio |
| DevOps | Docker, Docker Compose, GitHub Actions |

---

## 📂 Project Structure

```text
price-sentinel/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions automated CI pipeline
├── src/
│   ├── __init__.py
│   ├── cache.py            # Redis cache client configuration
│   ├── config.py           # Zero-trust Pydantic settings
│   ├── database.py         # SQLAlchemy engine and session dependency
│   ├── logger.py           # Structured rotation logging setup
│   ├── main.py             # FastAPI app, lifespan, and API endpoints
│   ├── models.py           # SQLAlchemy ORM models (Product & PriceHistory)
│   └── scraper.py          # Playwright & BeautifulSoup scraping engine
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # ORM unit tests & cascade delete verification
│   └── test_scraper.py     # Scraper parsing & exception handling tests
├── .dockerignore
├── .env.example            # Environment variable template
├── .gitignore
├── .pre-commit-config.yaml # Ruff and Bandit hooks before every commit
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Option A: Local

```bash
git clone https://github.com/rawfu-siam/price-sentinel.git
cd price-sentinel
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env             # then edit the values
uvicorn src.main:app --reload
```

Open **http://localhost:8000/docs** to test every endpoint in Swagger UI.

### Option B: Docker (app + Redis)

```bash
docker compose up --build
```

The API is served on port 8000 and Redis starts alongside it. Note that the SQLite file lives inside the container, so data resets when the container is recreated.

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and set:

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | none | SQLAlchemy URL, e.g. `sqlite:///./price_sentinel.db` |
| `TARGET_URL` | Yes | none | Default scraping target |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection string |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

The app refuses to start if a required variable is missing. `.env` is git-ignored and excluded from Docker images, and only `.env.example` is committed.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Database and Redis status (returns 503 if the database is down) |
| `POST` | `/api/v1/scrape` | Scrape a product URL, save the product, record price history, cache the latest price |
| `GET` | `/api/v1/products` | List all tracked products and their current prices |

**Example request**

```bash
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"sku": "WIDGET-001", "url": "https://example.com/products/widget"}'
```

**Example response**

```json
{
  "status": "success",
  "sku": "WIDGET-001",
  "name": "Example Widget",
  "current_price": 29.99,
  "in_stock": true
}
```

Error responses: `502` if the target page cannot be scraped after retries, `500` if the database write fails.

---

## 🧪 Testing & Code Quality

```bash
pytest -v                # run the test suite
ruff check .             # lint
ruff format --check .    # formatting check
```

Enable the pre-commit hooks so Ruff and Bandit run automatically before every commit:

```bash
pre-commit install
```

On every push, GitHub Actions spins up a Redis service, installs dependencies and Chromium, runs Ruff, and executes the full pytest suite.

---

## 🤝 Responsible Scraping

Only point Price Sentinel at sites you have permission to scrape. Respect each site's `robots.txt` and terms of service, and keep request rates polite.

---

## 👤 Author

**Rawfu Siam**: [github.com/rawfu-siam](https://github.com/rawfu-siam)
