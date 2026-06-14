# AI Events Intelligence Pipeline — London AI Radar

A spec-driven system to discover, score, and notify the user of high-value ML/AI events in **London, the surrounding region (Oxbridge, South East), and online**.

## 🚀 Overview

This application automates the discovery of AI-related events in and around London. It uses a pipeline architecture to find potential events via Brave Search and the Eventbrite API, extracts content from event pages, uses a Large Language Model (Gemma-4) to score the events based on value/interest, and notifies the user via email.

## 🛠 Technical Stack

- **Backend**: Python 3.9 / FastAPI
- **Frontend**: Vue.js + Tailwind CSS (Single Page Application)
- **Database**: SQLite
- **Intelligence**: OpenRouter API (`google/gemma-4-31b-it`)
- **Discovery**: Brave Search API + Eventbrite API v3
- **Notifications**: Gmail CLI (`gmcli`)
- **Workflow**: [OpenSpec](https://github.com/Fission-AI/OpenSpec) for spec-driven development

## 📁 Project Structure

```text
├── data/                  # SQLite database (events.db)
├── frontend/              # Static Vue.js frontend (index.html)
├── openspec/              # OpenSpec configurations and specifications
├── src/                   # Core application logic
│   ├── api.py             # FastAPI backend server
│   ├── api_discovery.py   # Eventbrite API discovery module
│   ├── db.py              # Database connection and schema logic
│   ├── deep_discovery.py  # Link extraction and multi-level crawling
│   ├── discovery.py       # Brave Search discovery module
│   ├── discovery_stage.py # Discovery orchestrator (Brave + Eventbrite)
│   ├── fetcher.py         # Content extraction stage
│   ├── processor.py       # LLM scoring and processing stage
│   ├── notifier.py        # Notification delivery stage
│   └── pipeline.py        # Pipeline orchestrator
├── tests/                 # Unit tests for LLM and DB
└── requirements.txt       # Python dependencies
```

## 🏃 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 20.19.0+ (for OpenSpec)
- API Keys for Eventbrite, Brave Search, and OpenRouter

### Installation
1. **Clone the repository**
2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running with Docker (Production)

The recommended way to run the full stack in production is via Docker Compose:

```bash
# Start the API + Frontend (with nginx reverse proxy)
docker compose up -d api frontend

# Run the data pipeline (once, then exits)
docker compose --profile pipeline run --rm pipeline
```

- **Frontend**: `http://localhost:8080` (served via nginx, proxies `/api` to backend)
- **Backend API**: `http://localhost:8082` (or proxied through nginx at `http://localhost:8080/events`, `http://localhost:8080/health`, etc.)
- **Healthcheck**: `http://localhost:8080/health`

### Running Locally (Development)

**1. Start the Backend API:**
```bash
cd src
python api.py
```
The API will be available at `http://localhost:8082`.

**2. Launch the Frontend:**
```bash
cd frontend
python -m http.server 8081
```
Visit `http://localhost:8081`.

The frontend automatically detects the development setup (frontend on `:8081`, API on `:8082`) and routes API calls accordingly. In production behind nginx, it uses the same origin.

### Running the Data Pipeline
To update the event database, run the full pipeline:
```bash
cd src
python pipeline.py
```

Or run stages individually:
```bash
cd src
python discovery_stage.py  # Brave Search + Eventbrite discovery
python fetcher.py          # Fetch page content
python processor.py        # Score and categorize
python notifier.py         # Send alerts
```

## 🌍 Geographical Scope

This pipeline targets:
- **London** — Imperial, UCL, KCL, LSE, Queen Mary, DeepMind London, London meetups
- **Surrounding / Oxbridge** — Oxford, Cambridge, Surrey, Reading, and other South East institutions (within ~100km of London)
- **Online** — Virtual/online AI/ML events with no location barrier

In-person events outside the South East (e.g., Berlin, San Francisco) are excluded unless they have a London mirror venue.

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

### API Keys
| Variable | Description |
|---|---|
| `EVENTBRITE_API_KEY` | Eventbrite API v3 key for structured event discovery |
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM scoring |

### Geo-Filtering
| Variable | Default | Description |
|---|---|---|
| `LONDON_LAT` | `51.5074` | Centre latitude for geo-filtering |
| `LONDON_LNG` | `-0.1278` | Centre longitude for geo-filtering |
| `GEO_RADIUS_KM` | `100` | Search radius in km |

### Discovery
| Variable | Default | Description |
|---|---|---|
| `MAX_QUERIES_PER_RUN` | `5` | Brave Search queries per pipeline run |
| `BRAVE_RESULTS_PER_QUERY` | `15` | Max Brave results per query |
| `BRAVE_DOMAIN_FILTERS` | (see .env.example) | Domains for Brave site: queries |
| `HIGHLY_SOURCED_DOMAINS` | (see .env.example) | Domains eligible for level-2 deep crawling |
| `MAX_DEEP_CRAWL_PER_RUN` | `5` | Sub-pages to deep-crawl per run |
| `MAX_FETCHES_PER_RUN` | `5` | Sources to fetch per run |

### Rate Limiting
| Variable | Default | Description |
|---|---|---|
| `API_CALLS_PER_RUN` | `60` | Max Eventbrite API calls per run |
| `API_DELAY_SECONDS` | `0.5` | Delay between API calls |

## ☁️ Deployment

The app runs on a Hetzner CX22 VPS (€3.99/mo, 2 vCPU, 4GB RAM). Architecture:

```
Cloudflare (DNS only) → Hetzner VPS (nginx on port 443/80) → Docker containers (frontend:8080, api:8082)
```

SSL is handled by Let's Encrypt (auto-renews via certbot). No Caddy in production.

### SSH into the server

```bash
ssh root@167.233.44.167
```

### First-time setup (one-time)

```bash
# Install Docker
apt update && apt install -y docker.io docker-compose-v2

# Clone the repo
cd /opt
git clone https://github.com/claudeio98/the-ai-register.git ai-events-tracker
cd ai-events-tracker

# Create .env with API keys
cat > .env << 'EOF'
DOMAIN=the-ai-register.com
OPENROUTER_API_KEY=<your-openrouter-key>
BRAVE_API_KEY=<your-brave-key>
GMAIL_USER=theairegister@gmail.com
GMAIL_APP_PASSWORD=<your-gmail-app-password>
FEEDBACK_RECIPIENT=theairegister@gmail.com
EOF

# Create data directory
mkdir -p data

# Start all services
docker compose up -d
```

Then set up nginx as a reverse proxy on the host:

```bash
# Install nginx + certbot
apt install -y nginx certbot python3-certbot-nginx

# Configure nginx (see /etc/nginx/sites-enabled/default on the server)
# It proxies requests to the Docker containers

# Get SSL certificate
certbot --nginx -d the-ai-register.com
```

Visit `https://the-ai-register.com`.

### DNS

- **Provider**: Cloudflare (DNS-only, gray cloud — proxy was too slow)
- **Record**: `A` record pointing `the-ai-register.com` to `167.233.44.167`

### Keeping the app updated

```bash
ssh root@167.233.44.167
cd /opt/ai-events-tracker
git pull
docker compose up -d --build
```

### Run the pipeline

```bash
cd /opt/ai-events-tracker
docker compose --profile pipeline run --rm pipeline
```

The pipeline runs automatically at 6am every 3 days via cron (`0 6 */3 * *`).

### Moving to a new server

If migrating to a new server:
1. Copy the entire `/opt/ai-events-tracker/` directory (including `data/events.db`)
2. Install Docker + nginx + certbot
3. Update the DNS A record to the new IP
4. Run `certbot --nginx -d the-ai-register.com`
5. Update the IP in this file

## 📝 Development Workflow

This project follows the OpenSpec workflow. To propose changes or implement new features:

```bash
openspec propose "Description of the feature"
openspec apply
```