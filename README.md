# Freelance Marketplace API

A Django REST Framework backend for a freelance marketplace platform (similar to Upwork). Clients post projects, freelancers place bids, contracts are created on acceptance, and reviews close the loop.

## Tech Stack

- **Python 3.14** / **Django 6.x** / **DRF 3.16+**
- **PostgreSQL** (no SQLite fallback)
- **JWT Authentication** via djangorestframework-simplejwt
- **Filtering** via django-filter
- **OpenAPI/Swagger** via drf-spectacular

## Setup

### 1. Clone and install

`ash
git clone https://github.com/Aminovich7/job-x.git
cd job-x
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
`

### 2. Configure PostgreSQL

Set environment variables or use defaults from conf/settings.py:

`ash
export POSTGRES_DB=jobx
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=7799
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432
`

### 3. Run

`ash
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
`

Server starts at http://127.0.0.1:8000.

## Authentication

All endpoints require JWT authentication except /api/auth/register/ and /api/auth/login/.

`ash
# Register
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "client1", "email": "client1@example.com", "password": "pass1234!", "role": "client"}'

# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "client1", "password": "pass1234!"}'
# Returns: {"refresh": "...", "access": "..."}

# Use the access token in subsequent requests
curl http://127.0.0.1:8000/api/projects \
  -H "Authorization: Bearer ACCESS_TOKEN_HERE"
`

**Token lifetime**: 1 day. **Logout**: POST /api/auth/logout/ with {"refresh": "TOKEN"}.

## API Endpoints

> **Note**: Auth endpoints use trailing slash (/api/auth/register/).
> Project/contract endpoints do **NOT** (/api/projects). Mismatched slashes return 404.

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/auth/register/ | No | Register (role: client or freelancer) |
| POST | /api/auth/login/ | No | Login, get JWT tokens |
| POST | /api/auth/logout/ | Yes | Blacklist refresh token |
| GET | /api/auth/profile/ | Yes | Get own profile |
| PATCH | /api/auth/profile/ | Yes | Update username, email, bio |
| PUT | /api/auth/profile/password/ | Yes | Change password |

### Projects

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/projects | Yes | List open projects (paginated, filterable) |
| POST | /api/projects | Yes | Create project (client only) |
| GET | /api/projects/<id>/ | Yes | Project detail |
| PATCH | /api/projects/<id>/ | Yes | Update project (owner only, open only) |
| POST | /api/projects/<id>/cancel/ | Yes | Cancel project (owner only, open only) |
| GET | /api/projects/<id>/skills/ | Yes | List project skills |
| POST | /api/projects/<id>/skills/ | Yes | Add skill to project (owner only) |
| DELETE | /api/projects/<id>/skills/ | Yes | Remove skill from project (owner only) |

### Bids

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/projects/<id>/bids/ | Yes | List bids (project owner only) |
| POST | /api/projects/<id>/bids/ | Yes | Place bid (freelancer only) |
| DELETE | /api/projects/<id>/bids/<bid_id>/ | Yes | Withdraw bid (own, pending only) |
| POST | /api/projects/<id>/bids/<bid_id>/accept/ | Yes | Accept bid, creates contract (owner only) |

### Contracts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/contracts | Yes | List user contracts |
| GET | /api/contracts/<id>/ | Yes | Contract detail (participants only) |
| POST | /api/contracts/<id>/finish/ | Yes | Finish contract (client only) |
| POST | /api/contracts/<id>/cancel/ | Yes | Cancel contract (client or freelancer) |
| POST | /api/contracts/<id>/review/ | Yes | Review contract (client only, one per contract) |

### Freelancers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/freelancers/ | Yes | List freelancers (searchable) |
| GET | /api/freelancers/<id>/reviews/ | Yes | Freelancer reviews |
| GET | /api/freelancers/<id>/skills/ | Yes | Freelancer skills |

### Skills and Categories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/skills/ | Yes | List all skills |
| GET | /api/categories/ | Yes | List all categories |

## Query Parameters

### Projects (GET /api/projects)

| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search by title (case-insensitive) |
| min_budget | number | Minimum budget |
| max_budget | number | Maximum budget |
| page | integer | Page number (10 items per page) |

### Freelancers (GET /api/freelancers/)

| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search by username or bio (case-insensitive) |
| page | integer | Page number (10 items per page) |

## Business Flow

`
Client registers -> creates project -> Freelancer places bid -> Client accepts bid
                                                                      |
                                                              Contract created
                                                                      |
                                                              Client finishes
                                                                      |
                                                              Client reviews (1-5)
`

1. **Client** creates a project (status: open)
2. **Freelancer** places a bid (one per project)
3. **Client** accepts a bid -> other bids rejected, project in_progress, contract auto-created
4. **Client** finishes contract -> project completed
5. **Client** leaves a review (rating 1-5, one per contract)

**Cancel paths**: Client can cancel open projects. Either party can cancel active contracts.

## Permissions

| Role | Can Do |
|------|--------|
| **Client** | Create/update/cancel projects, view/accept bids, finish/cancel contracts, review |
| **Freelancer** | Browse projects, place/withdraw bids, cancel contracts |

## Swagger / OpenAPI

- **Schema**: GET /api/schema/
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **Postman import**: postman/Freelance-Marketplace.openapi.yaml

## Project Structure

`
job-x/
  conf/           # Settings, root URLs
  users/          # Custom User model, auth, profile
  projects/       # Projects, Bids, permissions, filters
  contracts/      # Contracts, Reviews
  freelancers/    # Freelancer search, reviews, skills
  skills/         # Skill and Category models
  postman/        # OpenAPI YAML spec
  manage.py
  requirements.txt
`

## Database

- **PostgreSQL only** - no SQLite fallback
- **User model**: users.User (extends AbstractUser with role, bio, skills)
- **Bid uniqueness**: enforced at serializer + database constraint level
- **Contract**: one per project (OneToOneField)
- **Review**: one per contract (OneToOneField)

## License

MIT
