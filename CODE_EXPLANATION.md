# Freelance Marketplace API - Detailed Code Explanation

## Table of Contents

1. Project Structure
2. Settings and Configuration
3. URL Routing
4. Users App
5. Projects App
6. Contracts App
7. Freelancers App
8. Skills App
9. Permissions System
10. Serializers Deep Dive

---

## Project Structure

`
job-x/
  conf/          # Project configuration
  users/         # User model, auth, profile
  projects/      # Projects and Bids
  contracts/     # Contracts and Reviews
  freelancers/   # Freelancer search and discovery
  skills/        # Skills and Categories
  manage.py      # Django management command
  requirements.txt
`

---

## Settings and Configuration

### conf/settings.py

Key settings:

- AUTH_USER_MODEL = users.User (Custom user model)
- DEFAULT_AUTO_FIELD = django.db.models.AutoField

INSTALLED_APPS: rest_framework, rest_framework_simplejwt, rest_framework_simplejwt.token_blacklist, django_filters, drf_spectacular, users, projects, contracts, freelancers, skills

REST_FRAMEWORK: JWTAuthentication, IsAuthenticated, DjangoFilterBackend, drf_spectacular

SIMPLE_JWT: ACCESS_TOKEN_LIFETIME = timedelta(days=1)

DATABASES: PostgreSQL (jobx / postgres / 7799 / 127.0.0.1 / 5432)

---

## URL Routing

### Root URLs (conf/urls.py)

- /api/auth/ -> users.urls (trailing slash)
- /api/projects -> projects.urls (no trailing slash)
- /api/contracts -> contracts.urls (no trailing slash)
- /api/freelancers/ -> freelancers.urls (trailing slash)
- /api/ -> skills.urls

Critical: Auth uses trailing slash, projects/contracts do NOT. Mismatched slashes return 404.

---

## Users App

### users/models.py

Custom User model extending AbstractUser with:
- role: client or freelancer
- bio: optional text
- created_at: auto timestamp
- skills: M2M with Skill

### users/serializers.py

RegisterSerializer: Accepts username, email, password (write-only), role. Validates email uniqueness. Hashes password in create().
LoginSerializer: Uses authenticate() to verify credentials. Returns user in attrs.
UserProfileSerializer: Allows updating username, email, bio. Validates username and email uniqueness. Role/read-only fields protected.
ChangePasswordSerializer: Validates old password, runs Django validators on new password.

### users/views.py

register_view: POST /api/auth/register/ (AllowAny). Returns UserSerializer.
login_view: POST /api/auth/login/ (AllowAny). Returns JWT tokens.
logout_view: POST /api/auth/logout/ (IsAuthenticated). Blacklists refresh token.
profile_view: GET/PATCH /api/auth/profile/ (IsAuthenticated). Get/update profile.
change_password_view: PUT /api/auth/profile/password/ (IsAuthenticated). Change password.

---

## Projects App

### projects/models.py

Project: title, description, budget (decimal), deadline (date), status (open/in_progress/completed/cancelled), client FK, skills M2M, category FK, created_at.

Bid: project FK, freelancer FK, price (decimal), message, status (pending/accepted/rejected), created_at. UniqueConstraint on (project, freelancer).

### projects/serializers.py

ProjectSerializer(DeadlineValidationMixin): Writable: title, description, budget, deadline. Read-only: id, status, client, created_at. Deadline validation via mixin.
BidSerializer: Writable: price, message. Requires request/project/freelancer in context. Validates no duplicate bids. Role check enforced by view (IsFreelancer).
ProjectUpdateSerializer(DeadlineValidationMixin): Same fields. Validates project is open before allowing edits.

### projects/views.py

project_list_create_view: GET filters open projects (search/budget, paginated 10/page). POST creates project (client only).
project_detail_view: GET returns project. Any auth user.
project_bids_view: GET lists bids (project owner only). POST creates bid (freelancer only).
accept_bid_view: POST accepts bid transactionally. Creates contract, rejects other bids, updates project status.
project_update_view: PATCH updates project (owner only, open only).
project_cancel_view: POST cancels project (owner only, open only).
bid_withdraw_view: DELETE withdraws bid (freelancer only, pending only).
project_skills_view: GET/POST/DELETE manage project skills (owner only).

### projects/filters.py

ProjectFilter: search (title icontains), min_budget (gte), max_budget (lte).

---

## Contracts App

### contracts/models.py

Contract: OneToOne to Project, client FK, freelancer FK, agreed_price, status (active/finished/cancelled), created_at, finished_at.
Review: OneToOne to Contract, rating (1-5), comment, created_at.

### contracts/serializers.py

ContractSerializer: Fully read-only.
FinishContractSerializer: Validates contract is active. Permission check enforced by view (IsContractClient).
ReviewSerializer: Validates contract is finished and no existing review. Permission check enforced by view (IsContractClient).
CancelContractSerializer: Validates contract is active. Permission check enforced by view (IsContractParticipant).

### contracts/views.py

contract_list_view: GET lists contracts where user is client or freelancer.
contract_detail_view: GET returns contract (participants only).
finish_contract_view: POST finishes contract (client only). Sets finished_at, project completed.
cancel_contract_view: POST cancels contract (client or freelancer). Sets project cancelled.
review_contract_view: POST creates review (client only). One per contract.

---

## Freelancers App

### freelancers/filters.py

FreelancerFilter: search (username OR bio icontains) using Q objects.

### freelancers/serializers.py

FreelancerSerializer: Read-only User (id, username, email, bio, created_at).
FreelancerReviewSerializer: Read-only with reviewer info (source traversal).

### freelancers/views.py

freelancer_list_view: GET lists freelancers (paginated 10/page, searchable).
freelancer_reviews_view: GET lists freelancer reviews (paginated, select_related for N+1).
freelancer_skills_view: GET lists freelancer skills.

---

## Skills App

### skills/models.py

Skill: name (unique), description. Ordered by name.
Category: name (unique), description. Ordered by name.

### skills/views.py

skill_list_view: GET /api/skills/ - lists all skills.
category_list_view: GET /api/categories/ - lists all categories.

---

## Permissions System

### projects/permissions.py

enforce_permission(): Helper that instantiates permission class, checks has_permission() and has_object_permission(). Raises PermissionDenied.
IsClient: role must be client.
IsFreelancer: role must be freelancer.
IsAuthenticatedClientWrite: GET any auth, POST client only.
IsAuthenticatedFreelancerBidWrite: GET any auth, POST freelancer only.
IsProjectOwner: Object-level - obj.client == request.user.

### contracts/permissions.py

IsContractParticipant: user in (obj.client, obj.freelancer).
IsContractClient: user == obj.client.

### Dual Enforcement Pattern

1. DRF permission_classes decorator (view-level)
2. Manual enforce_permission() call inside view (object-level)
Provides defense-in-depth security.

---

## Serializers Deep Dive

### Context Passing Pattern

Serializers receive context from views (project, freelancer, contract). Views handle permission checks; serializers use context for data validation only.

### Validation Layers

1. Serializer validation (data format, uniqueness, business rules)
2. Permission checks (view-level via enforce_permission())
Serializers handle data validation only. Permission/role checks are enforced in views. Example: Bid creation uses enforce_permission(IsFreelancer) in view + BidSerializer validates no duplicate bids + UniqueConstraint.

### Transaction Pattern

Multi-model writes use transaction.atomic() for consistency. Used in accept_bid_view, finish_contract_view, cancel_contract_view.

### read_only_fields Pattern

Serializers use read_only_fields to prevent client manipulation. Fields like client set by view (serializer.save(client=request.user)).

---

## Key Patterns Summary

| Pattern | Where Used | Purpose |
|---------|-----------|---------|
| @api_view + @permission_classes | All views | Function-based views with DRF |
| @extend_schema | All views | OpenAPI documentation |
| enforce_permission() | Views with object-level perms | Manual permission checks |
| transaction.atomic() | Multi-model writes | Data consistency |
| Context passing | Serializers | Access to request/objects |
| get_object_or_404() | Detail views | 404 handling |
| select_related() | Freelancer reviews | N+1 query prevention |
| update_fields=[] | Model saves | Partial updates |
| read_only_fields | All serializers | Prevent client manipulation |
| UniqueConstraint | Bid model | Database-level uniqueness |
