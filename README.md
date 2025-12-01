# Mental Health App Backend

This is the backend for the Mental Health App, built with Django, Django REST Framework, Celery, and Django Channels (WebSockets).

## Prerequisites

*   Python 3.10+
*   Redis (for Celery and Channels)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, install the main packages manually: `django djangorestframework celery redis channels daphne django-allauth dj-rest-auth djangorestframework-simplejwt drf-spectacular pillow django-celery-beat`)*

4.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (optional):**
    ```bash
    python manage.py createsuperuser
    ```

## Running the Application

You need to run three separate processes in different terminal windows.

### 1. Redis Server
Ensure Redis is running.
```bash
redis-server
```
*(Check if running with `redis-cli ping` -> `PONG`)*

### 2. Django Server (Daphne)
This runs the main web server and WebSocket handler.
```bash
daphne -p 6001 Mental_health.asgi:application
```
*   HTTP API: `http://127.0.0.1:6001/`
*   WebSocket: `ws://127.0.0.1:6001/`

### 3. Celery Worker
This handles background tasks.
```bash
celery -A Mental_health worker -l info
```

### 4. Celery Beat
This schedules periodic tasks (like daily notifications).
```bash
celery -A Mental_health beat -l info
```

---

## API Endpoints

### Authentication (`/auth/`)
*   `POST /auth/register/` - Register a new user
*   `POST /auth/login/` - Login (returns JWT tokens)
*   `POST /auth/logout/` - Logout
*   `POST /auth/verify-otp/` - Verify email OTP
*   `GET /auth/user/` - Get current user details
*   `PUT /auth/profile/update/` - Update user profile
*   `POST /auth/google/` - Google Social Login
*   `POST /auth/apple/` - Apple Social Login
*   `POST /auth/account-inactive/` - Resend activation OTP (if applicable)

### Daily Checking (`/daily_checking/`)
*   `GET /daily_checking/daily-checking/` - List daily check-ins
*   `POST /daily_checking/daily-checking/` - Create a daily check-in
*   `GET /daily_checking/daily-checking/<id>/` - Retrieve a specific check-in
*   `PUT /daily_checking/daily-checking/<id>/` - Update a check-in
*   `DELETE /daily_checking/daily-checking/<id>/` - Delete a check-in
*   `POST /daily_checking/ai_questions` - Get AI-suggested questions

### Chatbot (`/api/chatbot/`)
*   `GET /api/chatbot/sessions/` - List chat sessions
*   `POST /api/chatbot/sessions/` - Create a new chat session
*   `GET /api/chatbot/sessions/<id>/` - Get chat session details
*   `POST /api/chatbot/sessions/<session_id>/message/` - Send a message to the chatbot

### Reports (`/api/report/`)
*   `GET /api/report/monthly/` - Get monthly mental health report

### Notifications (`/api/notifications/`)
*   `GET /api/notifications/list/` - List all notifications (with unseen count)
*   `GET /api/notifications/list/<id>/` - Mark a specific notification as read

---

## WebSockets

### Notification Stream
Connect to this endpoint to receive real-time notifications.

**URL:**
`ws://127.0.0.1:6001/api/notifications/ws/notifications/?token=<YOUR_ACCESS_TOKEN>`

**Events:**
*   **`notify`**: Sent when a new notification is created.
    *   Payload:
        ```json
        {
            "id": 1,
            "title": "Daily Check-in Notification",
            "data": {},
            "is_read": false,
            "created_at": "2023-10-27T10:00:00Z"
        }
        ```
