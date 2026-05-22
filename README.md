# AI Events Intelligence Pipeline

A spec-driven system to discover, score, and notify the user of high-value ML/AI events in London and internationally.

## 🚀 Overview

This application automates the discovery of AI-related events. It uses a pipeline architecture to find potential events via search APIs, extracts content from event pages, uses a Large Language Model (Gemma-4) to score the events based on value/interest, and notifies the user via email.

## 🛠 Technical Stack

- **Backend**: Python 3.9 / FastAPI
- **Frontend**: Vue.js + Tailwind CSS (Single Page Application)
- **Database**: SQLite
- **Intelligence**: OpenRouter API (`google/gemma-4-31b-it`)
- **Discovery**: Brave Search API
- **Notifications**: Gmail CLI (`gmcli`)
- **Workflow**: [OpenSpec](https://github.com/Fission-AI/OpenSpec) for spec-driven development

## 📁 Project Structure

```text
├── data/               # SQLite database (events.db)
├── frontend/           # Static Vue.js frontend (index.html)
├── openspec/           # OpenSpec configurations and specifications
├── src/                # Core application logic
│   ├── api.py          # FastAPI backend server
│   ├── db.py           # Database connection and schema logic
│   ├── discovery.py    # Event discovery stage
│   ├── fetcher.py      # Content extraction stage
│   ├── processor.py    # LLM scoring and processing stage
│   ├── notifier.py     # Notification delivery stage
│   └── pipeline.py     # Pipeline orchestrator
├── tests/              # Unit tests for LLM and DB
└── requirements.txt    # Python dependencies
```

## 🏃 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 20.19.0+ (for OpenSpec)
- API Keys for Brave Search and OpenRouter

### Installation
1. **Clone the repository**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

**1. Start the Backend API:**
```bash
cd src
python api.py
```
The API will be available at `http://localhost:8000`.

**2. Launch the Frontend:**
Open `frontend/index.html` in your browser or serve it via:
```bash
cd frontend
python -m http.server 8080
```
Visit `http://localhost:8080`.

### Running the Data Pipeline
To update the event database, run the pipeline stages from the `src` directory:
```bash
cd src
python discovery.py  # Find events
python fetcher.py    # Fetch page content
python processor.py  # Score and categorize
python notifier.py   # Send alerts
```
Alternatively, run `python pipeline.py` to execute the full sequence.

## ⚙️ Configuration
Environment variables or config files are used for API keys:
- `BRAVE_API_KEY`: For event discovery.
- `OPENROUTER_API_KEY`: For event scoring.
- `GMAIL_CONFIG`: Configured via `gmcli`.

## 📝 Development Workflow
This project follows the OpenSpec workflow. To propose changes or implement new features:
```bash
openspec propose "Description of the feature"
openspec apply
```
