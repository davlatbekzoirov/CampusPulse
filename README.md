# CampusPulse

A Django web app for students to track everything happening outside the classroom — club roles, volunteer hours, achievements, and campus events — in one place.

## Features

### Club & Society Role Ledger
Track club memberships and role progression over time (e.g. Member → Secretary → President), with skill tags compiled into a tag cloud showing your most-used soft skills.

### Volunteer Hour Log & Milestone Tracker
Log community service hours with organization, location, and supervisor contact info. Hours are grouped by cause in a doughnut chart, with progress bars toward Bronze (25h), Silver (50h), Gold (100h), and Platinum (200h) milestones.

### Impact Journal
A real-time log of achievements with quantitative impact ("Raised $450, 120+ attendees"), so the details aren't forgotten by the time you write a resume.

### Event & Workshop Calendar
Log club meetings, workshops, and networking events. Each user gets a unique, regenerable iCal feed URL to subscribe in Apple/Google Calendar.

### Dashboard
At-a-glance stats (active clubs, total volunteer hours, total impacts logged), milestone progress, cause breakdown chart, and the next upcoming event with a live countdown.

## Tech Stack

- Python 3.12 / Django
- SQLite (default)
- Chart.js for data visualization
- Vanilla HTML/CSS/JS templates

## Project Structure

```
CampusPulse/
├── accounts/          # User auth
├── core/               # Project settings, root urls
├── extracurricular/    # Clubs, volunteering, impact journal, events
├── templates/
└── manage.py
```

## Setup

```bash
git clone git@github.com:davlatbekzoirov/CampusPulse-.git
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
