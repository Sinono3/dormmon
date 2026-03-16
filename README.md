# Dormmon

A smart dormitory management system for shared living spaces. Dormmon uses facial recognition to identify roommates and provides an intuitive interface for tracking chores, splitting expenses, and managing shared finances — available as both a web dashboard and a native desktop app.

> Built as a university project for a shared dorm of four people, running on a Raspberry Pi.

---

<!-- ## Screenshots -->

<!-- > *(Add screenshots here)* -->

## Features

### Face Recognition Login
Roommates are identified automatically via webcam using real-time facial recognition. No passwords needed — just look at the camera.

### Chore Tracking
Log trash disposal and room cleaning events with timestamps and optional photos. See at a glance who last took out the trash and how long ago.

### Automated Cleaning Schedule
A 6-week rotating cleaning schedule automatically assigns duties to each roommate. The system tracks statuses (Pending, Late, Completed) and advances the rotation when a task is marked done.

### Expense Splitting
Record shared purchases and split costs equally among selected roommates. Every transaction is saved to a ledger for full auditability.

### Financial Balances
View a clear summary of who owes whom. Record direct payments to settle up. Balances update in real time as expenses are logged.

### Inventory Tracking
Monitor shared household items (e.g. toilet paper) and log stock levels over time.

### Dual Interface
- **Web dashboard** — Admin-friendly interface for managing users, categories, events, and schedules
- **Desktop app** — Touch-friendly Tkinter UI designed for a mounted display, with live weather and a dark mode

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | [Flask](https://flask.palletsprojects.com/) 3.1.2 |
| ORM / Database | [Peewee](http://docs.peewee-orm.com/) 3.18.3 + SQLite |
| Face Recognition | [face-recognition](https://github.com/ageitgey/face_recognition) 1.3.0 |
| Computer Vision | [OpenCV](https://opencv.org/) 4.11 |
| Deep Learning backend | [TensorFlow / tf-keras](https://keras.io/) 2.20 |
| Desktop UI | [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) 1.19 (Tkinter) |
| Image Processing | [Pillow](https://python-pillow.org/) |
| Numerical Computing | [NumPy](https://numpy.org/) |
| Serial Communication | [pyserial](https://pyserial.readthedocs.io/) 3.5 |
| Linter | [Ruff](https://docs.astral.sh/ruff/) |
| Language | Python 3.10 |

---

## Architecture

```
dormmon/
├── app.py                  # Flask entry point
├── database.py             # Peewee ORM models
├── database_access.py      # Query / data access layer
├── recognition.py          # Face recognition endpoints
├── face_encoding.py        # Encoding utilities
├── tasks.py                # Cleaning rotation logic
├── user.py / event.py / ledger.py / ...  # REST endpoints
│
├── acn_ui/                 # Desktop app (Tkinter)
│   ├── ui.py               # Main window & navigation
│   ├── api.py              # HTTP client for the backend
│   └── pages/
│       ├── face.py         # Face recognition login
│       ├── home.py         # Dashboard + weather widget
│       ├── balance.py      # Balances & payments
│       ├── trash.py        # Trash tracking
│       ├── expense.py      # Expense entry
│       └── cleanroom.py    # Cleaning schedule
│
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS & JS
├── database/               # Face training images (per user)
└── uploads/                # Event photos from webcam
```

The backend exposes a REST API consumed by both the web templates and the desktop app. The desktop app communicates entirely over HTTP, so it can run on any machine on the local network.

---

## Installation

### Prerequisites

- Python 3.10
- A webcam (for face recognition)
- CMake and C++ build tools (required to compile `dlib`)
  - macOS: `brew install cmake`
  - Ubuntu/Raspberry Pi: `sudo apt install cmake build-essential`

### 1. Clone the repository

```bash
git clone <repo-url>
cd dormmon
```

### 2. Create a virtual environment

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

Or with [`uv`](https://github.com/astral-sh/uv):

```bash
uv sync
```

> The first install may take a few minutes — `dlib` compiles from source.

### 4. Run the app

**Full stack (server + desktop UI):**
```bash
./run.sh
```

**Web server only:**
```bash
flask run -h 0.0.0.0 -p 5000
# Open http://localhost:5000
```

**Desktop UI only** (pointing at an existing server):
```bash
cd acn_ui
DORMMON_API_BASE_URL=http://<server-ip>:5000 python ui.py
```

The SQLite database is created automatically on first run — no migrations needed.

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DORMMON_API_BASE_URL` | `http://localhost:5000` | Backend URL used by the desktop UI |

Weather display (on the home screen) uses the OpenWeather API. The key and city can be set in `acn_ui/pages/home.py`.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List users with balances |
| `POST` | `/users` | Add user with face images |
| `GET` | `/events` | List recent events |
| `POST` | `/events` | Log a new event |
| `POST` | `/ledger/pay` | Record a payment |
| `GET` | `/status_view` | Current task statuses |
| `GET` | `/schedule` | 6-week cleaning schedule |
| `POST` | `/face/recognize` | Identify a user from a photo |
| `GET/POST` | `/items` | List or add shared items |
| `POST` | `/stock` | Update item stock level |

---

## Database Schema

| Table | Description |
|-------|-------------|
| `User` | Roommate profiles with stored 128-D face encodings |
| `EventCategory` | Categories: Trash, Room Cleaning, Purchases, etc. |
| `Event` | Logged household events with optional webcam photos |
| `Ledger` | Financial transactions (expenses & direct payments) |
| `Item` | Shared inventory items |
| `ItemStock` | Stock level history per item |

---

## Enrolling a New Roommate

1. Open the web dashboard at `http://localhost:5000/users`
2. Click **Add User** and upload several photos of the new roommate
3. The system averages all face encodings into a single 128-dimensional vector stored in the database
4. The roommate can now log in on the desktop app via face recognition

---

## License

This project was built for academic purposes.
