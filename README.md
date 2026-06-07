# Fitness & Diet Tracker

A simple Python + Streamlit + SQLite app for tracking daily workouts and diet records.

## Features

- Weight Record Table
- Diet Record Table
- Previous Entries page
- Auto-updating daily date
- SQLite database storage
- Read-only history by default
- Confirmation before enabling edit mode
- Confirmation before saving edited records

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Local access

Open:

```text
http://localhost:8501
```

## Mobile access on same Wi-Fi

Find your Mac IP address and open this on your iPhone:

```text
http://YOUR_MAC_IP:8501
```
