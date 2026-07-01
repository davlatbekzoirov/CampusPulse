# CampusPulse

A modern Django web application designed for students to catalog, analyze, and showcase everything happening outside the classroom. From managing club leadership lifecycles and tracking community service milestones to instantly generating optimized resume bullets, CampusPulse turns daily campus involvement into a strategic portfolio.

## Features

### 📋 Club & Society Role Ledger
Track memberships and active executive role progression over time (e.g., *Member → Secretary → President*). The system parses your involvements to compile a personal skill tag cloud highlighting your top administrative and soft-skill competencies.

### ⏱️ Volunteer Hour Log & Milestone Tracker
Log service hours complete with organization data, location mapping, and supervisor verification fields. Includes a dynamic progress engine that visualizes your path toward certified student tiers: **Bronze (25h)**, **Silver (50h)**, **Gold (100h)**, and **Platinum (200h)**.

### 📝 Impact Journal & Google X-Y-Z Resume Generator
Log achievements alongside quantitative metrics ("*Raised $450, 120+ attendees*") to ensure critical data points are never forgotten. The built-in **Resume Generator** automatically transforms raw journal entries into high-impact bullet points styled using the Google-recommended X-Y-Z formula (*Accomplished [X] as measured by [Y], by doing [Z]*).

### 📊 Growth Analytics & Industry "Gaps" Finder
An advanced diagnostic dashboard that audits your leadership vs. membership ratios. It evaluates your registered skill logs against standard recruitment profiles (e.g., *Management, Tech, Non-profit*) to instantly surface exact skill gaps you need to fill.

### 🌐 Shareable Public Portfolios
Provides an optional public-facing directory profile with built-in access controls. Securely showcase verified hours, top skills, leadership roles, and impact achievements to college admissions panels or professional recruiters through a static, shareable URL.

### 📅 iCal Calendar Sync & Live Countdown
Track upcoming club meetings, events, and workshops. The dashboard features a live JavaScript countdown timer for your next commitment, alongside a unique, regenerable iCal feed token to sync your campus schedule directly with Google Calendar or Apple Calendar.

---

## Tech Stack

* **Backend:** Python 3.12 / Django Web Framework
* **Database:** SQLite (Development default)
* **Frontend UI:** Vanilla HTML5 / Custom CSS3 Grid Architecture (Dark/Slate Palette)
* **Data Visualization:** Chart.js (via CDN)
* **Calendar Integration:** iCal / django-ical architecture

---

## Project Structure

```text
CampusPulse/
├── accounts/           # User authentication & user session state
├── core/               # Root settings, core asset pipelines, deployment routing
├── extracurricular/    # Core engines: Clubs, volunteering, impact logs, and analytics
├── templates/          # Global layout extensions and tailored feature views
│   └── extracurricular/
│       ├── base.html              # Core layout shell & slate style utilities
│       ├── dashboard.html         # Live overview workspace & charts
│       ├── impact_list.html       # Journal feed with developer action hooks
│       ├── resume_generator.html  # Google X-Y-Z formatting utility
│       ├── analytics_insights.html# Industry gap matrices and charts
│       └── public_portfolio.html  # Unauthenticated public showcase profiles
└── manage.py

## Setup

```bash
git clone git@github.com:davlatbekzoirov/CampusPulse.git
cd CampusPulse

python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_extracurricular   # optional: default skills & volunteer causes
python manage.py createsuperuser

python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

## Management Commands

| Command | Description |
|---|---|
| `seed_extracurricular` | Seeds default skill tags (Public Speaking, Budgeting, etc.) and volunteer causes (Environment, Animal Shelter, etc.) |

## Calendar Feed

Each user has a private iCal feed at:

```
/events/feed/<token>.ics
```

The token can be regenerated from the Events page, which invalidates the previous URL.

## License

Private project — all rights reserved.
