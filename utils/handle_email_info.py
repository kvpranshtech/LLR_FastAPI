import requests
import logging
from django.conf import settings
# Configure logging
email_logger = logging.getLogger("EmailValidation")


def API_EmailValidation(email):
    """
    Validate email using the email validation API.

    Args:
        email (str): The email address to validate.

    Returns:
        dict: Parsed results from the email validation API.
    """
    # Base URL of the email validation API
    # url = f"{settings.SITE_DOMAIN_LINK}/api/validate-email/"
    url = f"{settings.SITE_DOMAIN_LINK}/api/validate-bulk-email/"

    # Payload and headers
    payload = {"email": email}
    headers = {
        "Content-Type": "application/json",
        # Add a valid CSRF token if required
    }

    returnDict = {
        "email": email,
        "results": {
            "email_format": "invalid",
            "mx_record": "unavailable",
            "domain_exists": False,
            "disposable_email": False,
            "role_account": False,
            "common_typo": False,
            "spf_record": False,
            "dkim_record": False,
            "dmarc_record": False,
            "new_domain": False,
            "valid_tld": False,
            "spam": False,
            "is_free_domain": False,
        },
    }

    try:
        # Make the request
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        # Parse the response
        if response.status_code == 200:
            data = response.json()
            email_logger.info(f"Response for {email}: {data}")

            # Extract results if available
            results = data.get("results", {})
            returnDict["results"].update(results)
        else:
            # pass
            email_logger.error(f"Failed to validate email {email}: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        email_logger.error(f"Request error during email validation for {email}: {str(e)}")

    return returnDict
