# Event Registration System API

A RESTful API built with FastAPI and SQLite for managing event registrations with seat limits, validation rules, and race condition protection.

## Tech Stack

- **Python 3.14**
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **SQLite** — embedded database
- **Pydantic** — data validation
- **Poetry** — dependency management

## Features

- Create events with seat limits and future date validation
- Register users for events with duplicate prevention
- View all events with available seat counts, sortable by date
- Filter upcoming events only
- Cancel registrations with automatic seat restoration
- Race condition prevention via database-level row locking
- Soft deletes — cancelled registrations preserved in history

## Project Structure
├── main.py               # App entry point, router registration

├── database.py           # SQLite connection and session factory

├── models.py             # SQLAlchemy ORM models (Event, Registration)

├── schemas.py            # Pydantic request/response schemas

├── routers/

│   ├── events.py         # Event endpoints

│   └── registrations.py  # Registration endpoints

├── pyproject.toml        # Poetry dependency config

└── poetry.lock           # Locked dependency versions

## Setup & Installation

### Prerequisites
- Python 3.14+
- Poetry

### Install dependencies

```bash
poetry install
```

### Run the server

```bash
poetry run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

Interactive docs at `http://127.0.0.1:8000/docs`

## API Endpoints

### Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/events/` | Create a new event |
| GET | `/events/` | List all events, sorted by date |
| GET | `/events/?upcoming_only=true` | Filter future events only |

### Registrations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/registrations/` | Register a user for an event |
| DELETE | `/registrations/{id}` | Cancel a registration |

## Example Usage

### Create an Event

```bash
curl -X POST http://127.0.0.1:8000/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Conference 2026",
    "total_seats": 50,
    "event_date": "2026-12-01T10:00:00Z"
  }'
```

### Register a User

```bash
curl -X POST http://127.0.0.1:8000/registrations/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Ahmed Fazil",
    "event_id": 1
  }'
```

### Cancel a Registration

```bash
curl -X DELETE http://127.0.0.1:8000/registrations/1
```

## Validation Rules

**Events**
- Name must be unique
- Total seats must be greater than 0
- Event date must be in the future

**Registrations**
- Cannot register if event is fully booked
- Same user cannot register twice for the same event
- Cancelled users can re-register
- Cancellation restores the seat automatically

## Race Condition Handling

Overbooking is prevented using database-level row locking via SQLAlchemy's `with_for_update()`. When a registration request comes in, the event row is locked for the duration of the transaction. Any concurrent request targeting the same event is blocked until the lock is released, ensuring seat counts are always accurate.

## Author

Ahmed Fazil  
Innovaxel Summer Internship Program 2026  
Role: Backend Developer