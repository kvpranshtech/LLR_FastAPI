import stripe
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def set_stripe_api_keys(user_email):
    email_domain = user_email.split('@')[-1]
    print(f'Current User Email Domain - {email_domain} For User {user_email}')
    logger.info(f"Current User Email Domain - {email_domain} For User {user_email}")
    
    # if email_domain == 'pranshtech.com' or email_domain == 'textdrip.com':
    if email_domain == 'pranshtech.com':
        stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY_TEST')
        stripe_publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY_TEST')
        logger.info(f'Test Stripe Publish Key For Domain {email_domain}')
    else:
        stripe_secret_key = settings.STRIPE_SECRET_KEY
        stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
        logger.info(f'Live Stripe Publish Key For Domain {email_domain} - For User {user_email}')

    stripe.api_key = stripe_secret_key
    
    return stripe_publishable_key, stripe_secret_key
