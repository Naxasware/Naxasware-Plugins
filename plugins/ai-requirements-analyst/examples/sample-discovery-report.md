# Discovery Report — Gym Check-In & Class Booking App

## Problem Statement
Small gyms need a way to track member check-ins and manage class bookings. The current process wasn't described — assume manual/no system exists unless told otherwise.

## Business Objective
BO-001: Give small gyms a simple way to track who's checked in and let members book classes, replacing manual/ad-hoc tracking.

## Stakeholders
ST-001: Gym Owner/Manager — interested in attendance visibility, class capacity utilization.
ST-002: Member — interested in easy check-in and booking.

## Actors
ACT-001: Front Desk Staff / Gym Owner
ACT-002: Member
ACT-003: Class Instructor (inferred — classes usually have an instructor, but not stated; flagged below as an assumption)

## Functional Requirements

FR-001 — Check in a member
Actor: ACT-001
Trigger: Member arrives at the gym
Behavior: Staff (or member via self-service) records a check-in against the member's account
Acceptance: A check-in record is created with member ID and timestamp

FR-002 — Book a class
Actor: ACT-002
Trigger: Member selects a class and requests a spot
Precondition: Class has available capacity
Behavior: System reserves a spot for the member
Acceptance: A booking record is created; capacity count decrements

FR-003 — View class schedule
Actor: ACT-002
Behavior: Member can see upcoming classes, times, and remaining capacity

## Business Rules
BR-001: A member cannot book a class that is already at capacity. (Needs confirmation: is there a waitlist, or is the booking simply rejected?)

## Data Requirements
DR-001: Member — name, contact info, membership status
DR-002: Class — name, schedule, capacity, instructor
DR-003: Check-in — member ID, timestamp
DR-004: Booking — member ID, class ID, timestamp, status

## Non-Functional Requirements
Not specified — no NFR section is included because nothing was said about expected member count, response-time expectations, or compliance needs. Flagging as an open question below rather than guessing.

## Assumptions
A-001: There is a single gym location (not a multi-location chain). Reason: not stated either way. Impact if wrong: data model needs a "location" entity and staff/class scoping per location. Needs confirmation: yes.
A-002: Classes have a named instructor (ACT-003). Reason: typical for gym class scheduling. Impact if wrong: instructor field/actor is unnecessary. Needs confirmation: yes.

## Open Questions
Q-001: Should check-in be self-service (e.g. a kiosk or QR code) or staff-operated?
Q-002: Is there a waitlist for full classes, or is booking simply blocked once capacity is reached?
Q-003: Does membership status (active/expired/frozen) affect whether someone can check in or book?

## What's Not Included
No NFR, integration, or permissions sections were generated — nothing in the request supports them yet. Add these once basic scope is confirmed.
