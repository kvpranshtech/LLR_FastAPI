import datetime
from collections import defaultdict

from celery import shared_task
from django.db import transaction
from django.utils.timezone import now, localtime, make_aware, localdate
from datetime import timedelta

from api.models import APIData
from core.models import CsvFileData, EndatoCsvFileData, EndatoApiResponse
from datastorage.models import (
    SignalwireNumbersDataLogs0, SignalwireNumbersDataLogs1, SignalwireNumbersDataLogs2,
    SignalwireNumbersDataLogs3, SignalwireNumbersDataLogs4, SignalwireNumbersDataLogs5,
    SignalwireNumbersDataLogs6, SignalwireNumbersDataLogs7, SignalwireNumbersDataLogs8,
    SignalwireNumbersDataLogs9,
    NetNumberingDataLogs0, NetNumberingDataLogs1, NetNumberingDataLogs2, NetNumberingDataLogs3,
    NetNumberingDataLogs4, NetNumberingDataLogs5, NetNumberingDataLogs6, NetNumberingDataLogs7, NetNumberingDataLogs8,
    NetNumberingDataLogs9,
    WavixDataLogs0, WavixDataLogs1, WavixDataLogs2, WavixDataLogs3, WavixDataLogs4, WavixDataLogs5, WavixDataLogs6,
    WavixDataLogs7, WavixDataLogs8, WavixDataLogs9, APICall,
    DataEndato0, DataEndato1, DataEndato2, DataEndato3, DataEndato4, DataEndato5, DataEndato6, DataEndato7, DataEndato8,
    DataEndato9
)
from django.contrib.auth import get_user_model

User = get_user_model()


# @shared_task
# def count_and_create_api_call():
#     from django.contrib.auth.models import User
#     # user = User.objects.get(id=user_id)
#     user = User.objects.get(id=1)
#
#     today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
#     today_end = today_start + timedelta(days=1)
#
#     # Signalwire
#     signalwire_models = [
#         SignalwireNumbersDataLogs0, SignalwireNumbersDataLogs1, SignalwireNumbersDataLogs2,
#         SignalwireNumbersDataLogs3, SignalwireNumbersDataLogs4, SignalwireNumbersDataLogs5,
#         SignalwireNumbersDataLogs6, SignalwireNumbersDataLogs7, SignalwireNumbersDataLogs8,
#         SignalwireNumbersDataLogs9
#     ]
#     signalwire_count = sum(
#         models.objects.filter(timestamp__range=(today_start, today_end)).count() for models in signalwire_models)
#
#     # NetNumbering
#     netnumbering_models = [
#         NetNumberingDataLogs0, NetNumberingDataLogs1, NetNumberingDataLogs2,
#         NetNumberingDataLogs3, NetNumberingDataLogs4, NetNumberingDataLogs5,
#         NetNumberingDataLogs6, NetNumberingDataLogs7, NetNumberingDataLogs8,
#         NetNumberingDataLogs9
#     ]
#     netnumbering_count = sum(
#         models.objects.filter(timestamp__range=(today_start, today_end)).count() for models in netnumbering_models)
#
#     # Wavix
#     wavix_models = [
#         WavixDataLogs0, WavixDataLogs1, WavixDataLogs2,
#         WavixDataLogs3, WavixDataLogs4, WavixDataLogs5,
#         WavixDataLogs6, WavixDataLogs7, WavixDataLogs8,
#         WavixDataLogs9
#     ]
#     wavix_count = sum(models.objects.filter(timestamp__range=(today_start, today_end)).count() for models in wavix_models)
#
#
#
#     enrichment_model = [DataEndato0, DataEndato1, DataEndato2, DataEndato3, DataEndato4, DataEndato5, DataEndato6,
#                         DataEndato7, DataEndato8, DataEndato9]
#
#     enrichment_count = sum(
#         models.objects.filter(timestamp__range=(today_start, today_end)).count() for models in enrichment_model)
#
#     # Create APICall object
#     APICall.objects.create(
#         user=user,
#         signalwire=signalwire_count,
#         netnumbering=netnumbering_count,
#         wavix=wavix_count,
#         dataenrich=enrichment_count,
#     )
#
#     current_datetime = datetime.datetime.now()
#     print(f"Count Of API call for {current_datetime} has been updated .")
#     return f"Count Of API call for {current_datetime} has been updated ."


def create_or_update_signalwire_entry(user, signalwire_value):
    """
    Create or update an APICall entry for the user and signalwire.
    """
    today = localdate()
    api_call, created = APICall.objects.get_or_create(
        user=user,
        timestamp__date=today,
        defaults={
            'signalwire': signalwire_value
        }
    )
    if not created:
        api_call.signalwire += signalwire_value
        api_call.save()
    return api_call


def create_or_update_netnumbering_entry(user, netnumbering_value):
    """
    Create or update an APICall entry for the user and netnumbering.
    """
    today = localdate()
    api_call, created = APICall.objects.get_or_create(
        user=user,
        timestamp__date=today,
        defaults={
            'netnumbering': netnumbering_value
        }
    )
    if not created:
        api_call.netnumbering += netnumbering_value
        api_call.save()
    return api_call


def create_or_update_wavix_entry(user, wavix_value):
    """
    Create or update an APICall entry for the user and wavix.
    """
    today = localdate()
    with transaction.atomic():
        api_call, created = APICall.objects.select_for_update().get_or_create(
            user=user,
            timestamp__date=today,
            defaults={
                'wavix': wavix_value
            }
        )
        if not created:
            api_call.wavix += wavix_value
            api_call.save()
    return api_call


def create_or_update_dataenrich_entry(user, enrichment_value):
    """
    Create or update an APICall entry for the user and dataenrich.
    """
    today = localdate()
    api_call, created = APICall.objects.get_or_create(
        user=user,
        timestamp__date=today,
        defaults={
            'dataenrich': enrichment_value
        }
    )
    if not created:
        api_call.dataenrich += enrichment_value
        api_call.save()
    return api_call


@shared_task
def count_and_create_api_call():
    from django.contrib.auth.models import User
    # user = User.objects.get(id=user_id)
    user = User.objects.get(id=1)

    today_start = localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)


    # # Signalwire
    signalwire_models = [
        SignalwireNumbersDataLogs0, SignalwireNumbersDataLogs1, SignalwireNumbersDataLogs2,
        SignalwireNumbersDataLogs3, SignalwireNumbersDataLogs4, SignalwireNumbersDataLogs5,
        SignalwireNumbersDataLogs6, SignalwireNumbersDataLogs7, SignalwireNumbersDataLogs8,
        SignalwireNumbersDataLogs9
    ]
    signalwire_count = sum(
        model.objects.filter(timestamp__range=(today_start, today_end)).count() for model in signalwire_models)

    processed_numbers = set()
    user_signalwire_counts = defaultdict(set)

    for model in signalwire_models:
        signalwire_data = model.objects.filter(timestamp__range=(today_start, today_end))

        for signalwire_entry in signalwire_data:
            if signalwire_entry.number in processed_numbers:
                continue

            processed_numbers.add(signalwire_entry.number)

            matching_csv_entries = CsvFileData.objects.filter(
                phonenumber=signalwire_entry.number,
                csvfile__uploaded_at__range=(today_start, today_end)
            )

            if matching_csv_entries.exists():
                for csv_entry in matching_csv_entries:
                    print(' --- --- Signal -----', csv_entry)
                    user = csv_entry.csvfile.user
                    user_signalwire_counts[user].add(signalwire_entry.number)

            else:
                matching_api_entries = APIData.objects.filter(
                    phonenumber=signalwire_entry.number,
                    timestamp__range=(today_start, today_end)
                )

                if matching_api_entries.exists():
                    for api_entry in matching_api_entries:
                        print('----signal API entry ---', api_entry)
                        user = api_entry.userprofile.user
                        user_signalwire_counts[user].add(signalwire_entry.number)

    final_user_counts = {user: len(numbers) for user, numbers in user_signalwire_counts.items()}

    today = localdate()
    with transaction.atomic():
        for user, signalwire_value in final_user_counts.items():
            api_call = create_or_update_signalwire_entry(user, signalwire_value)
            print(f"User: {user}, Unique signal Count: {signalwire_value}, APICall: {api_call}")



    ## NetNumbering
    netnumbering_models = [
        NetNumberingDataLogs0, NetNumberingDataLogs1, NetNumberingDataLogs2,
        NetNumberingDataLogs3, NetNumberingDataLogs4, NetNumberingDataLogs5,
        NetNumberingDataLogs6, NetNumberingDataLogs7, NetNumberingDataLogs8,
        NetNumberingDataLogs9
    ]
    netnumbering_count = sum(
        model.objects.filter(timestamp__range=(today_start, today_end)).count() for model in netnumbering_models)

    processed_numbers = set()
    user_netnumbering_counts = defaultdict(set)

    for model in netnumbering_models:
        netnumbering_data = model.objects.filter(timestamp__range=(today_start, today_end))

        for netnumbering_entry in netnumbering_data:
            if netnumbering_entry.number in processed_numbers:
                continue

            processed_numbers.add(netnumbering_entry.number)

            matching_csv_entries = CsvFileData.objects.filter(
                phonenumber=netnumbering_entry.number,
                csvfile__uploaded_at__range=(today_start, today_end)
            )

            if matching_csv_entries.exists():
                for csv_entry in matching_csv_entries:
                    print(' --- --- netnumbering -----', csv_entry)
                    user = csv_entry.csvfile.user
                    user_netnumbering_counts[user].add(netnumbering_entry.number)

            else:
                matching_api_entries = APIData.objects.filter(
                    phonenumber=netnumbering_entry.number,
                    timestamp__range=(today_start, today_end)
                )

                if matching_api_entries.exists():
                    for api_entry in matching_api_entries:
                        print('---- netnumbering API entry ---', api_entry)
                        user = api_entry.userprofile.user
                        user_netnumbering_counts[user].add(netnumbering_entry.number)

    final_net_numbering_counts = {user: len(numbers) for user, numbers in user_netnumbering_counts.items()}

    today = localdate()
    with transaction.atomic():
        for user, netnumbering_value in final_net_numbering_counts.items():
            api_call = create_or_update_netnumbering_entry(user, netnumbering_value)
            print(f"User: {user}, Unique netnumbering Count: {netnumbering_value}, APICall: {api_call}")

    # Wavix
    wavix_models = [
        WavixDataLogs0, WavixDataLogs1, WavixDataLogs2,
        WavixDataLogs3, WavixDataLogs4, WavixDataLogs5,
        WavixDataLogs6, WavixDataLogs7, WavixDataLogs8,
        WavixDataLogs9
    ]
    wavix_count = sum(model.objects.filter(timestamp__range=(today_start, today_end)).count() for model in wavix_models)

    processed_numbers = set()
    user_wavix_counts = defaultdict(set)

    for model in wavix_models:
        wavix_data = model.objects.filter(timestamp__range=(today_start, today_end))

        for wavix_entry in wavix_data:
            if wavix_entry.number in processed_numbers:
                continue

            processed_numbers.add(wavix_entry.number)

            matching_csv_entries = CsvFileData.objects.filter(
                phonenumber=wavix_entry.number,
                csvfile__uploaded_at__range=(today_start, today_end)
            )

            if matching_csv_entries.exists():
                for csv_entry in matching_csv_entries:
                    print('----', csv_entry)
                    user = csv_entry.csvfile.user
                    user_wavix_counts[user].add(wavix_entry.number)

            else:
                matching_api_entries = APIData.objects.filter(
                    phonenumber=wavix_entry.number,
                    timestamp__range=(today_start, today_end)
                )

                if matching_api_entries.exists():
                    for api_entry in matching_api_entries:
                        print('---- API entry ---', api_entry)
                        user = api_entry.userprofile.user
                        user_wavix_counts[user].add(wavix_entry.number)

    final_user_counts = {user: len(numbers) for user, numbers in user_wavix_counts.items()}

    today = localdate()
    with transaction.atomic():
        for user, wavix_value in final_user_counts.items():
            api_call = create_or_update_wavix_entry(user, wavix_value)
            print(f"User: {user}, Unique Wavix Count: {wavix_value}, APICall: {api_call}")




    # # Iterate over Wavix models and process data
    # for models in wavix_models:
    #     # Filter Wavix data for today's timestamp
    #     wavix_data = models.objects.filter(timestamp__range=(today_start, today_end))
    #
    #     for wavix_entry in wavix_data:
    #         print("----------------", wavix_entry)
    #
    #         # Check if the phone number has already been processed globally
    #         if wavix_entry.number in processed_numbers:
    #             continue
    #
    #         # Mark the phone number as processed globally
    #         processed_numbers.add(wavix_entry.number)
    #
    #         # Find matching entries in CsvFileData
    #
    #         matching_csv_entries = CsvFileData.objects.filter(phonenumber=wavix_entry.number)
    #
    #         for csv_entry in matching_csv_entries:
    #             user = csv_entry.csvfile.user
    #
    #             # Add the unique phone number to the user's set
    #             user_wavix_counts[user].add(wavix_entry.number)
    #
    # # Calculate the count for each user
    # final_user_counts = {user: len(numbers) for user, numbers in user_wavix_counts.items()}
    #
    # # After processing all data, update the APICall models for each user
    # today = localdate()
    # with transaction.atomic():
    #     for user, wavix_value in final_user_counts.items():
    #         # Call the helper function to create or update the entry
    #         api_call = create_or_update_wavix_entry(user, wavix_value)
    #         print(f"User: {user}, Unique Wavix Count: {wavix_value}, APICall: {api_call}")


    # Enrichment Count
    enrichment_model = [DataEndato0, DataEndato1, DataEndato2, DataEndato3, DataEndato4, DataEndato5, DataEndato6,
                        DataEndato7, DataEndato8, DataEndato9]

    enrichment_count = sum(
        model.objects.filter(timestamp__range=(today_start, today_end)).count() for model in enrichment_model)

    processed_numbers = set()
    user_enrichment_counts = defaultdict(set)

    for model in enrichment_model:
        enrichment_data = model.objects.filter(timestamp__range=(today_start, today_end))

        # print("----------------- entering enrichment models")

        for enrichment_entry in enrichment_data:
            if enrichment_entry.number in processed_numbers:
                continue

            processed_numbers.add(enrichment_entry.number)

            # print('------- enrichment API check')
            matching_api_entries = EndatoApiResponse.objects.filter(
                phone_number=enrichment_entry.number,
                created_at__range=(today_start, today_end)
            )

            if matching_api_entries.exists():
                for api_entry in matching_api_entries:
                    # print('---- Enrichment API entry ---', api_entry)
                    # print("user test 2 ------ " , api_entry.userprofile)
                    user = api_entry.userprofile.user if api_entry.userprofile else None
                    # print("---------------- User --------", user)
                    if user:
                        user_enrichment_counts[user].add(enrichment_entry.number)

    final_user_counts = {user: len(numbers) for user, numbers in user_enrichment_counts.items()}

    today = localdate()
    with transaction.atomic():
        for user, enrichment_value in final_user_counts.items():
            api_call = create_or_update_dataenrich_entry(user, enrichment_value)
            print(f"User: {user}, Unique Enrichment Count: {enrichment_value}, APICall: {api_call}")

    # Create APICall object
    # APICall.objects.create(
    #     user=user,
    #     signalwire=signalwire_count,
    #     netnumbering=netnumbering_count,
    #     wavix=wavix_count,
    #     dataenrich=enrichment_count,
    # )

    current_datetime = datetime.datetime.now()
    print(f"Count Of API call for {current_datetime} has been updated .")
    return f"Count Of API call for {current_datetime} has been updated ."


