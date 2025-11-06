"""
    - modification needed
    - add other method to handle payment utils
    - handle payment type properly
"""
import stripe

from adminv2.models import UserActivityLog
from dashboard.models import Payment
from django.conf import settings
import logging
from utils.handle_credit_pricing import get_lead_charges
from utils.logs import user_bulk_upload_activity

# Configure logging (this can be adjusted as per your logging setup)
logger = logging.getLogger(__name__)


def ChargeUser(customer_id, charge_amount,payment_descriptions='Not Found'):
    try:
        decimal_int = charge_amount * 100
        final_amount = int(decimal_int)
        decimal_charge_amt = final_amount
        charge = stripe.Charge.create(
            amount=decimal_charge_amt,
            currency="usd",
            customer=customer_id,
            description=payment_descriptions
        )   
        return charge
    except Exception as e:
        error_message = f"Stripe Charge Error: {str(e)}"
        logger.error(error_message)  # Log the error
        print(error_message)
        return None


def ChargeUserInTestMode(customer_id, charge_amount, payment_descriptions):
    """
    Simulate a test mode charge.
    """
    try:
        decimal_int = charge_amount * 100
        final_amount = int(decimal_int)
        decimal_charge_amt = final_amount
        charge = stripe.Charge.create(
            amount=decimal_charge_amt,
            currency="usd",
            customer=customer_id,
            description=payment_descriptions
        )
        return charge
    except Exception as e:
        return None


def triggerAutoTopUp(profile):
    if profile.stripe_customer_id and profile.auto_topup:
        try:
            user_credits = int(profile.credits)
            auto_topup_amount = int(profile.auto_topup_amount)
            auto_topup_credits = int(profile.auto_topup_credits)
            # print(user_credits, auto_topup_amount, auto_topup_credits)
            if auto_topup_credits > user_credits:
                quantity = auto_topup_amount
                if quantity >= 200:
                    charge_credits = get_lead_charges('per_lead_charges_bulk',profile.user.id)
                    # new_total_credits = int(quantity/settings.PER_LEAD_CHARGE_BULK)
                    new_total_credits = int(quantity/charge_credits)
                else:
                    charge_credits = get_lead_charges('per_lead_charges',profile.user.id)
                    # new_total_credits = int(quantity/settings.PER_LEAD_CHARGE)
                    new_total_credits = int(quantity/charge_credits)

                total_credits = user_credits + new_total_credits
                payment_descriptions = f"Auto recharge of ${auto_topup_amount} done due to low credits {user_credits}, earned credits is {new_total_credits} and total credits {total_credits} "
                charge = ChargeUser(customer_id=profile.stripe_customer_id, charge_amount=quantity,payment_descriptions=payment_descriptions)
                # charge = {'id':'testid12334456'} #for debugging purpose or testing
                if charge:
                    Payment.objects.create(user = profile.user, 
                                    stripe_charge_id = charge['id'], 
                                    amount = quantity,
                                    is_autotop = True,
                                    earned_credits = new_total_credits,
                                    payment_through = Payment.PaymentThrough.AUTO_TOPUP
                                    )
                    profile.credits += new_total_credits
                    profile.save()
                    current_credits = profile.credits
                    user_bulk_upload_activity(
                        user=profile.user,
                        description=f"Credits updated after payment of ${auto_topup_amount}",
                        actions=UserActivityLog.ActionType.API,
                        amount=auto_topup_amount,
                        prev_credits=user_credits,
                        remaining_credits=current_credits,
                        earned_credits=new_total_credits
                    )

            return True
        except: 
            pass
    
    if profile.stripe_customer_id and profile.auto_topup:
        try:
            user_credits = int(profile.credits)
            auto_topup_amount = int(profile.auto_topup_amount)
            auto_topup_credits = int(profile.auto_topup_credits)
            # print(user_credits, auto_topup_amount, auto_topup_credits)
            if auto_topup_credits > user_credits:
                quantity = auto_topup_amount
                if quantity >= 200:
                    charge_credits = get_lead_charges('per_lead_charges_bulk',profile.user.id)
                    # new_total_credits = int(quantity/settings.PER_LEAD_CHARGE_BULK)
                    new_total_credits = int(quantity/charge_credits)
                else:
                    charge_credits = get_lead_charges('per_lead_charges',profile.user.id)
                    # new_total_credits = int(quantity/settings.PER_LEAD_CHARGE)
                    new_total_credits = int(quantity/charge_credits)

                total_credits = user_credits + new_total_credits
                payment_descriptions = f"Auto recharge of ${auto_topup_amount} done due to low credits {user_credits}, earned credits is {new_total_credits} and total credits {total_credits} "

                charge = ChargeUser(customer_id=profile.stripe_customer_id, charge_amount=quantity,payment_descriptions=payment_descriptions)
                # charge = {'id':'testid12334456'} #for debugging purpose or testing
                if charge:
                    Payment.objects.create(user = profile.user, 
                                    stripe_charge_id = charge['id'], 
                                    amount = quantity,
                                    is_autotop = True,
                                    earned_credits = new_total_credits,
                                    payment_through = Payment.PaymentThrough.AUTO_TOPUP
                                    )
                    profile.credits += new_total_credits
                    profile.save()
            return True
        except: 
            pass
    return None
    
    # return None







def create_payment_intent(
    customer_id,
    amount,
    description="",
    metadata=None,
    currency="usd",
    payment_method=None,
    confirm=True,
    off_session=True,
):
    """
    Create a Stripe PaymentIntent for pre-authorizing user payments.

    Args:
        customer_id (str): Stripe customer ID.
        amount (int): Amount in USD dollars (e.g., 50 for $50).
        description (str): Payment description for internal tracking.
        metadata (dict): Metadata for tracking user_id, plan_id, etc.
        currency (str): Currency, default 'usd'.

    Returns:
        dict: PaymentIntent object with 'id' and 'client_secret'.
    """
    try:
        # Convert to cents
        amount_cents = int(amount * 100)

        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            customer=customer_id,
            description=description,
            metadata=metadata or {},
            payment_method=payment_method,
            off_session=off_session,
            confirm=confirm,
            automatic_payment_methods={"enabled": True},
        )

        return payment_intent

    except stripe.error.StripeError as e:
        print(f"[StripeError] {str(e)}")
        raise Exception("An error occurred while creating the payment intent. Please try again.")
