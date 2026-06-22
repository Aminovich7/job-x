# Freelance Marketplace API â€” Project & Business Logic Explanation

## Overview

**job-x** is a backend API for a freelance marketplace platform (similar to Upwork). It connects **clients** who post projects with **freelancers** who bid on them. The platform handles the entire lifecycle: project creation, bidding, contract, delivery, review.

**Tech Stack:** Django 6.x, Django REST Framework 3.16+, PostgreSQL, JWT Authentication (simplejwt), django-filter, drf-spectacular.

---

## User Roles

| Role | Who | Can Do |
|------|-----|--------|
| **Client** | Business/person needing work done | Create projects, view bids, accept bids, finish contracts, leave reviews |
| **Freelancer** | Developer/contractor | Browse projects, place bids, withdraw bids, work on contracts |

---

## Core Business Flow

1. Client registers with role client
2. Freelancer registers with role freelancer
3. Client creates a project (title, description, budget, deadline). Status = open
4. Freelancers browse open projects and place bids (price + message). One bid per freelancer per project
5. Client reviews bids and accepts one. This triggers: accepted bid -> accepted, other bids -> rejected, project -> in_progress, contract auto-created with agreed price
6. Client and freelancer collaborate (tracked via contract)
7. Client marks contract as finished. Project status -> completed
8. Client leaves a rating (1-5) and comment. One review per contract

---

## Data Models

### User (users/models.py)
Extends Django AbstractUser with: role (client/freelancer), bio, created_at, skills (M2M with Skill)

### Project (projects/models.py)
title, description, budget (decimal), deadline (date), status (open/in_progress/completed/cancelled), client FK, skills (M2M), category FK, created_at

### Bid (projects/models.py)
project FK, freelancer FK, price (decimal), message, status (pending/accepted/rejected), created_at. UniqueConstraint on (project, freelancer)

### Contract (contracts/models.py)
project (OneToOne), client FK, freelancer FK, agreed_price, status (active/finished/cancelled), created_at, finished_at

### Review (contracts/models.py)
contract (OneToOne), rating (1-5), comment, created_at

### Skill (skills/models.py)
name (unique), description

### Category (skills/models.py)
name (unique), description

---

## API Endpoints Summary

### Authentication
- POST /api/auth/register/ â€” Register new user (no auth)
- POST /api/auth/login/ â€” Login, get JWT tokens (no auth)
- POST /api/auth/logout/ â€” Blacklist refresh token
- GET/PATCH /api/auth/profile/ â€” View/update profile
- PUT /api/auth/profile/password/ â€” Change password

### Projects
- GET /api/projects â€” List open projects (paginated, filterable by search, min_budget, max_budget)
- POST /api/projects â€” Create project (client only)
- GET /api/projects/{id}/ â€” Project detail
- PATCH /api/projects/{id}/ â€” Update project (owner only, open only)
- POST /api/projects/{id}/cancel/ â€” Cancel project (owner only, open only)
- GET/POST/DELETE /api/projects/{id}/skills/ â€” Manage project skills
- GET/POST /api/projects/{id}/bids/ â€” List/create bids
- DELETE /api/projects/{id}/bids/{bid_id}/ â€” Withdraw bid (freelancer only, pending only)
- POST /api/projects/{id}/bids/{bid_id}/accept/ â€” Accept bid (client only, creates contract)

### Contracts
- GET /api/contracts â€” List user contracts
- GET /api/contracts/{id}/ â€” Contract detail (participants only)
- POST /api/contracts/{id}/finish/ â€” Finish contract (client only)
- POST /api/contracts/{id}/cancel/ â€” Cancel contract (client or freelancer)
- POST /api/contracts/{id}/review/ â€” Review contract (client only, one per contract)

### Freelancers
- GET /api/freelancers/ â€” List freelancers (searchable by username/bio)
- GET /api/freelancers/{id}/reviews/ â€” Freelancer reviews
- GET /api/freelancers/{id}/skills/ â€” Freelancer skills

### Skills and Categories
- GET /api/skills/ â€” List all skills
- GET /api/categories/ â€” List all categories

---

## Key Business Rules

1. One bid per freelancer per project (serializer + DB constraint)
2. Only open projects can be edited or cancelled
3. Accepting a bid is transactional (transaction.atomic)
4. One review per contract
5. Contract finish sets finished_at timestamp
6. Contract cancel propagates to project
7. Only pending bids can be withdrawn
8. Deadline must be in the future

---

## Permission System

- IsClient: role must be client
- IsFreelancer: role must be freelancer
- IsAuthenticatedClientWrite: GET any auth, POST client only
- IsAuthenticatedFreelancerBidWrite: GET any auth, POST freelancer only
- IsProjectOwner: obj.client == request.user
- IsContractParticipant: user in (obj.client, obj.freelancer)
- IsContractClient: user == obj.client
- enforce_permission(): manual permission check helper

---

## Filtering and Pagination

- Projects: search (title icontains), min_budget, max_budget. Page size 10.
- Freelancers: search (username or bio icontains). Page size 10.
- Contracts: No pagination.
- Users: No pagination.

---

## JWT Authentication

- Access token lifetime: 1 day
- Header: Authorization: Bearer <access_token>
- Token blacklist enabled for logout

---

## Database

- PostgreSQL only (no SQLite fallback)
- AUTH_USER_MODEL = users.User
- DEFAULT_AUTO_FIELD = django.db.models.AutoField

---

## Swagger / OpenAPI

- Schema: GET /api/schema/
- Swagger UI: /api/docs/
- Postman: postman/Freelance-Marketplace.openapi.yaml

