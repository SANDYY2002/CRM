# CRM — Local Setup Guide

This guide gets the CRM running on a Windows PC with Django, React, and MySQL.

## Requirements

Install Git, Python 3.12+, Node.js 20+, MySQL 8+, and optionally Redis.

Verify:

```powershell
git --version
python --version
node --version
npm --version
mysql --version
```

## Clone

```powershell
git clone https://github.com/SANDYY2002/CRM.git
cd CRM
```

## MySQL

Create a database and user:

```sql
CREATE DATABASE crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'crm_user'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT ALL PRIVILEGES ON crm.* TO 'crm_user'@'localhost';
FLUSH PRIVILEGES;
```

You may use an existing MySQL account instead.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env`:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=crm
DB_USER=crm_user
DB_PASSWORD=change_this_password
DB_HOST=127.0.0.1
DB_PORT=3306
CORS_ALLOWED_ORIGINS=http://localhost:5173
REDIS_URL=redis://127.0.0.1:6379/0
```

Then:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend: `http://127.0.0.1:8000`

Admin: `http://127.0.0.1:8000/admin/`

Health check: `http://127.0.0.1:8000/api/health/`

## Frontend

Open a second PowerShell window:

```powershell
cd CRM\frontend
npm install
Copy-Item .env.example .env
```

Set:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Start:

```powershell
npm run dev
```

Open `http://localhost:5173`.

## Authentication

The first screen lets you register a CRM workspace and owner account. JWT tokens are used for protected API calls and the dashboard restores the authenticated session.

## Useful commands

Backend:

```powershell
cd CRM\backend
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py test
python manage.py makemigrations
python manage.py migrate
```

Frontend:

```powershell
cd CRM\frontend
npm install
npm run dev
npm run build
```

## Redis / Celery

Redis is not required for the basic login/dashboard flow. It will be required for background jobs, automation, social webhooks, and message processing.

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

## Social integrations

Do not place Facebook, Instagram, WhatsApp, Viber, YouTube, or other API secrets in source code. They will be configured through environment variables and protected channel credentials.

Real social credentials are **not required yet** for local CRM development.

## Windows PowerShell

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Daily development

Terminal 1:

```powershell
cd CRM\backend
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

Terminal 2:

```powershell
cd CRM\frontend
npm run dev
```

Keep `.env` files out of Git. Commit only `.env.example` files.

## Project layout

```text
CRM/
├── backend/
│   ├── apps/
│   ├── config/
│   ├── manage.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env
├── SETUP.md
└── README.md
```

## Development roadmap

1. Database migrations
2. Customers UI
3. Lead Kanban UI
4. Unified Inbox UI
5. Realtime messages
6. Channel connection management
7. Facebook / Instagram
8. WhatsApp
9. Viber
10. YouTube
11. Automation
12. Analytics
13. AI assistance
