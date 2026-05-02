# Authentication Guide - Team Task Manager

This guide explains how to use the JWT-based authentication system in the Team Task Manager API.

## Overview

The Team Task Manager uses:
- **Password Hashing**: Bcrypt via passlib
- **Token Generation**: JWT (JSON Web Tokens) via python-jose
- **Token Validation**: Custom dependency injection for protected routes

## Authentication Endpoints

### 1. Sign Up
**Endpoint**: `POST /api/auth/signup`

Create a new user account.

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "member",
    "created_at": "2026-05-02T10:30:00",
    "updated_at": "2026-05-02T10:30:00"
  }
}
```

**Errors**:
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid input format

### 2. Login
**Endpoint**: `POST /api/auth/login`

Authenticate and get a JWT token.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "member",
    "created_at": "2026-05-02T10:30:00",
    "updated_at": "2026-05-02T10:30:00"
  }
}
```

**Errors**:
- `401 Unauthorized`: Invalid email or password
- `422 Unprocessable Entity`: Invalid input format

### 3. Get Current User
**Endpoint**: `GET /api/auth/me`

Get information about the currently logged-in user.

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "member",
  "created_at": "2026-05-02T10:30:00",
  "updated_at": "2026-05-02T10:30:00"
}
```

**Errors**:
- `401 Unauthorized`: Invalid or missing token

### 4. Refresh Token
**Endpoint**: `POST /api/auth/refresh`

Get a new JWT token (useful before token expiration).

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "member",
    "created_at": "2026-05-02T10:30:00",
    "updated_at": "2026-05-02T10:30:00"
  }
}
```

### 5. Logout
**Endpoint**: `POST /api/auth/logout`

Logout the current user (client-side token deletion).

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out. Please discard the token.",
  "user_id": 1
}
```

## Using Protected Endpoints

All protected endpoints require the `Authorization` header with a Bearer token.

**Example - Create a Project**:
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Project description"
  }'
```

## Token Structure

The JWT token contains:
- `sub`: Subject (user ID)
- `exp`: Expiration time
- `iat`: Issued at time

**Default Token Expiration**: 30 minutes (configurable in `.env`)

## Configuration

Token settings are in `app/core/config.py`:

```python
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Environment Variables (.env)

```
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Security Best Practices

1. **Never share tokens**: Keep JWT tokens confidential
2. **Use HTTPS**: Always use HTTPS in production
3. **Change SECRET_KEY**: Use a strong, random secret key in production
4. **Token expiration**: Set appropriate expiration times
5. **Secure storage**: Store tokens securely on the client (not in localStorage if possible)
6. **CORS**: Configure CORS properly to prevent unauthorized access

## Testing with cURL

### Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "password": "Password123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "Password123!"
  }'
```

Save the `access_token` from the response.

### Get Current User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {your_access_token_here}"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer {your_access_token_here}"
```

### Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer {your_access_token_here}"
```

## Using in Python (requests library)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Sign up
signup_data = {
    "name": "Bob Johnson",
    "email": "bob@example.com",
    "password": "SecurePassword123!"
}
signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
token = signup_response.json()["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {token}"}
user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(user_response.json())

# Create a project
project_data = {
    "name": "My New Project",
    "description": "Test project"
}
project_response = requests.post(
    f"{BASE_URL}/projects",
    json=project_data,
    headers=headers
)
print(project_response.json())
```

## Password Requirements

Passwords should:
- Be at least 8 characters long (enforced by best practices)
- Include uppercase and lowercase letters
- Include numbers
- Include special characters

Example strong password: `Tr0pic@lBreeze#2024`

## Token Expiration

When a token expires, you'll receive a 401 error:

```json
{
  "detail": "Invalid or expired token"
}
```

**Solution**: Call the `/auth/refresh` endpoint to get a new token.

## User Roles

Users have two possible roles:
- `admin`: Administrator role
- `member`: Regular member role (default)

Currently assigned during signup as `member`. Admin role must be set manually in the database.

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Troubleshooting

### Token not working
- Check if token has expired (30 minutes default)
- Verify the `Authorization` header format: `Authorization: Bearer {token}`
- Ensure token is included with every protected request

### "Invalid authentication scheme"
- Make sure header format is: `Authorization: Bearer {token}`
- Common mistake: `Authorization: {token}` (missing "Bearer")

### "User not found"
- Token may be from a deleted user
- Try logging in again to get a new token

### CORS errors
- Configure CORS middleware in production
- Ensure frontend domain is allowed in CORS settings

## Next Steps

1. Use the access token in the `Authorization` header for all protected endpoints
2. Implement token refresh before expiration
3. Store tokens securely on the client side
4. Set up role-based access control (RBAC) if needed
