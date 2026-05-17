# HireUp — CV-Based Job Recommendation System
**Digital Systems Project (UFCFXK-30-3) | UWE Bristol 2025-26**

## Overview
HireUp is a web-based system that analyses a user's CV and recommends relevant job postings using NLP and cosine similarity matching.

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python server.py
```

Then open `http://127.0.0.1:5000` in your web browser.

## Demo Login
- Username: `demo`  Password: `demo123`

## Project Structure
```
cv_job_recommender/
├── server.py        # Flask Backend & API
├── static/          # HTML, CSS, JS Frontend
├── cv_parser.py     # PDF parsing + skill extraction
├── recommender.py   # TF-IDF similarity engine
├── dataset/
│   └── jobs.csv     # Job listings dataset (25 jobs)
└── requirements.txt
```

## Algorithm
TF-IDF Vectorisation + Cosine Similarity (scikit-learn)
