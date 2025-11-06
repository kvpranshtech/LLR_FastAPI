import stripe
from django.conf import settings
import requests
from dashboard.models import UserProfile
from utils.utils_helpers import get_proxy_settings



def set_stripe_api_key_proxy_server(customer_id=None, user_id=None, key_type="secret"):
    """
    Fetch Stripe API key (secret or publishable) securely via proxy server.
    key_type can be 'secret' or 'publishable'
    """
    try:
        if customer_id:
            user_profile = UserProfile.objects.get(stripe_customer_id=customer_id)
        elif user_id:
            user_profile = UserProfile.objects.get(user_id=user_id)
        else:
            user_profile = None

        mode = "test" if (user_profile and getattr(user_profile, "is_test_user", False)) else "live"
    except UserProfile.DoesNotExist:
        mode = "live"

    proxy_domain, proxy_token, server_ip = get_proxy_settings()
    if not proxy_domain or not proxy_token:
        print("❌ Proxy settings not configured properly.")
        return None


    ALLOWED_LIVE_IPS = ["18.232.36.228"]

    if server_ip not in ALLOWED_LIVE_IPS:
        print("Mode test ----")
        mode = "test"

    try:
        response = requests.post(
            f"{proxy_domain}/stripe-key/",
            headers={
                "X-Server-IP": server_ip,
                "Authorization": f"Bearer {proxy_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"mode": mode, "key_type": key_type},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("stripe_api_key")
    except Exception as e:
        print(f"❌ Proxy fetch failed: {e}")
        return None
