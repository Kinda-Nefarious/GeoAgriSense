# GeoAgriSense

**Don't inspect the whole farm. Know where to look first.**

GeoAgriSense is an AI-assisted crop-scouting application that helps smallholder horticultural farmers and farm managers record crop concerns, interpret field evidence, and decide which areas of a farm should be investigated first.

## Challenge

**Hack for Humanity Harare 2026 - Best Use of the Google Gemini API**

## What the solution does

GeoAgriSense allows a farmer to record a crop observation, add a photograph and context, analyse the evidence with Gemini Flash 3.8, review missing information and next checks, and receive an explainable scouting priority. The system is designed as decision support rather than a definitive crop-diagnosis or treatment system.

## Technology stack

- Python
- Django
- Streamlit
- SQLite
- Google Gemini API
- Gemini Flash 3.8

## How Gemini is used

Gemini performs a specific technical role rather than acting as a general chatbot. The application sends relevant farmer-supplied evidence such as crop type, symptom description, crop context and an optional crop image. Gemini returns a structured assessment that can include visible features, farmer-reported context, possible explanations, missing information, follow-up questions, next checks, a proposed scouting priority and limitations.

The application keeps the farmer's original observation separate from AI interpretation and uses the result as decision support. Gemini can also support evidence-linked explanations of where the farmer should investigate first.

## Project structure

The final repository should contain the actual files used by the application. A typical structure is:

```text
GeoAgriSense/
├── README.md
├── requirements.txt
├── manage.py                  # if used by the Django setup
├── <streamlit_entry_file>.py  # update to the actual Streamlit entry file
├── <django_project>/          # update to the actual Django project/module
├── <app_modules>/
├── data/                      # only if non-sensitive demo data is stored here
└── docs/                      # optional technical documentation
```

Update this tree to match the final repository before submission.

## Installation and local run

### 1. Clone the repository

```bash
git clone <GITHUB_REPOSITORY_URL>
cd <REPOSITORY_FOLDER>
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Store the API key in an environment variable or local secrets configuration. **Do not commit API keys or secrets to GitHub.**

Example environment variable name:

```text
GEMINI_API_KEY=your_key_here
```

### 5. Prepare the Django database

If the final build uses Django migrations:

```bash
python manage.py migrate
```

### 6. Run the application

Run the actual Streamlit entry file used by the project, for example:

```bash
streamlit run app.py
```

If the entry file has a different name, replace `app.py` with the correct file before submission.

## What we tested

The hackathon prototype passed the core workflow tests, including application launch, demo/farm data loading, observation creation, image upload, Gemini Flash 3.8 API integration, AI result display, missing-evidence handling, scouting priority output, SQLite persistence, scouting workflow, follow-up recording and basic AI/error handling.

## Responsible AI

GeoAgriSense is a crop-scouting decision-support prototype. It does not provide a certified diagnosis and does not autonomously prescribe pesticides, fertilisers or treatment dosages. AI-generated outputs may be inaccurate, and farmers remain responsible for decisions. Unobserved areas are not labelled healthy, and nearby observations are not treated as proof of disease spread.

## Team

- **Butho Dube** - Technical Architect / Primary Developer
- **Rufaro Nyakudya** - Product & Agriculture / Demo & Documentation
- **Thembelihle Ndebele** - Product & Agriculture / Demo & Documentation
- **Shaun Jeranyama** - GIS / Data Assistant
- **Tichaona B Wutete** - UI/UX

## Security note

Never commit API keys, passwords, tokens, service-account files or other secrets to the repository.
