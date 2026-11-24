# EasyMail frontend

React and Vite client for the EasyMail FastAPI service.

## Run locally

1. Install the frontend dependencies with `npm install`.
2. Configure Google OAuth credentials and the backend redirect URI in the backend environment:
   `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, and `FRONTEND_URL`.
   The Google OAuth redirect URI must match `GOOGLE_REDIRECT_URI` (default:
   `http://localhost:8000/api/v1/auth/callback/google`).
3. Start the FastAPI service on port 8000.
4. Start the frontend with `npm run dev`, then open `http://localhost:3000`.

The client defaults to `http://localhost:8000/api/v1`. Set `VITE_API_BASE_URL` to
override the API base URL for another environment.

## Checks

- `npm run lint`
- `npm run build`
