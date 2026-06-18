# Freelance Marketplace API

Backend API for a small freelance marketplace built with Django REST Framework, JWT auth, PostgreSQL, and `django-filter`.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure PostgreSQL environment variables:

```bash
POSTGRES_DB=jobx
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Start the server:

```bash
python manage.py runserver
```

## API Endpoints

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`

### Projects

- `GET /api/projects/`
- `POST /api/projects/`
- `GET /api/projects/<id>/`
- `GET /api/projects/<id>/bids/`
- `POST /api/projects/<id>/bids/`
- `POST /api/projects/<id>/bids/<bid_id>/accept/`

### Contracts

- `GET /api/contracts/`
- `GET /api/contracts/<id>/`
- `POST /api/contracts/<id>/finish/`
- `POST /api/contracts/<id>/review/`

## Swagger

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`

## Query Parameters

The project list endpoint supports:

- `search=<title>`
- `min_budget=<value>`
- `max_budget=<value>`

Pagination is 10 items per page.

## Postman

Import `postman/Freelance-Marketplace.postman_collection.json` into Postman to test the full API flow.
You can also import `postman/Freelance-Marketplace.openapi.yaml` if you want Postman to generate the collection from the OpenAPI schema.
