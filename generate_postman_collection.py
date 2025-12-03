import json
import uuid

BASE_URL = "{{base_url}}"

def create_item(name, method, url, body=None, tests=None, description=""):
    item = {
        "name": name,
        "request": {
            "method": method,
            "header": [
                {
                    "key": "Content-Type",
                    "value": "application/json",
                    "type": "text"
                },
                {
                    "key": "Authorization",
                    "value": "Bearer {{access_token}}",
                    "type": "text"
                }
            ],
            "url": {
                "raw": f"{BASE_URL}{url}",
                "host": ["{{base_url}}"],
                "path": url.split('/')[1:]
            },
            "description": description
        },
        "event": []
    }

    if body:
        item["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=4)
        }

    if tests:
        item["event"].append({
            "listen": "test",
            "script": {
                "exec": tests,
                "type": "text/javascript"
            }
        })

    return item

def generate_collection():
    collection = {
        "info": {
            "name": "Mental Health App API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "variable": [
            {
                "key": "base_url",
                "value": "http://127.0.0.1:8000",
                "type": "string"
            },
            {
                "key": "access_token",
                "value": "",
                "type": "string"
            },
            {
                "key": "refresh_token",
                "value": "",
                "type": "string"
            }
        ]
    }

    # --- Auth Folder ---
    auth_folder = {"name": "Auth", "item": []}
    
    # Login
    login_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.test('Access token received', function () { pm.expect(jsonData).to.have.property('access'); });",
        "if (jsonData.access) { pm.environment.set('access_token', jsonData.access); }",
        "if (jsonData.refresh) { pm.environment.set('refresh_token', jsonData.refresh); }"
    ]
    # Note: Login endpoint doesn't need Bearer token, so we'll remove it later or override
    login_item = create_item("Login", "POST", "/auth/login/", {
        "email": "test_logout@example.com",
        "password": "password123"
    }, login_tests)
    login_item["request"]["header"] = [{"key": "Content-Type", "value": "application/json", "type": "text"}] # Remove Auth header
    auth_folder["item"].append(login_item)

    # User Profile
    user_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.test('Email matches', function () { pm.expect(jsonData.email).to.eql('test_logout@example.com'); });"
    ]
    auth_folder["item"].append(create_item("Get User Profile", "GET", "/auth/user/", tests=user_tests))

    # Token Refresh
    refresh_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "if (jsonData.access) { pm.environment.set('access_token', jsonData.access); }"
    ]
    refresh_item = create_item("Refresh Token", "POST", "/auth/token/refresh/", {
        "refresh": "{{refresh_token}}"
    }, refresh_tests)
    refresh_item["request"]["header"] = [{"key": "Content-Type", "value": "application/json", "type": "text"}]
    auth_folder["item"].append(refresh_item)

    # Logout
    logout_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });"
    ]
    auth_folder["item"].append(create_item("Logout", "POST", "/auth/logout/", {
        "token": "{{refresh_token}}"
    }, logout_tests))

    collection["item"].append(auth_folder)

    # --- Daily Checking Folder ---
    daily_folder = {"name": "Daily Checking", "item": []}

    # Create Checking
    create_checking_tests = [
        "pm.test('Status code is 201', function () { pm.response.to.have.status(201); });",
        "var jsonData = pm.response.json();",
        "pm.environment.set('checking_id', jsonData.id);"
    ]
    daily_folder["item"].append(create_item("Create Daily Checking", "POST", "/daily_checking/daily-checking/", {
        "feeling": "Happy",
        "sleeping_quality": "Good",
        "note": "Feeling great today!"
    }, create_checking_tests))

    # List Checkings
    list_checking_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.expect(jsonData).to.be.an('array');"
    ]
    daily_folder["item"].append(create_item("List Daily Checkings", "GET", "/daily_checking/daily-checking/", tests=list_checking_tests))

    # AI Questions
    ai_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.expect(jsonData).to.have.property('questions');"
    ]
    daily_folder["item"].append(create_item("Get AI Questions", "POST", "/daily_checking/ai_questions", {
        "feelings": "Anxious"
    }, ai_tests))

    collection["item"].append(daily_folder)

    # --- Chatbot Folder ---
    chatbot_folder = {"name": "Chatbot", "item": []}

    # Create Session
    create_session_tests = [
        "pm.test('Status code is 201', function () { pm.response.to.have.status(201); });",
        "var jsonData = pm.response.json();",
        "pm.environment.set('session_id', jsonData.id);",
        "pm.test('Title matches', function () { pm.expect(jsonData.title).to.eql('My Therapy Session'); });"
    ]
    chatbot_folder["item"].append(create_item("Create Chat Session", "POST", "/api/chatbot/sessions/", {
        "title": "My Therapy Session"
    }, create_session_tests))

    # List Sessions
    list_session_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.expect(jsonData).to.be.an('array');"
    ]
    chatbot_folder["item"].append(create_item("List Chat Sessions", "GET", "/api/chatbot/sessions/", tests=list_session_tests))

    # Get Session Detail
    get_session_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.expect(jsonData.id).to.eql(pm.environment.get('session_id'));"
    ]
    chatbot_folder["item"].append(create_item("Get Chat Session Detail", "GET", "/api/chatbot/sessions/{{session_id}}/", tests=get_session_tests))

    # Send Message
    send_msg_tests = [
        "pm.test('Status code is 201', function () { pm.response.to.have.status(201); });",
        "var jsonData = pm.response.json();",
        "pm.test('Bot response exists', function () { pm.expect(jsonData).to.have.property('bot_response'); });"
    ]
    chatbot_folder["item"].append(create_item("Send Message to Session", "POST", "/api/chatbot/sessions/{{session_id}}/message/", {
        "message": "I am feeling a bit stressed today.",
        "location": "New York, USA"
    }, send_msg_tests))

    # Delete Session
    delete_session_tests = [
        "pm.test('Status code is 204', function () { pm.response.to.have.status(204); });"
    ]
    chatbot_folder["item"].append(create_item("Delete Chat Session", "DELETE", "/api/chatbot/sessions/{{session_id}}/", tests=delete_session_tests))

    collection["item"].append(chatbot_folder)

    # --- Report Folder ---
    report_folder = {"name": "Report", "item": []}

    # Monthly Report
    report_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.test('Contains weeks', function () { pm.expect(jsonData).to.have.property('weeks'); });",
        "pm.test('Week 1 points exist', function () { pm.expect(jsonData.weeks.week_1).to.have.property('points'); });"
    ]
    report_folder["item"].append(create_item("Get Monthly Report", "GET", "/api/report/monthly/?month=11&year=2025", tests=report_tests))

    collection["item"].append(report_folder)

    # --- Notifications Folder ---
    notifications_folder = {"name": "Notifications", "item": []}

    # List Notifications
    list_notif_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
        "var jsonData = pm.response.json();",
        "pm.expect(jsonData).to.have.property('results');"
    ]
    notifications_folder["item"].append(create_item("List Notifications", "GET", "/api/notifications/list/", tests=list_notif_tests))

    # Mark Notification Read
    mark_read_tests = [
        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });"
    ]
    notifications_folder["item"].append(create_item("Mark Notification Read", "GET", "/api/notifications/list/1/", tests=mark_read_tests))

    collection["item"].append(notifications_folder)

    with open('Mental_Health_API.postman_collection.json', 'w') as f:
        json.dump(collection, f, indent=4)

    print("Postman collection generated: Mental_Health_API.postman_collection.json")

if __name__ == "__main__":
    generate_collection()
