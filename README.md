# BRApp — Beeston Rylands Archers

A Django web application for managing an archery club's memberships, events, scores, forum, badges and courses.

## Colour Scheme
Black (#111111) and Gold (#E8A800) — taken from the BRA logo.

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000

## Demo Accounts

| Username | Password     | Role              |
|----------|--------------|-------------------|
| admin    | admin123     | Admin (superuser) |
| jsmith   | password123  | Chair             |
| mbrown   | password123  | Treasurer         |
| slee     | password123  | Records Officer   |
| awilson  | password123  | Member            |

## Features

- **Memberships** — Create and manage membership records with levels, start/end dates and pricing
- **Events** — Internal and external events with poll options and attendance tracking
- **Scores** — Log scores by round, bow type and location; auto-marks personal bests
- **Leaderboard** — Filter by round and bow type; shows ranked personal bests
- **Forum** — Member discussion threads with image attachments
- **Badges** — Award badges to members (Records and Admin only)
- **Courses** — Public course listing, non-member application flow, waitlist management
- **Dashboard** — Membership status, upcoming events, check-in reminders, recent badges

## User Roles

| Role          | Access                                       |
|---------------|----------------------------------------------|
| Admin         | Full access including site admin              |
| Chair         | Committee — create events, courses            |
| Treasurer     | Committee — manage memberships                |
| Secretary     | Committee — general committee access          |
| Records       | Committee — manage rounds, award badges       |
| Member        | Standard member — scores, forum, events       |
| Beginners     | Committee — beginner-facing features          |
| Social        | Committee — social event management           |
| Guest         | Minimal access                               |
| Course Guest  | Can view courses; cannot access member areas  |
