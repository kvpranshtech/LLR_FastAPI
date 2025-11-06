from adminv2.models import UserActivityLog , AdminActivityLog


def user_log_activity(user, description, actions):
    try:
        UserActivityLog.objects.create(user=user, actions=actions, description=description)

    except Exception as e:
        print(f"error in log {e}")
        pass


def user_bulk_upload_activity(user, description, actions, amount, prev_credits, remaining_credits, earned_credits):

    print(user)
    print()
    print(description)
    print()
    print(actions)
    print()
    print(amount)
    print()
    print(prev_credits,'PREVVVVVVVV')
    print()
    print(remaining_credits,'REMAINING ....')
    print()
    print(earned_credits)
    
    try:
        UserActivityLog.objects.create(
            user=user,
            description=description,
            actions=actions,
            amount=amount,
            prev_credits=prev_credits,
            remaining_credits=remaining_credits,
            earned_credits=earned_credits
        )
    except Exception as e:
        print(f"Error creating UserActivityLog: {e}")
        raise

def user_bulk_upload_activity_with_subscription(user, description, actions, amount=0, prev_credits=0, remaining_credits = 0, earned_credits=0, subscription_prev_credits=0, subscription_remaining_credits=0, subscription_earned_credits=0, subscription_offer_prev_credits=0, subscription_offer_remaining_credits=0, subscription_offer_earned_credits=0 ):

    print(user)
    print()
    print(description)
    print()
    print(actions)
    print()
    print(amount)
    print()
    print(prev_credits,'PREVVVVVVVV')
    print()
    print(remaining_credits,'REMAINING ....')
    print()
    print(earned_credits)

    print(subscription_prev_credits,'SUBSCRIPTION PREVVVVVVVV')
    print()
    print(subscription_remaining_credits,'SUBSCRIPTION REMAINING ....')
    print()
    print(subscription_earned_credits, "SUBSCRIPTION EARNED")

    print(subscription_offer_prev_credits,'SUBSCRIPTION OFFER PREVVVVVVVV')
    print()
    print(subscription_offer_remaining_credits,'SUBSCRIPTION OFFER REMAINING ....')
    print()
    print(subscription_offer_earned_credits, "SUBSCRIPTION OFFER EARNED")

    try:
        UserActivityLog.objects.create(
            user=user,
            description=description,
            actions=actions,
            amount=amount,
            prev_credits=prev_credits,
            remaining_credits=remaining_credits,
            earned_credits=earned_credits,
            subscription_prev_credits=subscription_prev_credits,
            subscription_remaining_credits=subscription_remaining_credits,
            subscription_earned_credits=subscription_earned_credits,
            subscription_offer_prev_credits=subscription_offer_prev_credits,
            subscription_offer_remaining_credits=subscription_offer_remaining_credits,
            subscription_offer_earned_credits=subscription_offer_earned_credits,
        )
    except Exception as e:
        print(f"Error creating UserActivityLog: {e}")
        raise

    
def user_api_priority_change_activity(user, description, actions):
    try:
        UserActivityLog.objects.create(user=user, description=description, actions=actions)
    except:
        pass

def user_credit_pricing_change_activity(user, action, message):
    try:
        UserActivityLog.objects.create(
            user=user,
            actions=action,
            description=message,
            earned_credits=None,
            prev_credits=None,
            remaining_credits=None,
            amount=None,
        )
    except Exception as e:
        print(f"Error while logging user activity: {e}")

def admin_log_activity(user, actions, description):
    try:
        AdminActivityLog.objects.create(user=user, actions=actions, description=description)
    except Exception as e:
        print(f"error in log {e}")
        pass

def admin_credit_log_activity(user, description, actions, amount, prev_credits, remaining_credits, earned_credits):
    try:
        AdminActivityLog.objects.create(
            user=user,
            actions=actions,
            description=description,
            amount=amount,
            prev_credits=prev_credits,
            remaining_credits=remaining_credits,
            earned_credits=earned_credits
        )
    except Exception as e:
        print(f"Error creating AdminActivityLog: {e}")
        raise

def admin_credit_log_activity_with_subscription(user, description, actions, amount=0, prev_credits=0, remaining_credits = 0, earned_credits=0, subscription_prev_credits=0, subscription_remaining_credits=0, subscription_earned_credits=0 ):

    try:
        AdminActivityLog.objects.create(
            user=user,
            description=description,
            actions=actions,
            amount=amount,
            prev_credits=prev_credits,
            remaining_credits=remaining_credits,
            earned_credits=earned_credits,
            subscription_prev_credits=subscription_prev_credits,
            subscription_remaining_credits=subscription_remaining_credits,
            subscription_earned_credits=subscription_earned_credits,
        )
    except Exception as e:
        print(f"Error creating UserActivityLog: {e}")
        raise

def exhaust_subscription_credit_log(user, actions, description):
    try:
        UserActivityLog.objects.create(
            user=user,
            actions=actions,
            description=description
        )

    except Exception as e:
        print(f"error in log {e}")
        pass
