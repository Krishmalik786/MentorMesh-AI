# MentorMesh AI

A mentorship copilot for startups. A founder submits 4 links — GitHub repo,
website, pitch deck, social media — and gets a profile built from what's
actually in them, then a chat interface staffed by specialist mentor agents
who ground every claim in that evidence instead of giving generic advice.

## Architecture

```
Founder's 4 links
      ↓
Ingestion (4 independent fetchers, run in parallel)
  - GitHub API            - PDF text extraction (pitch deck)
  - Website scraping,     - Open Graph metadata (social)
    with a headless-
    browser fallback for
    JS-rendered pages
      ↓
Synthesis graph (LangGraph)
  synthesize (LLM) → assemble (code) → validate (code) → retry if ungrounded
      ↓
StartupProfile  (schema-defined, every claim tied to an evidence entry)
      ↓
Mentorship graph (LangGraph, multi-agent)
  coordinator → specialist mentor(s) [technical / product / pitch / growth]
             → synthesizer → grounding check → reply
```

Every fetcher, and every AI step, is built to fail honestly rather than
guess: unreachable sources are reported as unreachable, and every claim the
mentor makes has to trace back to something a fetcher actually found.

## Stack

- **Ingestion:** `requests`, `BeautifulSoup`, `trafilatura`, Playwright (headless-browser fallback), `pypdf`
- **AI orchestration:** LangGraph, LangChain, OpenRouter (provider-agnostic LLM access)
- **Backend:** FastAPI — async profile building with live status polling, no job queue needed at this scale
- **Frontend:** Streamlit

## Running it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # then add your OPENROUTER_API_KEY

# terminal 1
uvicorn src.api.main:app --reload

# terminal 2
streamlit run app.py
```

Or skip the wait on your first run — generate a fully-populated mock
profile and load it straight from the UI:

```bash
python -m src.mock_data
```

## Project structure

```
src/
  profile_schema.py     Phase 0 — the StartupProfile schema
  ingestion/             Phase 1 — the 4 fetchers, one file each
  synthesis/             Phase 2 — LangGraph graph: raw data -> StartupProfile
  mentorship/            Phase 3 — LangGraph graph: question -> grounded reply
  api/                   Phase 4 — FastAPI backend
  pipeline.py            ties ingestion + synthesis together end-to-end
app.py                   Phase 5 — Streamlit frontend
docs/mentorship_spec.md  what "good mentorship" means, concretely
```
