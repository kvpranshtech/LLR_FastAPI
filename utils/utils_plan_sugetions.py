from django.utils.timezone import now

from core.models import Plans, Offers, OfferDetails


def get_bulk_plan_suggestion(required_credits: int, service_type: str, is_reseller: bool = False):
    """
    Suggests a bulk plan that provides at least the required credits.


    Args:
        required_credits (int): Number of credits needed.
        service_type (str): The type of service (e.g. "number", "email").
        is_reseller (bool): Whether to include reseller plans.

    Returns:
        tuple: (bool, Plans instance or "no plan")
    """

    today = now()

    # Get active offers
    offers = Offers.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today)
    offer_mapping = {
        offer_detail.plan.id: offer_detail
        for offer_detail in OfferDetails.objects.filter(offer__in=offers)
    }

    # Fetch plans that match the requirement
    plans = Plans.objects.filter(
        is_reseller=is_reseller,
        service_type=service_type,
        credits__gte=required_credits
    )

    suitable_plans = []
    for plan in plans:
        # Check if this plan has an active offer
        offer_detail = offer_mapping.get(plan.id)
        if offer_detail:
            effective_price = offer_detail.offer_price or plan.discount_price
            effective_credits = offer_detail.offer_credits or plan.credits
        else:
            effective_price = plan.discount_price
            effective_credits = plan.credits

        suitable_plans.append({
            "plan": plan,
            "effective_price": effective_price,
            "effective_credits": effective_credits
        })

    if not suitable_plans:
        return False, "no plan", None, None

    # Sort by effective (lowest) price
    suitable_plans.sort(key=lambda x: x["effective_price"])

    best_plan = suitable_plans[0]
    return True, best_plan["plan"], best_plan["effective_price"], best_plan["effective_credits"]

    # today = now()
    #
    # offers = Offers.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today)
    #
    # plans = Plans.objects.filter(
    #     is_reseller=is_reseller,
    #     service_type=service_type,
    #     credits__gte=required_credits
    # )
    #
    #
    # suitable_plans = [plan for plan in plans if plan.credits >= required_credits]
    #
    #
    # if not suitable_plans:
    #     return False, "no plan"
    #
    # suitable_plans.sort(key=lambda x: x.discount_price)
    #
    # return True, suitable_plans[0]

    #  ----------- v2 ---------------
    # today = now()
    #
    # # Get active offers
    # offers = Offers.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today)
    # offer_mapping = {
    #     offer_detail.plan.id: offer_detail
    #     for offer_detail in OfferDetails.objects.filter(offer__in=offers)
    # }
    #
    # # Fetch plans that match the requirement
    # plans = Plans.objects.filter(
    #     is_reseller=is_reseller,
    #     service_type=service_type,
    #     credits__gte=required_credits
    # )
    #
    # suitable_plans = []
    # for plan in plans:
    #     # Check if this plan has an active offer
    #     offer_detail = offer_mapping.get(plan.id)
    #     effective_price = offer_detail.offer_price if offer_detail else plan.discount_price
    #
    #     suitable_plans.append({
    #         "plan": plan,
    #         "effective_price": effective_price
    #     })
    #
    # if not suitable_plans:
    #     return False, "no plan", None
    #
    # # Sort by effective (lowest) price
    # suitable_plans.sort(key=lambda x: x["effective_price"])
    #
    # best_plan = suitable_plans[0]
    # return True, best_plan["plan"], best_plan["effective_price"]
