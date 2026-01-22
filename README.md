# AI SEO Analyst

A FastAPI-based web application that connects to Google Search Console to answer natural language questions about your SEO performance using AI (Llama 3 via OpenRouter).

## Features
- **Google Search Console Integration**: Secure OAuth2 authentication.
- **AI-Powered Insights**: Uses Llama 3 to interpret questions and analyze GSC data.
- **Natural Language Interface**: Ask questions like "Why did my traffic drop last week?" or "What are my top performing queries?".
- **Render Ready**: Configured for easy deployment on Render.com.

## Deployment on Render

This application is ready to be deployed as a Web Service on Render.

1. **Create a New Web Service** on Render connected to this repository.
2. **Environment**: Select `Python 3`.
3. **Build Command**: `pip install -r requirements.txt` (Render default).
4. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT` (or let it use the `Procfile`).

### Environment Variables

You must set the following Environment Variables in your Render Dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLIENT_ID` | OAuth2 Client ID from Google Cloud Console | `12345...apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | OAuth2 Client Secret from Google Cloud Console | `GOCSPX-...` |
| `GOOGLE_REDIRECT_URI` | *Optional*. Allowed Redirect URI. | `https://your-app-name.onrender.com/auth/callback` |
| `APP_BASE_URL` | The URL of your deployed app (No trailing slash) | `https://your-app-name.onrender.com` |
| `OPENROUTER_API_KEY` | API Key for OpenRouter (to access Llama 3) | `sk-or-v1-...` |
| `SESSION_SECRET` | Random string for securing sessions | `complex-random-string-here` |

### Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable **Google Search Console API**.
3. Configure OAuth Consent Screen.
4. Create Credentials (OAuth Client ID - Web Application).
5. Add Authorized Redirect URIs:
   - Local: `http://localhost:8000/auth/callback`
   - Production: `https://your-app-name.onrender.com/auth/callback`

## Local Development

1. Create a `.env` file with the variables above.
2. Run `pip install -r requirements.txt`.
3. Run `python main.py` or `uvicorn main:app --reload`.
4. Open `http://localhost:8000`.
"# Gsc-automation" 
