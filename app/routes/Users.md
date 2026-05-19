# User API Reference

Base path: `/api/users/`

---

## Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/users/` | Get current user details | Required |
| `POST` | `/api/users/register/` | Register a new user | No |
| `POST` | `/api/users/login/` | Log in a user | No |
| `POST` | `/api/users/logout/` | Log out a user | Required |

---

## GET `/api/users/`
### Show Current User

Returns details of the currently authenticated user.

**Auth required:** Yes

#### Success — `200 OK`

```json
{
  "username": "John"
}
```

---

## POST `/api/users/register/`
### Register New User

Registers a new user. Intended for first-time application setup.

**Auth required:** No

#### Success — `201 Created`

```json
{
  "message": "Account created successfully"
}
```

#### Errors — `400 Bad Request`

| Scenario | Response |
|----------|----------|
| Missing username or password | `{ "error": "Missing username or password" }` |
| Account already exists | `{ "error": "Account already created" }` |
| Password too short | `{ "error": "Password must be at least 8 characters" }` |
| Passwords don't match | `{ "error": "Please retype your password" }` |

---

## POST `/api/users/login/`
### Login User

Authenticates a user and starts a session.

**Auth required:** No

#### Success — `200 OK`

```json
{
  "message": "Login successful",
  "username": "John",
  "id": 1
}
```

#### Error — `401 Unauthorized`

```json
{
  "error": "Invalid credentials"
}
```

---

## POST `/api/users/logout/`
### Logout User

Ends the current user's session.

**Auth required:** Yes

#### Success — `200 OK`

```json
{
  "message": "Logged out"
}
```