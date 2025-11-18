import requests
import time


def test_endpoint(url, method="GET", data=None):
    try:
        start_time = time.time()
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        end_time = time.time()

        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Time: {end_time - start_time:.2f}s")
        print(f"Response: {response.text[:200]}")
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
        print("-" * 50)


# Test endpoints
test_endpoint("http://127.0.0.1:8000/")
test_endpoint("http://127.0.0.1:8000/health")
test_endpoint("http://127.0.0.1:8000/test-simple")

test_endpoint(
    "http://127.0.0.1:8000/user_api/apiv2/user-register/initiate/",
    method="POST",
    data={
        "email": "test@example.com",
        "password": "test123",
        "phone_number": "1234567890",
        "reference_through": "INSTAGRAM",
        "accept_privacy_policy": "True",
        "accept_terms_of_service": "True",
        "accept_refund_policy": "True"
    }
)
