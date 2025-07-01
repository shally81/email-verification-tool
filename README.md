# Email Verifier (Single & Bulk)

Simple email verification tool built with **Node.js + Express** for backend and **HTML/CSS/JS** for frontend.

## Features

- ✅ Single email verification (regex-based for now).
- ✅ Bulk email verification via CSV upload.
- ✅ Downloadable CSV results.
- ✅ Modern responsive UI.
- ✅ Render.com ready (includes *Procfile*).

## Local Setup

```bash
npm install
npm start
# Open http://localhost:3000
```

## Deploy on Render

1. Push this code to GitHub.
2. Create new **Web Service** on Render → Connect repository.
3. Set **Environment**:
   - `NODE_VERSION` = `20`
4. Render auto-detects `start` script (`npm start`).
5. Click **Deploy**.

> **Note**: Currently uses *regex-only* validation (dummy). Swap `verifyEmailLocal` with real API logic once you have a key.

## CSV Format

First column must contain the email (header name can be `email` or anything).

```csv
email
test@example.com
hello@domain.org
```

Enjoy! ✉️
