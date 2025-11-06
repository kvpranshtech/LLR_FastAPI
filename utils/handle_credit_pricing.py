from adminv2.models import Credit_Pricing
from django.conf import settings


def get_lead_charges(credit_type, user_id):
    from dashboard.models import UserProfile
    from core.models import StripeSubscriptions
    try:
        credits_per_lead_charge = Credit_Pricing.objects.first()
        if credit_type == 'per_lead_charges':
            if get_users_current_subscriptions_status(user_id):
                try:
                    up = UserProfile.objects.get(user_id=user_id)
                    stripe_subscription = StripeSubscriptions.objects.get(price_id=up.active_subscription_price_id)
                    return stripe_subscription.nm_credit_price
                except Exception as e:
                    print(f"Error getting stripe subscription: {e}")
                    return credits_per_lead_charge.PER_LEAD_CHARGE
            return credits_per_lead_charge.PER_LEAD_CHARGE

        elif credit_type == 'per_lead_charges_bulk':
            return getattr(credits_per_lead_charge, 'PER_LEAD_CHARGE_BULK', settings.PER_LEAD_CHARGE_BULK)

        elif credit_type == 'endato_per_lead_charges':
            return getattr(credits_per_lead_charge, 'ENDATO_PER_LEAD_CHARGE', settings.ENDATO_PER_LEAD_CHARGE)

        elif credit_type == 'email_per_lead_charges':
            return getattr(credits_per_lead_charge, 'EMAIL_PER_LEAD_CHARGE', settings.EMAIL_PER_LEAD_CHARGE)

    except Exception as e:
        print(f"Error in get_lead_charges(): {e}")
        return settings.PER_LEAD_CHARGE  # Fallback default


def get_users_current_subscriptions_status(user_id):
    from dashboard.models import UserProfile
    try:
        if not user_id:
            return False

        up = UserProfile.objects.get(user_id=user_id)

        return all([
            up.stripe_customer_id,
            up.stripe_payment_method_id,
            up.stripe_subscription_id,
            up.active_subscription_price_id,
            up.subscription_status == 'active'
        ])

    except Exception:
        return False
