# Price Intelligence Platform

An AI-powered multi-platform price intelligence system merged from:

- `Price-Tracker`: backend workflow, scraper adapters, API/auth/rate-limit concepts, notification flow, multi-product tracking.
- `price-checker-v2`: modern React + TypeScript + Tailwind interface, compact dashboard UX, component structure, lucide/Radix-style UI primitives.

## Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, Recharts, lucide-react.
- Backend: FastAPI, SQLAlchemy 2, MySQL, Alembic, JWT auth, slowapi rate limiting.
- Scraping: Scrapy + BeautifulSoup parsing.
- ML: pandas, numpy, scikit-learn, joblib.
- ML extensions: XGBoost, Prophet, matplotlib, drift checks, anomaly detection.
- Background processing: Redis, Celery, APScheduler.
- Deployment: Docker Compose, nginx reverse proxy, environment-driven config.

## Quick Start

1. Copy env config:

```bash
cp .env.example .env
```

2. Start MySQL and the API:

```bash
docker compose up --build
```

3. Apply migrations from another terminal:

```bash
docker compose exec backend alembic upgrade head
```

4. Start the frontend locally:

```bash
cd apps/frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Major Integrations

- Consolidated the old public server, notification server, and scraping server into one FastAPI service.
- Replaced local/Electron product storage with MySQL tables for users, products, websites, product links, price history, alerts, ML predictions, and notifications.
- Ported marketplace scraping logic into adapter classes that can be extended per website.
- Added analytics APIs for price summaries, comparisons, trend direction, savings, and dashboard metrics.
- Added ML training and prediction modules for future price, discount authenticity, trend analysis, recommendations, and alert priority.
- Added enterprise SQL migration with categories, brands, preferences, recommendation logs, scraper logs, search history, discount analysis, reviews, trend analysis, competitor prices, purchases, audit logs, and daily analytics.
- Added Celery/Redis background jobs for scraping, retraining, model evaluation, and analytics generation.
- Rebuilt the frontend as an API-driven dashboard with responsive pages for dashboard, search, comparison, analytics, alerts, ML insights, and settings.

## Production Notes
- Set real SMTP and Telegram credentials before enabling live alerts.
- Rotate `JWT_SECRET` and use a managed MySQL instance for deployment.
- Use `scripts/backup_mysql.ps1` for local MySQL backups.
- Use nginx on port `8080` as the production-style API reverse proxy.

## Local MySQL Workbench

If you want to use your existing MySQL Workbench server instead of the Docker MySQL container:

1. Create a database named `price_intelligence`.
2. Set this in `.env`:

```bash
DATABASE_URL=mysql+pymysql://root:pass123@127.0.0.1:3306/price_intelligence
```

3. Use Python 3.10-3.12 for the backend. Python 3.14 is too new for the pinned NumPy/scikit-learn wheels and may try to compile NumPy from source.

On Windows, from `price-intelligence-platform/apps/backend`:

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

If `python` points to Python 3.14, install Python 3.12 or create a conda env:

```powershell
conda create -n price-intel python=3.12
conda activate price-intel
```

Then rerun the commands above.
- Add background workers such as Celery/RQ/APScheduler for high-volume scheduled tracking.
