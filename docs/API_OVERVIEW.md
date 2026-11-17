# API Overview

Base path: `/api/v1` (interactive docs at `/docs`). Authentication uses a JWT bearer token from `/auth/login`.

## Authentication
| Method | Path | Access |
|--------|------|--------|
| POST | `/auth/login` | Public |
| POST | `/auth/logout` | Authenticated |
| GET | `/auth/me` | Authenticated |

## Documents
| Method | Path | Access |
|--------|------|--------|
| POST | `/documents/upload` | Authenticated |
| POST | `/documents/{id}/process` | Authenticated |
| GET | `/documents/{id}/status` | Authenticated |
| GET | `/documents/{id}/metadata` | Authenticated |
| PATCH | `/documents/{id}/metadata` | Authenticated |
| GET | `/documents/{id}` | Authenticated |
| GET | `/documents` | Authenticated |
| DELETE | `/documents/{id}` | Authenticated |

## Search
| Method | Path | Access |
|--------|------|--------|
| GET | `/search` | Authenticated (results are permission-filtered) |

## Taxonomy
| Method | Path | Access |
|--------|------|--------|
| GET | `/categories` | Authenticated |
| POST | `/categories` | Admin |
| DELETE | `/categories/{id}` | Admin |

## Administration
| Method | Path | Access |
|--------|------|--------|
| GET | `/users` | Admin |
| POST | `/users` | Admin |
| PATCH | `/users/{id}/role` | Admin |
| POST | `/admin/reindex` | Admin |
| GET | `/admin/metrics` | Admin |
| GET | `/audit/logs` | Auditor, Admin |

## Operations
| Method | Path | Access |
|--------|------|--------|
| GET | `/health` (also `/api/v1/health`) | Public |
| GET | `/metrics` | Service metrics |

Access rules are enforced server-side by `require_roles` and `get_current_user` in `backend/app/api/deps.py`.
