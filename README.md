# AnkiLite

AnkiLite is a full-stack spaced-repetition learning system inspired by Anki, built with an emphasis on transparency, configurability, and time-aware learning behavior.

Unlike traditional SRS tools where scheduling behavior is largely opaque, AnkiLite exposes scheduling rules directly to the user, allows per-deck customization, supports both strict review and freeform practice modes, and records timing signals to better understand learning difficulty.

The project is designed both as a usable study tool and as a systems-level exploration of how spaced-repetition algorithms actually behave.

---

## What AnkiLite Does

AnkiLite lets users create decks of flashcards, review them using spaced repetition, and explicitly control how and when cards become due again.

Each user:
- registers and logs in
- creates decks
- adds cards to decks
- reviews cards using different modes
- controls scheduling behavior at the deck level

All data is isolated per user.

---

## Authentication & User Isolation

AnkiLite uses JWT-based authentication.

Each registered user has:
- their own decks
- their own cards
- their own review history
- completely isolated data

Users never see or affect each other’s content.

Logging out clears local authentication state and allows switching accounts.

---

## Decks

A deck is more than a container for cards.  
It defines how learning works.

Each deck has:
- a name and description
- a scheduling mode
- configurable review intervals for each grade
- configurable time units

### Scheduling Modes

There are two scheduling modes:

Fixed mode  
Intervals are exactly what the user specifies. A card graded “Good” always becomes due after the same amount of time, regardless of history.

Hybrid mode  
Intervals start from the user’s specified values but grow over time using an ease-based multiplier. This preserves user intent while allowing natural spacing growth.

Deck settings can be changed at any time, and changes immediately affect future reviews.

---

## Cards

Each card belongs to exactly one deck and one user.

Cards store:
- front text
- back text
- optional tags
- current interval
- due time
- ease factor
- repetition count
- lapse count

Cards persist across sessions and are never automatically deleted.

---

## Review Modes

### Due Mode (Spaced Repetition)

In Due mode:
- only cards whose due time has passed are shown
- scheduling rules are enforced
- this mirrors traditional Anki-style behavior

If no cards are due, the user is informed that they are “done for now”.

### Cram Mode (Practice)

In Cram mode:
- any card can be reviewed regardless of due time
- scheduling is optional
- useful for last-minute studying or free practice

Users can switch between modes at any time.

---

## Review Flow

Each review follows a deterministic process:

1. Show the card front
2. User reveals the back
3. User selects a grade:
   Again, Hard, Good, or Easy
4. The system updates the card’s state

There is no randomness.  
Given the same inputs, the outcome is always the same.

---

## Time-Aware Review Signals

For each review, the system records:
- time spent before revealing the answer
- time spent choosing a grade

These timing signals are:
- stored for analytics
- optionally used to prioritize which card is shown next

This allows future extensions such as difficulty estimation, hesitation detection, and learning analytics.

---

## Force-Due & Manual Control

Users can:
- force all cards in a deck to become due immediately
- optionally reset card progress
- review decks even when nothing is scheduled

This ensures the system never blocks a motivated learner from studying.

---

## Scheduling Philosophy

AnkiLite is fully deterministic and explainable.

Given:
- the deck’s scheduling mode
- the user’s grade
- the card’s current state

The next due time can always be predicted and explained.

This makes the system transparent, debuggable, and educational.

---

## Technology Stack

Backend:
- Django
- Django REST Framework
- SimpleJWT authentication
- SQLite for relational data
- MongoDB for review event logs

Frontend:
- Angular with standalone components
- JWT-based authentication handling
- Centralized API services
- Route-based navigation

---

## Backend Architecture (Conceptual)

The backend is organized around responsibilities rather than features.

Authentication logic is isolated from learning logic.  
Deck and card management is separated from review scheduling.  
Scheduling logic is centralized so it can be replaced or extended.

Review events are stored separately from core relational data to support analytics and future insights.

---

## Frontend Architecture (Conceptual)

The frontend is organized around user tasks:
- logging in
- managing decks and cards
- reviewing cards

Services handle all backend communication.  
Pages focus on UI state and user interaction.

This separation keeps the UI simple and predictable.

---

## Data Persistence Model

Relational data:
- users
- decks
- cards
- scheduling configuration

Event-based data:
- review events
- timing signals
- session identifiers

This hybrid model avoids bloating the relational schema while preserving detailed learning history.

---

## Running the Project Locally

Backend:
- create a virtual environment
- install dependencies
- run migrations
- start the Django server

Frontend:
- install npm dependencies
- start the Angular dev server

The backend runs on port 8000.  
The frontend runs on port 4200.

---

## Project Status

AnkiLite is a complete MVP with:
- real authentication
- configurable scheduling
- multiple review modes
- time-aware review tracking
- persistent storage
- a usable UI

It is intentionally designed to be extendable rather than minimal.

---

## Why AnkiLite Exists

AnkiLite is not just a flashcard app.

It is an exploration of:
- how spaced repetition systems behave
- how user control compares to opaque heuristics
- how timing reflects learning difficulty
- how learning tools can be transparent rather than mysterious

If you have ever wondered why Anki schedules cards the way it does, AnkiLite shows you.
