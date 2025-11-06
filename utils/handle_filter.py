from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Q, Case, When, Count
from allauth.account.models import *
from dashboard.models import *
from api.models import *
from contact.models import *
from core.models import *
from datastorage.models import *
from filecleaner.models import *
from site_settings.models import *
from datastorage.models import *
from core.models import *
from adminv2.models import *

UserModel = get_user_model()
User = get_user_model()

from django_filters import rest_framework as filters
import django_filters
from django_filters.filters import OrderingFilter
from datetime import date
from dateutil.relativedelta import relativedelta


class DateFilter(django_filters.FilterSet):
    DATE_FIELD_OPTIONS = ('date_joined', 'created_at', 'timestamp', 'uploaded_at', 'created', 'verification_date', 'start_date', 'validation_date', 'joined_date','completed_at')

    start_date = django_filters.DateFilter(method='filter_start_date')
    end_date = django_filters.DateFilter(method='filter_end_date')
    today = django_filters.BooleanFilter(method='filter_today')
    yesterday = django_filters.BooleanFilter(method='filter_yesterday')
    last_7_days = django_filters.BooleanFilter(method='filter_last_7_days')
    last_10_days = django_filters.BooleanFilter(method='filter_last_10_days')
    last_15_days = django_filters.BooleanFilter(method='filter_last_15_days')
    last_30_days = django_filters.BooleanFilter(method='filter_last_30_days')
    last_45_days = django_filters.BooleanFilter(method='filter_last_45_days')
    last_60_days = django_filters.BooleanFilter(method='filter_last_60_days')
    last_90_days = django_filters.BooleanFilter(method='filter_last_90_days')

    this_month = django_filters.BooleanFilter(method='filter_this_month')
    last_month = django_filters.BooleanFilter(method='filter_last_month')
    two_months_before = django_filters.BooleanFilter(method='filter_2_months_before')
    three_months_before = django_filters.BooleanFilter(method='filter_3_months_before')
    four_months_before = django_filters.BooleanFilter(method='filter_4_months_before')
    five_months_before = django_filters.BooleanFilter(method='filter_5_months_before')

    class Meta:
        model = CsvFileInfo  # Ensure this is correctly set!
        fields = ["start_date", "end_date", "today"]  # Define filterable fields if needed

    def __init__(self, *args, **kwargs):
        self.date_field_name = next(
            (field_name for field_name in self.DATE_FIELD_OPTIONS if any(
                field.name == field_name for field in self._meta.model._meta.get_fields()
            )),
            'date_field'
        )
        super().__init__(*args, **kwargs)

        self.filters['joined_date_ordering'] = OrderingFilter(
            fields=((self.date_field_name, self.date_field_name)),
            label=f'{self.date_field_name} (ascending/descending)',
            choices=[
                (self.date_field_name, 'Ascending'),
                (f'-{self.date_field_name}', 'Descending')
            ]
        )

    def filter_start_date(self, queryset, name, value):
        if value:
            return queryset.filter(**{f"{self.date_field_name}__gte": value})
        return queryset

    def filter_end_date(self, queryset, name, value):
        if value:
            return queryset.filter(**{f"{self.date_field_name}__lte": value + timedelta(days=1)})
        return queryset

    def filter_today(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(**{f"{self.date_field_name}__date": today})
        return queryset

    def filter_yesterday(self, queryset, name, value):
        if value:
            yesterday = timezone.now().date() - timezone.timedelta(days=1)
            return queryset.filter(**{f"{self.date_field_name}__date": yesterday})
        return queryset

    def filter_last_7_days(self, queryset, name, value):
        if value:
            last_7_days = timezone.now().date() - timezone.timedelta(days=7)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_7_days})
        return queryset

    def filter_last_10_days(self, queryset, name, value):
        if value:
            last_10_days = timezone.now().date() - timezone.timedelta(days=10)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_10_days})
        return queryset

    def filter_last_15_days(self, queryset, name, value):
        if value:
            last_15_days = timezone.now().date() - timezone.timedelta(days=15)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_15_days})
        return queryset

    def filter_last_30_days(self, queryset, name, value):
        if value:
            last_30_days = timezone.now().date() - timezone.timedelta(days=30)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_30_days})
        return queryset

    def filter_last_45_days(self, queryset, name, value):
        if value:
            last_45_days = timezone.now().date() - timezone.timedelta(days=45)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_45_days})
        return queryset

    def filter_last_60_days(self, queryset, name, value):
        if value:
            last_60_days = timezone.now().date() - timezone.timedelta(days=60)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_60_days})
        return queryset

    def filter_last_90_days(self, queryset, name, value):
        if value:
            last_90_days = timezone.now().date() - timezone.timedelta(days=90)
            return queryset.filter(**{f"{self.date_field_name}__gte": last_90_days})
        return queryset

    def filter_this_month(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            first_day_of_this_month = today.replace(day=1)
            last_day_of_this_month = (
                    first_day_of_this_month.replace(month=today.month + 1, day=1) - timezone.timedelta(
                days=1)) if today.month != 12 else today.replace(month=12, day=31)
            return queryset.filter(
                **{f"{self.date_field_name}__gte": first_day_of_this_month,
                   f"{self.date_field_name}__lte": last_day_of_this_month}
            )
        return queryset

    def filter_last_month(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            first_day_of_last_month = (today.replace(day=1) - timezone.timedelta(days=1)).replace(day=1)
            last_day_of_last_month = today.replace(day=1) - timezone.timedelta(days=1)
            return queryset.filter(
                **{f"{self.date_field_name}__gte": first_day_of_last_month,
                   f"{self.date_field_name}__lte": last_day_of_last_month}
            )
        return queryset

    def filter_months_before(self, queryset, name, value, months_before):
        if value:
            today = timezone.now().date()
            first_day_of_target_month = (today.replace(day=1) - relativedelta(months=months_before)).replace(day=1)
            last_day_of_target_month = (
                    first_day_of_target_month + relativedelta(months=1) - timezone.timedelta(days=1)
            )
            return queryset.filter(
                **{f"{self.date_field_name}__gte": first_day_of_target_month,
                   f"{self.date_field_name}__lte": last_day_of_target_month}
            )
        return queryset

    def filter_2_months_before(self, queryset, name, value):
        return self.filter_months_before(queryset, name, value, 2)

    def filter_3_months_before(self, queryset, name, value):
        return self.filter_months_before(queryset, name, value, 3)

    def filter_4_months_before(self, queryset, name, value):
        return self.filter_months_before(queryset, name, value, 4)

    def filter_5_months_before(self, queryset, name, value):
        return self.filter_months_before(queryset, name, value, 5)

    date_fields = ['start_date', 'end_date', 'today', 'yesterday', 'last_7_days', 'last_10_days', 'last_15_days',
                   'last_30_days', 'last_45_days', 'last_60_days', 'last_90_days', 'this_month', 'last_month',
                   'two_months_before', 'three_months_before', 'four_months_before', 'five_months_before']


# UserList Api
class ItemFilter(DateFilter):
    username = filters.CharFilter(field_name="username", lookup_expr="exact")
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    email = filters.CharFilter(field_name="email", lookup_expr="exact")
    is_staff = filters.BooleanFilter(field_name="is_staff", lookup_expr="exact")
    is_active = filters.BooleanFilter(field_name="is_active", lookup_expr="exact")
    is_superuser = filters.BooleanFilter(field_name="is_superuser", lookup_expr="exact")

    verified = django_filters.BooleanFilter(method='filter_verified')
    account_status = django_filters.CharFilter(field_name="profile__account_status", lookup_expr="exact")
    reseller = django_filters.BooleanFilter(field_name="profile__reseller", lookup_expr="exact")
    min_credits = filters.NumberFilter(field_name='profile__credits', lookup_expr='gte')
    max_credits = filters.NumberFilter(field_name='profile__credits', lookup_expr='lte')

    date_joined = filters.DateFilter(field_name="date_joined", lookup_expr='date')
    last_login = filters.DateFilter(field_name="last_login", lookup_expr='date')
    last_login_ordering = OrderingFilter(
        fields=(('last_login', 'last_login'),),
        label='Last Login (ascending/descending)',
        choices=[('last_login', 'Ascending'), ('-last_login', 'Descending')])

    domain = filters.CharFilter(method='filter_by_domain')

    def filter_verified(self, queryset, name, value):
        return queryset.filter(Q(emailaddress__verified=value) & Q(emailaddress__primary=True))

    def filter_by_domain(self, queryset, name, value):
        return queryset.filter(email__iendswith=f"@{value}")

    # fields = {
    #     'first_name': ['icontains'],
    #     'last_name': ['icontains'],
    #     'username': ['exact'],  #
    #     # 'price': ['lt'],
    #     # Add more fields if necessary
    #     'email': ['exact'],
    #     'is_staff': ['exact'],
    #     'is_active': ['exact'],
    #     'is_superuser': ['exact'],
    #     'date_joined': ['date', 'year'],
    # }

    class Meta:
        model = UserModel
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser',
                  'verified', 'reseller', 'min_credits', 'max_credits', 'date_joined',
                  'last_login', 'last_login_ordering', 'domain'] + DateFilter.date_fields


# UserProfile Api
class UserFilter(DateFilter):
    username = filters.CharFilter(field_name="user__username", lookup_expr="exact")
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    email = filters.CharFilter(field_name="user__email", lookup_expr="exact")
    is_staff = filters.BooleanFilter(field_name="user__is_staff", lookup_expr="exact")
    is_active = filters.BooleanFilter(field_name="user__is_active", lookup_expr="exact")
    is_superuser = filters.BooleanFilter(field_name="user__is_superuser", lookup_expr="exact")
    date_joined = filters.DateFilter(field_name="date_joined",
                                     lookup_expr='date')
    account_status = filters.CharFilter(field_name="account_status", lookup_expr="exact")
    reseller = filters.BooleanFilter(field_name="reseller", lookup_expr="exact")
    auto_topup = filters.BooleanFilter(field_name="auto_topup", lookup_expr="exact")
    verified = filters.BooleanFilter(method="filter_verified")
    email_verified = filters.BooleanFilter(method="filter_verified", lookup_expr="exact")
    phone_verified = filters.BooleanFilter(field_name="otp_verified", lookup_expr="exact")

    min_credits = filters.NumberFilter(field_name='credits', lookup_expr='gte')
    max_credits = filters.NumberFilter(field_name='credits', lookup_expr='lte')

    created_at = filters.DateFilter(field_name='created_at', lookup_expr='date')
    domain = filters.CharFilter(method='filter_by_domain')

    last_login = filters.DateFilter(field_name="user__last_login", lookup_expr='date')
    last_login_ordering = OrderingFilter(
        fields=(('user__last_login', 'user__last_login'),),
        label='Last Login (ascending/descending)',
        choices=[('user__last_login', 'Ascending'), ('-user__last_login', 'Descending')])

    top_7_users = filters.BooleanFilter(method='filter_top_7_users', label="Top 7 Users with Highest Credits")

    # top_7_payment = filters.BooleanFilter(method='filter_top_7_payments', label='Top 7 Users with Highest Payments')
    top_7_Files = filters.BooleanFilter(method='filters_top_7_files', label="Top 7 Users with Highest files Upload")
    permission_group = filters.CharFilter(field_name="user__groups__name", lookup_expr="exact")

    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(user__username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value)
        )


    def filter_verified(self, queryset, name, value):
        return queryset.filter(
            Q(user__emailaddress__verified=value)
        )

    def filter_by_domain(self, queryset, name, value):
        return queryset.filter(user__email__iendswith=f"@{value}")

    def filter_top_7_users(self, queryset, name, value):
        if value:
            return (
                queryset.filter(
                    user__is_staff=False,
                    user__is_superuser=False
                )
                .order_by('-credits')[:7]
            )
        return queryset

    def otp_verified(self, queryset, name, value):
        return queryset.filter(otp_verified=value)

    def filters_top_7_files(self, queryset, name, value):
        if value:  # Only apply the filter if the value is True
            return (
                queryset.annotate(uploaded_files_count=Count('csvfiles'))  # Count related 'csvfiles'
                .order_by('-uploaded_files_count')[:7]  # Order by file count, top 7
            )

        return queryset

    # def filter_top_7_payments(self, queryset, name, value):
    #     if value:  # Apply the filter only if the Boolean is True
    #         top_users = Payment.objects.filter(
    #             user__is_staff=False,
    #             user__is_superuser=False
    #         ).order_by('-amount')[:8].values_list('user_id', flat=True)  # Get top 7 user IDs
    #
    #         preserved_order = Case(
    #             *[When(user_id=user_id, then=index) for index, user_id in enumerate(top_users)]
    #         )
    #
    #         return queryset.filter(user_id__in=top_users).order_by(preserved_order)
    #     return queryset

    class Meta:
        model = UserProfile
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser',
                  'account_status', 'reseller', 'auto_topup', 'min_credits', 'max_credits',
                  'domain', 'last_login', 'last_login_ordering', 'top_7_users', 'top_7_Files',
                  'permission_group', 'phone_verified', 'email_verified'] + DateFilter.date_fields


class CustomerBillingAddressFiltrer(DateFilter):
    CustomerName = filters.CharFilter(field_name='customer_name', lookup_expr='icontains')
    UserEmail = filters.CharFilter(field_name='user__email', lookup_expr='exact')
    states = filters.CharFilter(field_name='customer_state', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(customer_name__icontains=value) |
            Q(user__email__icontains=value) |
            Q(customer_address1__icontains=value) |
            Q(customer_address2__icontains=value)
        )

    class Meta:
        model = CustomerBillingAddress
        fields = ['CustomerName', 'UserEmail', 'states', 'created_at'] + DateFilter.date_fields


class PaymentFilter(DateFilter):
    UserEmail = filters.CharFilter(field_name='user__email', lookup_expr='exact')
    Amount = filters.NumberFilter(field_name='amount', lookup_expr='exact')
    Earned_Credits = filters.NumberFilter(field_name='earned_credits', lookup_expr='exact')
    
    # Add the new combined search filter
    search = filters.CharFilter(method='filter_by_amount_or_credits')

    payment_through = filters.CharFilter(field_name='payment_through', lookup_expr='exact')
    refunded = filters.BooleanFilter(field_name='is_refunded', lookup_expr='exact')
    bonus = filters.BooleanFilter(field_name='is_bonus', lookup_expr='exact')
    autotop = filters.BooleanFilter(field_name="is_autotop", lookup_expr="exact")
    bulk = filters.BooleanFilter(field_name='is_bulk', lookup_expr="exact")
    payment_type = filters.CharFilter(field_name='payment_type', lookup_expr='exact')
    mode = filters.CharFilter(field_name='mode', lookup_expr='exact')
    start_date = filters.DateFilter(field_name='timestamp', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='timestamp', lookup_expr='lte')

    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')
    top_7_payment = filters.BooleanFilter(method='filter_top_7_payments', label='Top 7 Users with Highest Payments')

    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")
    user_id = filters.NumberFilter(field_name='user_id', lookup_expr='exact')


    def filter_by_amount_or_credits(self, queryset, name, value):
        """
        Filter payments by either amount or earned_credits
        """
        try:
            search_value = float(value)
            return queryset.filter(
                Q(amount=search_value) | 
                Q(earned_credits=search_value) |
                Q(user__email=search_value)
            )
        except (ValueError, TypeError):
            return queryset.none()



    def filter_by_code_or_email(self, queryset, name, value):
        try:
            search_value = float(value)
            return queryset.filter(
                Q(amount=search_value) |
                Q(earned_credits=search_value)
            )
        except (ValueError, TypeError):
            return queryset.filter(
                Q(user__email__icontains=value)
            )

    def filter_top_7_payments(self, queryset, name, value):
        if value:
            return (
                queryset.filter()
                .order_by('-amount')[:7]
            )
        return queryset

    class Meta:
        model = Payment
        fields = [
            'UserEmail', 'Amount', 'Earned_Credits', 'payment_through', 
            'refunded', 'bonus', 'autotop', 'bulk', 'payment_type', 
            'mode', 'created_at', 'top_7_payment', 'start_date', 
            'end_date', 'search'
        ] + DateFilter.date_fields


class BulkApiFilter(DateFilter):
    uid = filters.CharFilter(field_name='uid', lookup_expr='exact')
    UserEmail = filters.CharFilter(field_name='user__email', lookup_expr='exact')
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(uid__icontains=value)
        )

    class Meta:
        model = APIBULK
        fields = ['uid', 'UserEmail', 'status', 'created_at'] + DateFilter.date_fields

from django.utils.timezone import make_aware
import pytz
import datetime


class SingleApiFilter(DateFilter):
    # Custom date filters using just YYYY-MM-DD
    start_date = filters.CharFilter(method='filter_start_date')
    end_date = filters.CharFilter(method='filter_end_date')
    # other filters
    userprofile = filters.CharFilter(field_name='userprofile__user__email', lookup_expr='icontains')
    apibulk = filters.CharFilter(field_name='apibulk__id', lookup_expr='exact')
    phonenumber = filters.CharFilter(field_name='phonenumber', lookup_expr='icontains')
    line_type = filters.CharFilter(field_name='line_type', lookup_expr='icontains')
    dnc_type = filters.CharFilter(field_name='dnc_type', lookup_expr='icontains')
    carrier_name = filters.CharFilter(field_name='carrier_name', lookup_expr='icontains')
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    state = filters.CharFilter(field_name='state', lookup_expr='icontains')
    country = filters.CharFilter(field_name='country', lookup_expr='icontains')
    added_through = filters.ChoiceFilter(field_name='added_through', choices=APIData.ADDED_THROUGH.choices)
    is_deleted = filters.BooleanFilter(field_name='is_deleted')
    number_checked_from_db = filters.BooleanFilter(field_name='number_checked_from_db')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(phonenumber__icontains=value) |
            Q(userprofile__user__email__icontains=value)
        )

    def filter_start_date(self, queryset, name, value):
        try:
            start_date = datetime.datetime.strptime(value, '%Y-%m-%d')
            start_date = make_aware(start_date, timezone=pytz.UTC)
            return queryset.filter(timestamp__gte=start_date)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end_date = datetime.datetime.strptime(value, '%Y-%m-%d') + datetime.timedelta(days=1)
            end_date = make_aware(end_date, timezone=pytz.UTC)
            return queryset.filter(timestamp__lt=end_date)
        except Exception:
            return queryset.none()

    class Meta:
        model = APIData
        fields = ['userprofile', 'apibulk', 'phonenumber', 'line_type', 'dnc_type', 'carrier_name', 'city', 'state',
                  'country', 'added_through', 'is_deleted', 'number_checked_from_db', 'search_by'] + DateFilter.date_fields


class EndatoAPIFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    phone_number = filters.CharFilter(field_name="phone_number", lookup_expr="exact")
    added_through = filters.CharFilter(field_name='added_through', lookup_expr='exact')
    is_processed = filters.BooleanFilter(field_name='is_processed_through_endato', lookup_expr='exact')
    endato_invalid = filters.BooleanFilter(field_name='endato_invalid_flag', lookup_expr='exact')

    # Custom date filters using just YYYY-MM-DD
    start_date = filters.CharFilter(method='filter_start_date')
    end_date = filters.CharFilter(method='filter_end_date')

    def filter_start_date(self, queryset, name, value):
        try:
            start = datetime.datetime.strptime(value, "%Y-%m-%d")
            start = make_aware(start, timezone=pytz.UTC)
            return queryset.filter(created_at__gte=start)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end = datetime.datetime.strptime(value, "%Y-%m-%d") + datetime.timedelta(days=1)
            end = make_aware(end, timezone=pytz.UTC)
            return queryset.filter(created_at__lt=end)
        except Exception:
            return queryset.none()

    class Meta:
        model = EndatoApiResponse
        fields = [
            "first_name", "last_name", "phone_number", "added_through",
            "is_processed", "endato_invalid"
        ]


class EmailAPIFilter(filters.FilterSet):
    UserEmail = filters.CharFilter(field_name='userprofile__user__email', lookup_expr='exact')
    added_through = filters.CharFilter(field_name='added_through', lookup_expr='exact')

    # Custom date filters using just YYYY-MM-DD
    start_date = filters.CharFilter(method='filter_start_date')
    end_date = filters.CharFilter(method='filter_end_date')

    def filter_start_date(self, queryset, name, value):
        try:
            start = datetime.datetime.strptime(value, "%Y-%m-%d")
            start = make_aware(start, timezone=pytz.UTC)
            return queryset.filter(timestamp__gte=start)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end = datetime.datetime.strptime(value, "%Y-%m-%d") + datetime.timedelta(days=1)
            end = make_aware(end, timezone=pytz.UTC)
            return queryset.filter(timestamp__lt=end)
        except Exception:
            return queryset.none()

    class Meta:
        model = APIEmailData
        fields = ["UserEmail", "added_through"]


class CsvFileFilter(DateFilter):
    uid = filters.CharFilter(field_name='uid', lookup_expr='exact')
    file_name = filters.CharFilter(field_name='csvfile_name', lookup_expr='exact')
    UserEmail = filters.CharFilter(field_name='user__email', lookup_expr='exact')
    is_completed = filters.BooleanFilter(field_name='is_complete', lookup_expr='exact')
    is_failed = filters.BooleanFilter(field_name='is_failed', lookup_expr='exact')
    is_canceled = filters.BooleanFilter(field_name='is_canceled', lookup_expr='exact')
    min_rows = filters.NumberFilter(field_name='total_rows', lookup_expr='gte')
    max_rows = filters.NumberFilter(field_name='total_rows', lookup_expr='lte')
    created_at = filters.DateFilter(field_name='uploaded_at', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")
    file_status = filters.NumberFilter(method='filter_file_status', label='File Status')
    user_id = filters.NumberFilter(field_name='user__id', lookup_expr='exact')

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(uid__icontains=value) |
            Q(csvfile_name__icontains=value) |
            Q(user__email__icontains=value)
        )


    file_type = filters.ChoiceFilter(
        method='filter_file_type',
        choices=[
            ('1', 'Number Lookup'),
            ('2', 'Data Enrichment Only'),
            ('3', 'Both')
        ]
    )



    def filter_file_status(self, queryset, name, value):
        if value == 1:
            return queryset.filter(is_complete=True)
        elif value == 2:
            return queryset.filter(is_failed=True)
        elif value == 3:
            return queryset.filter(is_complete=False, is_failed=False, is_canceled=False)
        elif value == 4:
            return queryset.filter(is_canceled=True)
        return queryset

    def filter_file_type(self, queryset, name, value):
        if value == '1':  # Number Lookup
            return queryset.filter(
                Q(checkendatoapi__isnull=True)
            ).distinct()
        elif value == '2':  # Data Enrichment Only
            return queryset.filter(
                checkendatoapi__check_with_endato=True,
                checkendatoapi__check_with_endato_only=True
            ).distinct()
        elif value == '3':  # Both
            return queryset.filter(
                checkendatoapi__check_with_endato=True,
                checkendatoapi__check_with_endato_only=False
            ).distinct()
        return queryset

    line_type = filters.ChoiceFilter(
        field_name='csvfile_info__line_type_info__type',
        choices=[
            ('all', 'ALL'),
            ('mob', 'Mobile'),
            ('lan', 'Landline'),
            ('voip', 'Voip'),
            ('toll', 'Toll Free'),
            ('inv', 'Invalid'),
        ]
    )
    dnc_type = filters.ChoiceFilter(
        field_name='csvfile_info__dnc_type_info__type',
        choices=[
            ('all', 'ALL'),
            ('cln', 'Clean'),
            ('dnc', 'DNC'),
            ('lit', 'Litigator'),
            ('inv', 'Invalid'),
        ]
    )

    class Meta:
        model = CsvFile
        fields = ['uid', 'file_name', 'UserEmail', 'is_completed', 'is_failed', 'is_canceled',
                  'min_rows', 'max_rows', 'created_at', 'line_type', 'dnc_type', 'file_type', 'file_status', 'user_id'] + DateFilter.date_fields


class CsvFileCleanerFilter(DateFilter):
    uid = filters.CharFilter(field_name='uid', lookup_expr='exact')
    file_name = filters.CharFilter(field_name='csvfile_name', lookup_expr='exact')
    UserEmail = filters.CharFilter(field_name='user__email', lookup_expr='exact')
    file_status = filters.CharFilter(field_name='status', lookup_expr='exact')
    uploaded_at = filters.DateFilter(field_name='uploaded_at', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")
    user_id = filters.NumberFilter(field_name='user__id', lookup_expr='exact')

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(uid__icontains=value) |
            Q(csvfile_name__icontains=value) |
            Q(user__email__icontains=value)
        )

    class Meta:
        model = CsvFileCleaner
        fields = ['uid', 'file_name', 'UserEmail', 'file_status', 'uploaded_at', 'user_id'] + DateFilter.date_fields


# system-logs
class SystemLogsFilter(DateFilter):
    service_type = filters.CharFilter(field_name='service__service_type', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')

    class Meta:
        model = ServicesStatusLogs
        fields = ['service_type', 'created_at'] + DateFilter.date_fields


# Custom Logs
class CustomSiteLogsFilter(DateFilter):
    log_type = filters.CharFilter(field_name='log_type', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')

    class Meta:
        model = CustomSiteLogs
        fields = ['log_type', 'created_at'] + DateFilter.date_fields


# signalwire logs
class ServicesStatusLogsFilter(DateFilter):
    service_type = filters.CharFilter(field_name='service_type', lookup_expr='exact')
    uid = filters.CharFilter(field_name='uid', lookup_expr='exact')
    title = filters.CharFilter(field_name='title', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='created', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(service_type__icontains=value) |
            Q(uid__icontains=value) |

            Q(title__icontains=value)
        )

    class Meta:
        model = ServicesStatus
        fields = ['service_type', 'uid', 'title', 'created_at'] + DateFilter.date_fields


# databses filter
# Dnctcpa
class DnctcpaFilter(DateFilter):
    numbers = filters.NumberFilter(field_name='number', lookup_expr='exact')
    starts_with = filters.NumberFilter(field_name='number', lookup_expr='startswith')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')
    dnc_type = filters.CharFilter(field_name='dnc_type', lookup_expr='icontains')

    class Meta:
        model = BaseModel_DNCNumbersDataLogs
        fields = ['numbers', 'starts_with', 'created_at','dnc_type'] + DateFilter.date_fields


class InvalidNumberFilter(DateFilter):
    numbers = filters.NumberFilter(field_name='number', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')

    class Meta:
        model = InvalidNumbersDataLogs
        fields = ['numbers', 'created_at'] + DateFilter.date_fields


class UserLogFilter(DateFilter):
    numbers = filters.NumberFilter(field_name="number", lookup_expr='exact')
    starts_with = filters.NumberFilter(field_name="number", lookup_expr='startswith')
    line_type = filters.CharFilter(field_name='line_type', lookup_expr="exact")
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")
    dnc_type = filters.CharFilter(field_name='dnc_type', lookup_expr="exact")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(number__icontains=value) |
            Q(user__email__icontains=value)
        )


    class Meta:
        model = BaseModel_UserDataLogs
        fields = ['numbers', 'starts_with', 'line_type', 'created_at', 'dnc_type'] + DateFilter.date_fields

class EndatoLogFilter(DateFilter):
    numbers = filters.NumberFilter(field_name="number", lookup_expr='exact')
    starts_with = filters.NumberFilter(field_name="number", lookup_expr='startswith')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')

    class Meta:
        model = BaseModel_EndatoData
        fields = ['numbers', 'starts_with','created_at'] + DateFilter.date_fields


class SignalWireFilter(DateFilter):
    number = filters.NumberFilter(field_name='number', lookup_expr='exact')
    starts_with = filters.NumberFilter(field_name='number', lookup_expr='startswith')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')

    class Meta:
        model = BaseModel_NumbersData
        fields = ['number', 'starts_with', 'created_at'] + DateFilter.date_fields


class SignupDomainFilter(DateFilter):
    domain = filters.CharFilter(field_name='domain', lookup_expr='exact')
    domain_status = filters.BooleanFilter(field_name='status', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='timestamp', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(domain__icontains=value)
        )

    class Meta:
        model = SignUpDomains
        fields = ['domain', 'domain_status', 'created_at'] + DateFilter.date_fields


class AssignedCreditsFilter(DateFilter):
    user = filters.CharFilter(field_name='user__username', lookup_expr="exact")
    staff_user = filters.CharFilter(field_name='user__username', lookup_expr='exact')
    action = filters.CharFilter(field_name='log_action', lookup_expr='exact')
    min_credits = filters.NumberFilter(field_name='credits', lookup_expr='gte')
    max_credits = filters.NumberFilter(field_name='credits', lookup_expr='lte')
    created_at = filters.DateFilter(field_name='created', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user_note__icontains=value) |
            Q(staff_note__icontains=value)
        )

    class Meta:
        model = AssignedCredits
        fields = ['user', 'staff_user', 'action', 'min_credits', 'max_credits', 'created_at', 'search_by'] + DateFilter.date_fields


class OffersFilter(DateFilter):
    upcoming = filters.BooleanFilter(method='filter_upcoming', label="Upcoming Offers")
    expired = filters.BooleanFilter(method='filter_expired', label="Expired Offers")
    ongoing = filters.BooleanFilter(method='filter_ongoing', label="Ongoing Offer")

    offer_name = django_filters.CharFilter(field_name='offer_name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()  # Allows filtering by active status
    start_date = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')  # Filter for start date
    end_date = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')  # Filter for end date
    offer_type = django_filters.ChoiceFilter(choices=Offers.OfferType.choices)  # Filter by offer type

    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(offer_name__icontains=value) |
            Q(descriptions__icontains=value)
        )



    class Meta:
        model = Offers
        fields = ['upcoming', 'expired', 'ongoing', 'offer_name', 'is_active', 'start_date', 'end_date', 'offer_type'] + DateFilter.date_fields

    def filter_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(start_date__gt=date.today())
        return queryset

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(end_date__lt=date.today())
        return queryset

    def filter_ongoing(self, queryset, name, value):
        if value:
            return queryset.filter(start_date__lte=date.today(), end_date__gte=date.today())
        return queryset

class OfferDetailsFilterset(DateFilter):
    offer_id = filters.NumberFilter(field_name="offer__id", lookup_expr="exact")
    is_reseller = filters.BooleanFilter(field_name="plan__is_reseller", lookup_expr="exact")
    service_type = django_filters.ChoiceFilter(field_name="plan__service_type", choices=Plans.ServiceType.choices)

    class Meta:
        model = OfferDetails
        fields = ["offer_id", "is_reseller", "service_type"] + DateFilter.date_fields

class UserActivityLogFilter(DateFilter):
    user = filters.CharFilter(field_name='user__email', lookup_expr="exact")
    actions = filters.CharFilter(field_name='actions', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(actions__icontains=value) |
            Q(user__email__icontains=value) |
            Q(description__icontains=value)
        )


    class Meta:
        model = UserActivityLog
        fields = ['user', 'actions', 'start_date', 'end_date', 'search_by'] + DateFilter.date_fields



class UserActivityLogsFilter(DateFilter):
    user = filters.CharFilter(field_name='user__email', lookup_expr="exact")
    actions = filters.CharFilter(field_name='actions', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(actions__icontains=value) |
            Q(user__email__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = UserActivityLogs  # ✅ Use correct models
        fields = ['user', 'actions', 'start_date', 'end_date', 'search_by'] + DateFilter.date_fields

class AdminActivityLogFilter(DateFilter):
    user = filters.CharFilter(field_name='user__email', lookup_expr="exact")
    actions = filters.CharFilter(field_name='actions', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(actions__icontains=value) |
            Q(user__email__icontains=value) |
            Q(description__icontains=value)
        )


    class Meta:
        model = AdminActivityLog
        fields = ['user', 'actions', 'start_date', 'end_date', 'search_by'] + DateFilter.date_fields



class CsvTop7Filter(DateFilter):
    class Meta:
        model = CsvFile
        fields = DateFilter.date_fields


class EmailstatusFilter(DateFilter):
    class Meta:
        model = EmailAddress
        fields = DateFilter.date_fields


class CsvFileDataFilter(DateFilter):
    class Meta:
        model = CsvFileData
        fields = DateFilter.date_fields


class DatabasesGeneralAnalyticsFilter(DateFilter):
    class Meta:
        model = DatabasesGeneralAnalytics
        fields = DateFilter.date_fields


class CsvFilesDetailsFilter(DateFilter):
    phonenumber = filters.NumberFilter(field_name='phonenumber', lookup_expr='exact')
    city = filters.CharFilter(field_name='city', lookup_expr='exact')
    country = filters.CharFilter(field_name='country', lookup_expr='exact')
    line_type = filters.CharFilter(field_name='line_type', lookup_expr='exact')
    dnc_type = filters.CharFilter(field_name='dnc_type', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(city__icontains=value) |
            Q(country__icontains=value) |
            Q(phonenumber__icontains=value)
        )

    class Meta:
        model = CsvFileData
        fields = ['phonenumber', 'city', 'country', 'line_type', 'dnc_type','search_by'] + DateFilter.date_fields


class UserActionLogFilter(DateFilter):
    admin_user = filters.CharFilter(field_name='admin_user__username', lookup_expr="exact")
    target_user = filters.CharFilter(field_name='target_user__username', lookup_expr='exact')
    action_type = filters.CharFilter(field_name='action_type', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(admin_user__username__icontains=value) |
            Q(target_user__username__icontains=value) |
            Q(action_type__icontains=value) |
            Q(details__icontains=value)
        )

    class Meta:
        model = UserActionLog
        fields = ['admin_user', 'target_user', 'action_type'] + DateFilter.date_fields


class CsvFileEmailFilter(filters.FilterSet):
    uid = filters.CharFilter(field_name='uid', lookup_expr='exact')
    csvfile_name = filters.CharFilter(field_name='csvfile_name', lookup_expr='icontains')
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='exact')
    is_complete = filters.BooleanFilter(field_name='is_complete', lookup_expr='exact')
    is_failed = filters.BooleanFilter(field_name='is_failed', lookup_expr='exact')
    uploaded_at = filters.DateFromToRangeFilter(field_name='uploaded_at')

    class Meta:
        model = CsvFileEmail
        fields = ['uid', 'csvfile_name', 'user_email', 'is_complete', 'is_failed', 'uploaded_at']


class ApiHomeFilter(DateFilter):
    line_type = django_filters.CharFilter(field_name="line_type", lookup_expr="iexact")
    dnc_type = django_filters.CharFilter(field_name="dnc_type", lookup_expr="iexact")
    added_through = django_filters.CharFilter(field_name='added_through', lookup_expr='exact')

    class Meta:
        model = APIData
        fields = ['line_type', 'dnc_type', 'added_through', 'start_date', 'end_date'] + DateFilter.date_fields



class ContactUsFilter(DateFilter):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name='subject', lookup_expr='icontains')
    is_solved = django_filters.BooleanFilter(field_name='is_solved')
    created_at = django_filters.DateFilter(field_name='timestamp', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(email__icontains=value) |
            Q(message__icontains=value) |
            Q(subject__icontains=value)
        )

    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'subject', 'is_solved', 'created_at', 'search_by'] + DateFilter.date_fields


class ReferenceUserFilter(DateFilter):
    referral_source = filters.CharFilter(field_name='referral_source', lookup_expr='exact')
    user_input = filters.CharFilter(field_name='user_input', lookup_expr='exact')
    is_referral_user = filters.BooleanFilter(field_name='is_referral_user', lookup_expr='exact')
    created_at = filters.DateFilter(field_name='created_at', lookup_expr='date')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(user__username__icontains=value)
        )

    class Meta:
        model = ReferenceUser
        fields = ['referral_source', 'user_input', 'is_referral_user', 'created_at', 'search_by'] + DateFilter.date_fields


class CsvFileDataFilter(django_filters.FilterSet):
    line_type = django_filters.CharFilter(field_name="line_type", lookup_expr="iexact")
    dnc_type = django_filters.CharFilter(field_name="dnc_type", lookup_expr="iexact")
    start_date = django_filters.DateFilter(field_name="csvfile__uploaded_at", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="csvfile__uploaded_at", lookup_expr="lte")

    # Custom date range filter
    date_filter = django_filters.CharFilter(method="filter_by_date_range")

    class Meta:
        model = CsvFileData
        fields = ["line_type", "dnc_type", "start_date", "end_date"]

    def filter_by_date_range(self, queryset, name, value):
        today = timezone.now().date()

        if value == "today":
            return queryset.filter(csvfile__uploaded_at__date=today)
        elif value == "yesterday":
            return queryset.filter(csvfile__uploaded_at__date=today - timedelta(days=1))
        elif value == "last_7_days":
            return queryset.filter(csvfile__uploaded_at__date__gte=today - timedelta(days=7))
        elif value == "last_15_days":
            return queryset.filter(csvfile__uploaded_at__date__gte=today - timedelta(days=15))
        elif value == "last_30_days":
            return queryset.filter(csvfile__uploaded_at__date__gte=today - timedelta(days=30))
        elif value == "last_60_days":
            return queryset.filter(csvfile__uploaded_at__date__gte=today - timedelta(days=60))
        elif value == "this_month":
            return queryset.filter(csvfile__uploaded_at__year=today.year, csvfile__uploaded_at__month=today.month)
        elif value == "last_month":
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_year = today.year if today.month > 1 else today.year - 1
            return queryset.filter(csvfile__uploaded_at__year=last_month_year, csvfile__uploaded_at__month=last_month)

        return queryset


class APIDataFilter(DateFilter):
    line_type = django_filters.CharFilter(field_name="line_type", lookup_expr="iexact")
    dnc_type = django_filters.CharFilter(field_name="dnc_type", lookup_expr="iexact")
    start_date = django_filters.DateFilter(field_name="timestamp", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="timestamp", lookup_expr="lte")

    date_filter = django_filters.ChoiceFilter(
        method="filter_by_date",
        choices=[
            ("today", "Today"),
            ("yesterday", "Yesterday"),
            ("last_7_days", "Last 7 Days"),
            ("last_15_days", "Last 15 Days"),
            ("last_30_days", "Last 30 Days"),
            ("last_60_days", "Last 60 Days"),
            ("this_month", "This Month"),
            ("last_month", "Last Month"),
        ]
    )

    def filter_by_date(self, queryset, name, value):
        today = now().date()
        if value == "today":
            return queryset.filter(timestamp__date=today)
        elif value == "yesterday":
            return queryset.filter(timestamp__date=today - timedelta(days=1))
        elif value == "last_7_days":
            return queryset.filter(timestamp__date__gte=today - timedelta(days=7))
        elif value == "last_15_days":
            return queryset.filter(timestamp__date__gte=today - timedelta(days=15))
        elif value == "last_30_days":
            return queryset.filter(timestamp__date__gte=today - timedelta(days=30))
        elif value == "last_60_days":
            return queryset.filter(timestamp__date__gte=today - timedelta(days=60))
        elif value == "this_month":
            return queryset.filter(timestamp__year=today.year, timestamp__month=today.month)
        elif value == "last_month":
            last_month = today.month - 1 if today.month > 1 else 12
            last_month_year = today.year if today.month > 1 else today.year - 1
            return queryset.filter(timestamp__year=last_month_year, timestamp__month=last_month)

        return queryset

    class Meta:
        model = APIData
        fields = ["line_type", "dnc_type", "start_date", "end_date", "date_filter"] + DateFilter.date_fields


# class ExpenseInvoiceFilter(django_filters.FilterSet):
#     title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
#     user_email = django_filters.CharFilter(field_name='user_email__email', lookup_expr='exact')  # Assuming user_email is a ForeignKey to User
#     uploaded_at = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='date')
#     start_date = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='gte')  # Start date filter
#     end_date = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='lte')  # End date filter

#     class Meta:
#         models = ExpenseInvoice
#         fields = ['title', 'user_email', 'uploaded_at', 'start_date', 'end_date'] + DateFilter.date_fields


class PlansFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    price = django_filters.RangeFilter()  # Allows filtering by a range of prices
    discount_price = django_filters.RangeFilter()  # Allows filtering by a range of discount prices
    credits = django_filters.RangeFilter()  # Allows filtering by a range of credits
    is_reseller = django_filters.BooleanFilter()  # Allows filtering by reseller status
    service_type = django_filters.ChoiceFilter(choices=Plans.ServiceType.choices)  # Filter by service type

    class Meta:
        model = Plans
        fields = ['name', 'price', 'discount_price', 'credits', 'is_reseller', 'service_type']


# class OffersFilter(django_filters.FilterSet):
#     offer_name = django_filters.CharFilter(field_name='offer_name', lookup_expr='icontains')
#     is_active = django_filters.BooleanFilter()  # Allows filtering by active status
#     start_date = django_filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')  # Filter for start date
#     end_date = django_filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')  # Filter for end date
#     offer_type = django_filters.ChoiceFilter(choices=Offers.OfferType.choices)  # Filter by offer type
#
#     class Meta:
#         models = Offers
#         fields = ['offer_name', 'is_active', 'start_date', 'end_date', 'offer_type']


class FeaturePermissionFilter(DateFilter):
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')  # Filter by username
    feature = django_filters.CharFilter(field_name='feature__name', lookup_expr='icontains')  # Filter by feature name
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value)
        )

    class Meta:
        model = FeaturePermission
        fields = ['user', 'feature'] + DateFilter.date_fields


class WavixBatchRequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    status = django_filters.ChoiceFilter(choices=WavixBatchRequest.RequestStatus.choices)
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = WavixBatchRequest
        fields = ['status', 'created_at']


class WavixRequestTrackerFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search', label='Search')
    is_completed = django_filters.BooleanFilter()
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = WavixRequestTracker
        fields = ['is_completed', 'created_at']


class DynamicEmailMetadataFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr='icontains')
    email_format = django_filters.CharFilter(lookup_expr='icontains')
    mx_record = django_filters.CharFilter(lookup_expr='icontains')
    domain_exists = django_filters.BooleanFilter()
    disposable_email = django_filters.BooleanFilter()
    role_account = django_filters.BooleanFilter()
    common_typo = django_filters.BooleanFilter()
    spf_record = django_filters.BooleanFilter()
    dkim_record = django_filters.BooleanFilter()
    dmarc_record = django_filters.BooleanFilter()
    new_domain = django_filters.BooleanFilter()
    valid_tld = django_filters.BooleanFilter()
    is_spam = django_filters.BooleanFilter()
    feee_domain = django_filters.BooleanFilter()
    validation_date = django_filters.DateFilter()

    class Meta:
        model = EmailMetadataBase
        fields = [
            'email', 'email_format', 'mx_record', 'domain_exists', 'disposable_email',
            'role_account', 'common_typo', 'spf_record', 'dkim_record', 'dmarc_record',
            'new_domain', 'valid_tld', 'is_spam', 'feee_domain', 'validation_date'
        ]


class TeamFilter(django_filters.FilterSet):
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')

    team_name = django_filters.CharFilter(lookup_expr='icontains')
    created_by = django_filters.CharFilter(field_name="created_by__email", lookup_expr='icontains')
    created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='date')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_active = django_filters.BooleanFilter(method='filter_is_active')
    search_by = django_filters.CharFilter(method='filter_by_team_or_created_by')

    class Meta:
        model = Team
        fields = ['team_name', 'created_by', 'created_at', 'is_deleted', 'search_by']

    def filter_start_date(self, queryset, name, value):
        try:
            start_date = datetime.datetime.strptime(value, '%Y-%m-%d')
            start_date = make_aware(start_date, timezone=pytz.UTC)
            return queryset.filter(created_at__gte=start_date)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end_date = datetime.datetime.strptime(value, '%Y-%m-%d') + datetime.timedelta(days=1)
            end_date = make_aware(end_date, timezone=pytz.UTC)
            return queryset.filter(created_at__lt=end_date)
        except Exception:
            return queryset.none()

    def filter_by_team_or_created_by(self, queryset, name, value):
        return queryset.filter(
            Q(team_name__icontains=value) |
            Q(created_by__email__icontains=value) |
            Q(created_by__username__icontains=value)
        )

    def filter_is_active(self, queryset, name, value):
        return queryset.filter(is_deleted=not value)


class MembersFilter(django_filters.FilterSet):
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')
    team_name = django_filters.ModelChoiceFilter(queryset=Team.objects.all())
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='date')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_active = django_filters.BooleanFilter(field_name='is_deleted', lookup_expr='exact', exclude=True)
    feature = django_filters.CharFilter(method='filter_by_feature')
    search = django_filters.CharFilter(method='filter_search')
    team_id = django_filters.NumberFilter(field_name='team_name__id', lookup_expr='exact')

    class Meta:
        model = Members
        fields = ['team_name', 'user', 'created_at', 'is_deleted', 'feature_number_lookup', 'feature_data_enrichment',
                  'feature_email', 'search', 'team_id']

    def filter_by_feature(self, queryset, name, value):
        features = {
            'number_lookup': Q(feature_number_lookup=True),
            'data_enrichment': Q(feature_data_enrichment=True),
            'email': Q(feature_email=True)
        }
        if value in features:
            return queryset.filter(features[value])
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(team_name__team_name__icontains=value)
        )

    def filter_start_date(self, queryset, name, value):
        try:
            start_date = datetime.datetime.strptime(value, '%Y-%m-%d')
            start_date = make_aware(start_date, timezone=pytz.UTC)
            return queryset.filter(created_at__gte=start_date)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end_date = datetime.datetime.strptime(value, '%Y-%m-%d') + datetime.timedelta(days=1)
            end_date = make_aware(end_date, timezone=pytz.UTC)
            return queryset.filter(created_at__lt=end_date)
        except Exception:
            return queryset.none()


class MemberInvitationFilter(django_filters.FilterSet):
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')
    invited_user = django_filters.CharFilter(field_name='user_email', lookup_expr='icontains')
    is_accepted = django_filters.BooleanFilter(field_name='is_accepted')
    invited_by = django_filters.CharFilter(field_name='invited_by__email', lookup_expr='icontains')
    credit_type = django_filters.CharFilter(method='filter_credit_type')
    created_at = django_filters.DateTimeFilter(field_name='created_at')
    is_removed = django_filters.BooleanFilter(field_name='is_deleted')
    removed_at = django_filters.DateTimeFilter(field_name='deleted_at')

    class Meta:
        model = MemberInvitation
        fields = ['invited_user', 'is_accepted', 'invited_by', 'credit_type', 'created_at', 'is_removed', 'removed_at']

    def filter_credit_type(self, queryset, name, value):
        credit_types = [ct.strip().lower() for ct in value.split(',')]
        q_objects = Q()

        for credit_type in credit_types:
            if credit_type == 'number lookup':
                q_objects |= Q(feature_number_lookup=True)
            elif credit_type == 'data enrichment':
                q_objects |= Q(feature_data_enrichment=True)
            elif credit_type == 'email':
                q_objects |= Q(feature_email=True)

        if 'none' in credit_types:
            q_objects |= Q(feature_number_lookup=False, feature_data_enrichment=False, feature_email=False)
        return queryset.filter(q_objects)

    def filter_start_date(self, queryset, name, value):
        try:
            start_date = datetime.datetime.strptime(value, '%Y-%m-%d')
            start_date = make_aware(start_date, timezone=pytz.UTC)
            return queryset.filter(created_at__gte=start_date)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end_date = datetime.datetime.strptime(value, '%Y-%m-%d') + datetime.timedelta(days=1)
            end_date = make_aware(end_date, timezone=pytz.UTC)
            return queryset.filter(created_at__lt=end_date)
        except Exception:
            return queryset.none()


class TeamInvitationRequestFilter(django_filters.FilterSet):
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')
    email = django_filters.CharFilter(method='filter_email')
    status = django_filters.CharFilter(method='filter_status')

    class Meta:
        model = TeamInvitationRequest
        fields = ['email', 'status']

    def filter_email(self, queryset, name, value):
        return queryset.filter(email__icontains=value.strip())

    def filter_status(self, queryset, name, value):
        if value == 'accepted':
            return queryset.filter(is_joined=True)
        elif value == 'rejected':
            return queryset.filter(is_joined=False, is_deleted=True)
        elif value == 'pending':
            return queryset.filter(is_joined=False, is_deleted=False)
        return queryset

    def filter_start_date(self, queryset, name, value):
        try:
            start_date = datetime.datetime.strptime(value, '%Y-%m-%d')
            start_date = make_aware(start_date, timezone=pytz.UTC)
            return queryset.filter(created_at__gte=start_date)
        except Exception:
            return queryset.none()

    def filter_end_date(self, queryset, name, value):
        try:
            end_date = datetime.datetime.strptime(value, '%Y-%m-%d') + datetime.timedelta(days=1)
            end_date = make_aware(end_date, timezone=pytz.UTC)
            return queryset.filter(created_at__lt=end_date)
        except Exception:
            return queryset.none()

class TeamCreditsFilter(django_filters.FilterSet):
    team_name = django_filters.ModelChoiceFilter(queryset=Team.objects.all())
    assignto = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    credits_min = django_filters.NumberFilter(field_name='credits', lookup_expr='gte')
    credits_max = django_filters.NumberFilter(field_name='credits', lookup_expr='lte')
    credit_type = django_filters.ChoiceFilter(choices=TeamCredits.MODE_CHOICES)
    created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='date')
    created_at_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_active = django_filters.BooleanFilter(field_name='is_deleted', lookup_expr='exact', exclude=True)

    class Meta:
        model = TeamCredits
        fields = [
            'team_name',
            'assignto',
            'credits',
            'credit_type',
            'created_at',
            'is_deleted'
        ]


class ServiceLogsFilter(filters.FilterSet):
    # Search fields
    search_by = filters.CharFilter(method='filter_search')

    # Date filters
    created = filters.DateTimeFilter(field_name='created', lookup_expr='date')
    created_after = filters.DateTimeFilter(field_name='created', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created', lookup_expr='lte')

    # Date filters for last checked
    last_checked = filters.DateTimeFilter(field_name='last_checked', lookup_expr='date')
    last_checked_after = filters.DateTimeFilter(field_name='last_checked', lookup_expr='gte')
    last_checked_before = filters.DateTimeFilter(field_name='last_checked', lookup_expr='lte')

    # Interval filters
    success_interval_min = filters.NumberFilter(field_name='success_interval', lookup_expr='gte')
    success_interval_max = filters.NumberFilter(field_name='success_interval', lookup_expr='lte')
    failure_interval_min = filters.NumberFilter(field_name='failure_interval', lookup_expr='gte')
    failure_interval_max = filters.NumberFilter(field_name='failure_interval', lookup_expr='lte')

    # Boolean filters
    is_active = filters.BooleanFilter(field_name='service_status')
    has_telegram_alerts = filters.BooleanFilter(field_name='alert_on_telegram')
    has_email_alerts = filters.BooleanFilter(field_name='alert_on_email')
    is_tracking_enabled = filters.BooleanFilter(field_name='allow_tracking')

    # Exact match filters
    uid = filters.CharFilter(lookup_expr='exact')
    title = filters.CharFilter(lookup_expr='icontains')
    service_type = filters.ChoiceFilter(choices=ServicesStatus.SERVICE_TYPE.choices)

    class Meta:
        model = ServicesStatus
        fields = [
            'uid',
            'title',
            'service_type',
            'success_interval',
            'failure_interval',
            'last_checked',
            'allow_consecutive_failures',
            'consecutive_failures_attempts',
            'alert_on_telegram',
            'alert_on_email',
            'allow_tracking',
            'service_status',
            'created',
            'search_by'
        ]  # Removed 'updated' field as it doesn't exist in the models

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(uid__icontains=value) |
            Q(title__icontains=value) |
            Q(service_type__icontains=value)
        )


class promoCodeFilter(DateFilter):
    name = filters.CharFilter(field_name="title", lookup_expr="icontains")
    promo_code = filters.CharFilter(field_name='promo_code', lookup_expr='exact')
    is_active = filters.BooleanFilter(field_name='active', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_name_or_code', label="Search by Name or Promo Code")

    class Meta:
        model = PromoCodes
        fields = ["name", "promo_code", "is_active", "search_by"] + DateFilter.date_fields

    def filter_by_name_or_code(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(promo_code__icontains=value)
        )

class promoCodeUserFilter(DateFilter):
    promo_code = filters.CharFilter(field_name='promo_code__promo_code', lookup_expr="icontains")
    email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    class Meta:
        model = PromoCodeUsers
        fields = ['promo_code', 'email'] + DateFilter.date_fields

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(promo_code__promo_code__icontains=value) |
            Q(user__email__icontains=value)
        )




class EmailFilesFilter(DateFilter):
    file_uid = filters.CharFilter(field_name='uid', lookup_expr='icontains')
    file_name = filters.CharFilter(field_name='csvfile_name', lookup_expr='icontains')
    email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    is_complete = filters.BooleanFilter(field_name='is_complete', lookup_expr='exact')
    is_failed = filters.BooleanFilter(field_name='is_failed', lookup_expr='exact')
    is_canceled = filters.BooleanFilter(field_name='is_canceled', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    min_rows = filters.NumberFilter(field_name='total_rows', lookup_expr='gte')
    max_rows = filters.NumberFilter(field_name='total_rows', lookup_expr='lte')

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(uid__icontains=value) |
            Q(csvfile_name__icontains=value) |
            Q(user__email__icontains=value)
        )

    class Meta:
        model = CsvFileEmail
        fields = ['file_uid', 'file_name', 'email', 'min_rows', 'max_rows', 'search_by', 'is_complete', 'is_failed', 'is_canceled'] + DateFilter.date_fields


class EmailFileDataFilter(DateFilter):
    csvfile_id = filters.NumberFilter(field_name='csvfile__id', lookup_expr='exact')

    class Meta:
        model = CsvFileDataEmail
        fields = ['csvfile_id'] + DateFilter.date_fields

class DeletedAccountListFilter(DateFilter):
    user_email = filters.CharFilter(field_name='email', lookup_expr='exact')
    phone = filters.NumberFilter(field_name='phone_number', lookup_expr='icontains')
    reseller = filters.BooleanFilter(field_name='reseller', lookup_expr='exact')
    account_type = filters.CharFilter(field_name='account_status', lookup_expr='exact')
    account_role = filters.CharFilter(field_name='role', lookup_expr='exact')
    start_date = filters.DateFilter(field_name='deleted_at', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='deleted_at', lookup_expr='lte')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(email__icontains=value) |
            Q(phone_number__icontains=value)
        )

    class Meta:
        model = DeletedUserAccounts
        fields = ['user_email', 'phone', 'reseller', 'account_type', 'account_role', 'start_date', 'end_date'] + DateFilter.date_fields

class InvoicesFilter(DateFilter):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    user = filters.CharFilter(field_name='user_email__email', lookup_expr='icontains')
    Description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__name', lookup_expr='exact')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user_email__email__icontains=value) |
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = ExpenseInvoice
        fields = ['title', 'user', 'Description', 'category', 'min_amount', 'max_amount'] + DateFilter.date_fields

class InvoiceCategoryList(DateFilter):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ExpenseCategory
        fields = ['name'] + DateFilter.date_fields

class LineTypeDataList(DateFilter):
    number = filters.NumberFilter(field_name='number', lookup_expr='icontains')

    class Meta:
        model = OneYearOldData
        fields = ['number'] + DateFilter.date_fields

class CreditAnalyticsFilters(DateFilter):

    class Meta:
        model = CreditAnalytics
        fields = DateFilter.date_fields

class CreditLogsFilterFilters(DateFilter):
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')

    class Meta:
        model = UserActivityLog
        fields = ['user_email'] + DateFilter.date_fields

class TextDripWheebookFilter(DateFilter):
    csv_uid = filters.CharFilter(field_name="csv_file__uid", lookup_expr='icontains')
    added_through = filters.ChoiceFilter(field_name="added_through", choices=TextdripWebhook.ADDED_THROUGH.choices)
    credit_type = filters.ChoiceFilter(field_name="credit_type", choices=TextdripWebhook.CREDIT_TYPE.choices)

    class Meta:
        model = TextdripWebhook
        fields = ['csv_uid', 'added_through', 'credit_type'] + DateFilter.date_fields

class NotificationFilters(DateFilter):
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')

    class Meta:
        model = SiteNotifications
        fields = ['user_email'] + DateFilter.date_fields


class MembersTeamFilters(DateFilter):
    user_email = filters.CharFilter(field_name='user__email', lookup_expr='icontains')
    team_name = filters.CharFilter(field_name='team_name__team_name', lookup_expr='icontains')
    added_by = filters.CharFilter(field_name='team_name__created_by__email', lookup_expr='icontains')
    is_active = filters.BooleanFilter(field_name='is_deleted')
    team_id = filters.NumberFilter(field_name='team_name__id', lookup_expr='exact')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(team_name__team_name__icontains=value) |
            Q(team_name__created_by__email__icontains=value)
        )

    class Meta:
        model = Members
        fields = ['user_email', 'team_name', 'added_by', 'is_active', 'team_id'] + DateFilter.date_fields


class TeamAssignCreditFilters(DateFilter):
    user_email = filters.CharFilter(field_name='assignto__email', lookup_expr='icontains')
    team_name = filters.CharFilter(field_name='team_name__team_name', lookup_expr='icontains')
    assigned_by = filters.CharFilter(field_name='team_name__created_by__email', lookup_expr='icontains')
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")
    credit_type = filters.ChoiceFilter(field_name='credit_type', choices=TeamCredits.MODE_CHOICES, label='Credit Type')

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(assignto__email__icontains=value) |
            Q(team_name__team_name__icontains=value) |
            Q(team_name__created_by__email__icontains=value)
        )

    class Meta:
        model = TeamCredits
        fields = ['user_email', 'team_name', 'assigned_by', 'search_by'] + DateFilter.date_fields

class UserEmailFilter(django_filters.FilterSet):
    is_user = django_filters.BooleanFilter(method='filter_is_user')
    is_staff = django_filters.BooleanFilter(method='filter_is_staff')
    is_superuser = django_filters.BooleanFilter(field_name='is_superuser', lookup_expr='exact')
    is_staff_superuser = django_filters.BooleanFilter(method='filter_is_staff_superuser')

    class Meta:
        model = User
        fields = ['is_user', 'is_staff', 'is_superuser', 'is_staff_superuser']

    def filter_is_user(self, queryset, name, value):
        if value:
            return queryset.filter(is_staff=False, is_superuser=False)
        return queryset

    def filter_is_staff(self, queryset, name, value):
        if value:
            return queryset.filter(is_staff=True, is_superuser=False)
        return queryset

    def filter_is_staff_superuser(self, queryset, name, value):
        if value:
            return queryset.filter(is_staff=True)
        return queryset

class CustomStatusLogFilter(DateFilter):
    log_type = filters.CharFilter(field_name='log_type', lookup_expr='icontains')

    class Meta:
        model = CustomSiteLogs
        fields = ['log_type'] + DateFilter.date_fields

class ServiceStatusLogsFilter(DateFilter):
    service_type = filters.CharFilter(field_name='service__service_type', lookup_expr='icontains')

    class Meta:
        model = ServicesStatusLogs
        fields = ['service_type'] + DateFilter.date_fields

class DynamicEmailFilter(DateFilter):

    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    class meta:
        model = EmailMetadataBase
        fields = ['email'] + DateFilter.date_fields


class PersonSearchListFilters(DateFilter):
    search_by = filters.CharFilter(method='filter_by_code_or_email', label="Search by Promo Code or Email")
    file_status = filters.CharFilter(method='filter_file_status', label='File Status')
    min_rows = filters.NumberFilter(field_name='csvfile__total_rows', lookup_expr='gte')
    max_rows = filters.NumberFilter(field_name='csvfile__total_rows', lookup_expr='lte')

    def filter_by_code_or_email(self, queryset, name, value):
        return queryset.filter(
            Q(csvfile__uid__icontains=value) |
            Q(csvfile__csvfile_name__icontains=value) |
            Q(csvfile__user__email__icontains=value)
        )

    def filter_file_status(self, queryset, name, value):
        value = value.lower().strip()
        if value == "failed":
            return queryset.filter(csvfile__is_failed=True)
        elif value == "completed":
            return queryset.filter(csvfile__is_complete=True, csvfile__is_failed=False)
        elif value == "incomplete process":
            return queryset.filter(csvfile__is_charged=False, csvfile__is_complete=False, csvfile__is_failed=False)
        elif value == "in progress":
            return queryset.filter(csvfile__is_charged=True, csvfile__is_complete=False, csvfile__is_failed=False)
        return queryset.none()

    class Meta:
        model = EndatoCsvFileData
        fields = ['search_by', 'file_status', 'min_rows', 'max_rows'] + DateFilter.date_fields


class CustomSubscriptionFilter(DateFilter):
    search = filters.CharFilter(field_name='name', lookup_expr='icontains', label='Search by Plan Name')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    credits_min = filters.NumberFilter(field_name='nm_credits', lookup_expr='gte')
    credits_max = filters.NumberFilter(field_name='nm_credits', lookup_expr='lte')
    interval = filters.ChoiceFilter(field_name='interval', choices=[('month', 'Month'), ('year', 'Year')], label='Billing Interval')
    plan_duration = filters.CharFilter(field_name='plan_duration', lookup_expr='exact')
    ordering = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('-created_at', 'created_at_desc'),
            ('price', 'price'),
            ('-price', 'price_desc'),
            ('nm_credits', 'credits'),
            ('-nm_credits', 'credits_desc'),
        ),
        field_labels={
            'created_at': 'Created (oldest first)',
            '-created_at': 'Created (newest first)',
            'price': 'Price (low to high)',
            '-price': 'Price (high to low)',
            'nm_credits': 'Credits (low to high)',
            '-nm_credits': 'Credits (high to low)',
        }
    )

    class Meta:
        model = CustomSubscriptions
        fields = ['search', 'price_min', 'price_max', 'credits_min',
                  'credits_max', 'interval', 'plan_duration',] + DateFilter.date_fields


class CustomSubscriptionUserFilter(DateFilter):
    email = filters.CharFilter(field_name='user__email', lookup_expr='icontains', label='User Email')
    plan_name = filters.CharFilter(field_name='plan__name', lookup_expr='icontains', label='Plan Name')
    gross_credits_min = filters.NumberFilter(field_name='gross_credits', lookup_expr='gte')
    gross_credits_max = filters.NumberFilter(field_name='gross_credits', lookup_expr='lte')
    search = filters.CharFilter(method='filter_search', label='Search')
    ordering = OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('-created_at', 'created_at_desc'),
            ('plan__price', 'plan_price'),
            ('-plan__price', 'plan_price_desc'),
            ('gross_credits', 'gross_credits'),
            ('-gross_credits', 'gross_credits_desc'),
        ),
        field_labels={
            'created_at': 'Created (oldest)',
            '-created_at': 'Created (newest)',
            'plan__price': 'Plan Price (low)',
            '-plan__price': 'Plan Price (high)',
            'gross_credits': 'Gross Credits (low)',
            '-gross_credits': 'Gross Credits (high)',
        }
    )

    class Meta:
        model = CustomSubscriptionUser
        fields = [
            'email', 'plan_name',
            'gross_credits_min', 'gross_credits_max',
            'search',
        ] + DateFilter.date_fields

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__email__icontains=value) |
            Q(plan__name__icontains=value)
        )
