# CRM — Complete Local Setup Guide

This guide gets the CRM running locally on Windows with Django, React, MySQL, Redis, realtime messaging, and the first real YouTube integration.

The application is built around real database/provider data. A fresh workspace is expected to be empty; it does not require seeded customers or fake conversations.

## 1. Architecture

```text
Browser
  │
  ├── React + TypeScript + Vite
  │
  │ HTTP / WebSocket
  ▼
Django + Django REST Framework + Channels
  │
  ├── Auth / JWT
  ├── CRM APIs
  ├── Webhooks
  ├── Provider integrations
  └── Realtime events
  │
  ├──────────────┐
  ▼              ▼
MySQL          Redis
                │
                └── Channels / background jobs
```

## 2. Required software

Install:

| Software | Recommended | Purpose |
|---|---:|---|
| Git | Current | Source control |
| Python | 3.12+ | Django backend |
| Node.js | 20+ LTS | React frontend |
| npm | Comes with Node | Frontend packages |
| MySQL | 8.x | Primary database |
| Redis | Current | WebSockets/background jobs |

Verify:

```powershell
git --version
python --version
node --version
npm --version
mysql --version
redis-server --version
```

If `redis-server` is not available natively on Windows, use WSL2/Docker or another supported Redis distribution.

## 3. Clone the repository

```powershell
git clone https://github.com/SANDYY2002/CRM.git
cd CRM
git status
git branch
```

## 4. Create the MySQL database

Open MySQL:

```powershell
mysql -u root -p
```

Run:

```sql
CREATE DATABASE crm
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'crm_user'@'localhost'
  IDENTIFIED BY 'change_this_password';

GRANT ALL PRIVILEGES ON crm.* TO 'crm_user'@'localhost';
FLUSH PRIVILEGES;
```

Verify:

```sql
SHOW DATABASES;
```

You may use an existing MySQL user instead. Exit with:

```sql
EXIT;
```

## 5. Backend virtual environment

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 6. Backend environment variables

Create the environment file:

```powershell
Copy-Item .env.example .env
```

Edit `backend/.env`:

```env
DJANGO_SECRET_KEY=replace-this-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173

DB_NAME=crm
DB_USER=crm_user
DB_PASSWORD=change_this_password
DB_HOST=127.0.0.1
DB_PORT=3306

REDIS_URL=redis://127.0.0.1:6379/0

# Google / YouTube OAuth
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/youtube/oauth/callback/
```

Never commit the real `.env`. Keep client secrets server-side; Google recommends keeping OAuth client secrets outside publicly accessible source repositories. citeturn101676search5

## 7. Django checks and migrations

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

When models change during development:

```powershell
python manage.py makemigrations
python manage.py migrate
```

## 8. Create an admin user

```powershell
python manage.py createsuperuser
```

Django admin:

```text
http://127.0.0.1:8000/admin/
```

The normal CRM login/register UI is separate from Django admin.

## 9. Start Redis

Start Redis:

```powershell
redis-server
```

Verify from another terminal:

```powershell
redis-cli ping
```

Expected:

```text
PONG
```

## 10. Start Django

Terminal 1:

```powershell
cd CRM\backend
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
```

Backend:

```text
http://127.0.0.1:8000
```

Health:

```text
http://127.0.0.1:8000/api/health/
```

## 11. Start React

Terminal 2:

```powershell
cd CRM\frontend
npm install
Copy-Item .env.example .env
```

Set:

```env
VITE_API_URL=http://127.0.0.1:8000/api
VITE_WS_URL=ws://127.0.0.1:8000
```

Start:

```powershell
npm run dev
```

Open:

```text
http://localhost:5173
```

## 12. First-run flow

```text
1. Start MySQL
2. Start Redis
3. Start Django
4. Start React
5. Open http://localhost:5173
6. Register a CRM workspace
7. Log in
8. Create real customers/leads as required
9. Connect a real channel
10. Receive/send real data
```

An empty first-run workspace is expected.

## 13. Authentication

The CRM uses JWT authentication for protected APIs.

Endpoints:

```text
POST /api/auth/register/
POST /api/auth/login/
GET  /api/auth/me/
```

The first workspace member created through registration becomes the workspace owner.

## 14. Organization isolation

CRM records are organization-scoped. Requests use an authenticated user plus organization context.

Frontend requests send:

```http
X-Organization-ID: <organization-id>
```

Do not manually use another organization's ID.

## 15. Realtime inbox

The Unified Inbox uses Django Channels and Redis.

```env
VITE_WS_URL=ws://127.0.0.1:8000
```

Expected event flow:

```text
Provider webhook
    ↓
Django integration
    ↓
Customer / Conversation / Message
    ↓
MySQL
    ↓
Redis channel layer
    ↓
WebSocket
    ↓
Connected CRM agents
```

REST APIs continue to work when WebSockets are unavailable, but live updates will not.

# 16. YouTube integration

The CRM supports connecting a real YouTube channel and uploading actual video files from the CRM.

YouTube private-account operations require OAuth 2.0. The `youtube.upload` scope is used for managing video uploads. citeturn101676search1turn101676search6

### 16.1 Create a Google Cloud project

Open:

```text
https://console.cloud.google.com/
```

Create/select a project and enable:

```text
YouTube Data API v3
```

Google requires the API to be enabled before the application can call it. citeturn101676search1

### 16.2 Configure the OAuth consent screen

Configure the Google OAuth consent screen and add your Google account as a test user when the app is in testing mode.

### 16.3 Create OAuth credentials

Create:

```text
OAuth Client ID
Application type: Web application
```

Add this authorized redirect URI for local Django:

```text
http://127.0.0.1:8000/api/youtube/oauth/callback/
```

If the implementation uses `localhost` instead of `127.0.0.1`, register the exact URI used by the application. Google requires an exact redirect URI match. citeturn101676search0turn101676search1

Set in `backend/.env`:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/youtube/oauth/callback/
```

### 16.4 Keep Google secrets on Django

Do not create a React variable such as:

```text
VITE_GOOGLE_CLIENT_SECRET
```

The Google client secret must remain server-side. citeturn101676search5

### 16.5 Connect the channel

Restart Django after changing `.env`:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Use the CRM's YouTube connection UI.

The intended flow is:

```text
CRM
 ↓
Connect YouTube
 ↓
Google consent
 ↓
Django OAuth callback
 ↓
Authorization code exchange
 ↓
Server-side token storage
 ↓
Connected channel
```

### 16.6 Upload a real video

The YouTube Data API supports `videos.insert` to upload a real video and set metadata such as title, description, tags and privacy status. citeturn101676search2turn101676search3

Typical CRM upload fields:

```text
Video file
Title
Description
Tags
Category
Privacy
```

For the first test, use:

```text
Privacy: Private
```

Then verify the video exists on the real YouTube channel before testing Unlisted/Public.

## 17. Viber

The CRM includes a Viber adapter structure for real provider messaging. Store the Viber authentication token only on the server side.

For local webhook testing, the provider must be able to reach your Django server over HTTPS. Use a secure development tunnel rather than exposing random inbound firewall ports.

## 18. Facebook / Instagram / WhatsApp

These require Meta developer setup, business assets and the permissions appropriate to each integration.

For local webhook testing, provider servers cannot reach `127.0.0.1` directly. Use an HTTPS development tunnel or a public development deployment.

Each connection should be represented by a CRM Channel belonging to the current organization.

## 19. Public webhook testing

For provider webhooks during local development:

```text
Provider
   ↓ HTTPS
Public development tunnel
   ↓
127.0.0.1:8000
   ↓
Django webhook
```

Use this for development only. Production should use a real HTTPS deployment/reverse proxy.

## 20. Backend tests

```powershell
cd CRM\backend
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
```

## 21. Frontend tests/build

```powershell
cd CRM\frontend
npm run build
```

Development:

```powershell
npm run dev
```

Fix build/type errors before adding new provider integrations.

## 22. Recommended daily workflow

### Terminal 1 — Redis

```powershell
redis-server
```

### Terminal 2 — Django

```powershell
cd CRM\backend
.\.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
```

### Terminal 3 — React

```powershell
cd CRM\frontend
npm run dev
```

## 23. Common Windows issues

### PowerShell blocks activation

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

### MySQL is not recognized

Add the MySQL `bin` directory to Windows PATH or launch the MySQL client from its installation directory.

### `mysqlclient` fails to install

Check the exact compiler/client-library error and ensure your Python architecture matches the installed environment before changing dependencies.

### Port 8000 is in use

```powershell
netstat -ano | findstr :8000
```

Or:

```powershell
python manage.py runserver 127.0.0.1:8001
```

Then update:

```env
VITE_API_URL=http://127.0.0.1:8001/api
VITE_WS_URL=ws://127.0.0.1:8001
```

### Port 5173 is in use

Vite may choose another port. Update `CORS_ALLOWED_ORIGINS` to the actual frontend origin.

### MySQL connection refused

```powershell
netstat -ano | findstr :3306
```

Verify:

```env
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

### Redis connection refused

```powershell
redis-cli ping
```

Expected:

```text
PONG
```

### CORS error

Use the exact frontend origin:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

If Vite uses another port, use that port.

### YouTube `redirect_uri_mismatch`

Check every character in the registered Google redirect URI against `GOOGLE_REDIRECT_URI`:

- scheme
- host
- port
- path
- trailing slash

Google requires an exact match. citeturn101676search0turn101676search1

### YouTube OAuth consent error

Verify:

1. YouTube Data API v3 is enabled.
2. OAuth client type is Web application.
3. Redirect URI is registered exactly.
4. Your Google account is a test user when required.
5. The requested YouTube scope is available to the OAuth application.

## 24. Environment files

Backend:

```text
CRM/backend/.env
```

Frontend:

```text
CRM/frontend/.env
```

Never commit:

```text
.env
client_secret.json
*.pem
*.key
```

Only templates such as `.env.example` belong in Git.

## 25. First-run checklist

```text
[ ] Git installed
[ ] Python installed
[ ] Node installed
[ ] MySQL running
[ ] Redis running
[ ] Repository cloned
[ ] Backend virtual environment created
[ ] Backend dependencies installed
[ ] backend/.env created
[ ] MySQL database created
[ ] Django migrations applied
[ ] Django superuser created
[ ] Django server running
[ ] Frontend dependencies installed
[ ] frontend/.env created
[ ] React running
[ ] CRM opens in browser
[ ] Registration works
[ ] Login works
[ ] Dashboard loads real database metrics
[ ] No fake records are required
[ ] WebSocket connection works
[ ] Google Cloud project created
[ ] YouTube Data API enabled
[ ] YouTube OAuth client created
[ ] Redirect URI configured
[ ] YouTube connection works
[ ] Private test video upload works
```

## 26. Useful URLs

CRM:

```text
http://localhost:5173
```

Django API:

```text
http://127.0.0.1:8000/api/
```

Django admin:

```text
http://127.0.0.1:8000/admin/
```

Health:

```text
http://127.0.0.1:8000/api/health/
```

## 27. Project structure

```text
CRM/
├── backend/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── organizations/
│   │   ├── customers/
│   │   ├── leads/
│   │   ├── conversations/
│   │   ├── channels/
│   │   └── integrations/
│   ├── config/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   └── store/
│   ├── package.json
│   ├── .env.example
│   └── .env
├── README.md
└── SETUP.md
```

## 28. Development rules

1. No fake customer/message data. Empty states are preferred to invented records.
2. No provider credentials in React. Secrets remain server-side.
3. Every provider connection is organization-scoped.
4. External webhook events are normalized into the CRM message model.
5. Test database/API behavior before visual polish.
6. OAuth callbacks remain server-side.
7. Use private YouTube uploads for the first integration test.
8. Never commit `.env` or Google client-secret files.

## 29. Development roadmap

```text
1. Local environment
2. Authentication / organizations
3. Real MySQL CRM data
4. Customers / leads
5. Unified Inbox
6. Redis + WebSockets
7. Channel connection management
8. Facebook / Instagram
9. WhatsApp
10. Viber
11. YouTube channel management
12. YouTube video upload / editing
13. Campaigns
14. Automation
15. Analytics
16. AI assistance
17. Production deployment
```

The application should remain usable at every stage without requiring demo records.
