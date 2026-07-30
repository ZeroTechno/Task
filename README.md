My first CRUD API

<img width="1440" height="900" alt="Screenshot 2026-07-14 at 2 54 55 PM" src="https://github.com/user-attachments/assets/8cf4e311-5a9c-4cf5-8584-70777b9d6e4e" />
This image is Basically the 5th stage

Aside from the resources given, this is also an additional resource I used that helped me (https://www.youtube.com/watch?v=Lw-zLopB3o0&start=0)

# FastAPI Authentication & Route Protection with Supabase

A secure backend API built with FastAPI and Supabase Auth as the Identity Provider (IdP). This project demonstrates modern web security principles, using JSON Web Tokens (JWT) for user authentication and Bearer Tokens for protected route authorization.

---

## What This Project Is

This API provides user account management (Sign Up, Log In, Log Out) and enforces access control across endpoints. Public endpoints are accessible to anyone, while protected endpoints require a valid JWT issued by Supabase Auth and passed in the HTTP `Authorization: Bearer <token>` header.

Key security features include:
* Identity Provider Integration: Offloads password hashing, user registration, and session token generation to Supabase Auth.
* Token Verification Middleware: Uses FastAPI's dependency injection (`Depends`) to extract and verify JWT tokens against Supabase before serving protected routes.
* Interactive API Security: Configures `HTTPBearer` security schemes in Swagger UI (`/docs`) to test protected endpoints with Bearer tokens directly from the browser.
 
---

## How to Set Up Local Environment Variables

1. Create a `.env` file in the root directory of the project:
   ```bash
   touch .env

2. Open .env and add your Supabase credentials (found in your Supabase Dashboard -> Project Settings -> API):
SUPABASE_URL=[https://your-project-ref.supabase.co](https://your-project-ref.supabase.co)
SUPABASE_KEY=your-actual-anon-key-here

## To run through Project
1. Install the dependencies:
pip3 install fastapi uvicorn supabase python-dotenv pydantic

2. Start the server:
python3 -m uvicorn main:app --reload

3. Access the application
Server URL: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

Endpoint		Method	Auth Required		Description
/health			GET	No			Basic health check route
/public/info		GET	No			Open endpoint returning public information
/auth/signup		POST	No			Registers a new user account with Supabase Auth
/auth/login		POST	No			Authenticates credentials and returns JWT Bearer token
/auth/logout		POST	Yes (Bearer)		Terminates active session and invalidates token
/protected/profile	GET	Yes (Bearer)		Returns authenticated user profile metadata
/protected/dashboard	GET	Yes (Bearer)		Returns protected user dashboard data

![Swagger UI Screenshot1](./swagger-auth-screenshot1.png)
![Swagger UI Screenshot2](./swagger-auth-screenshot2.png)