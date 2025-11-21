"""Create a test user for integration testing"""
import requests

# Register a new user via API
response = requests.post(
    "http://127.0.0.1:8000/api/auth/register",
    json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "npi": "9999999999",
        "role": "provider",
    },
)

print(f"Registration Status: {response.status_code}")
if response.status_code == 201:
    print("User created successfully!")
    data = response.json()
    print(f"Email: {data['email']}")
    print(f"ID: {data['id']}")
else:
    print(f"Error: {response.json()}")

# Try to login
print("\n--- Testing Login ---")
login_response = requests.post(
    "http://127.0.0.1:8000/api/auth/login",
    json={"email": "test@example.com", "password": "TestPass123!"},
)

print(f"Login Status: {login_response.status_code}")
if login_response.status_code == 200:
    print("Login successful!")
    data = login_response.json()
    print(f"Access token received: {data['access_token'][:50]}...")
else:
    print(f"Login failed: {login_response.json()}")
