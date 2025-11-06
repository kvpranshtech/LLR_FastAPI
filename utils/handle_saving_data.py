from concurrent.futures import ThreadPoolExecutor
from django.utils.timezone import now
from django.core.paginator import Paginator

from utils._base import format_dnctype, csvdata_model_required_fields, csvemaildata_model_required_fields

from datastorage.models import (
    InvalidNumbersDataLogs, 

    TelynxNumbersDataLogs0,
    TelynxNumbersDataLogs1,
    TelynxNumbersDataLogs2,
    TelynxNumbersDataLogs3,
    TelynxNumbersDataLogs4,
    TelynxNumbersDataLogs5,
    TelynxNumbersDataLogs6,
    TelynxNumbersDataLogs7,
    TelynxNumbersDataLogs8,
    TelynxNumbersDataLogs9,

    SignalwireNumbersDataLogs0,
    SignalwireNumbersDataLogs1,
    SignalwireNumbersDataLogs2,
    SignalwireNumbersDataLogs3,
    SignalwireNumbersDataLogs4,
    SignalwireNumbersDataLogs5,
    SignalwireNumbersDataLogs6,
    SignalwireNumbersDataLogs7,
    SignalwireNumbersDataLogs8,
    SignalwireNumbersDataLogs9,

    NetNumberingDataLogs0,
    NetNumberingDataLogs1,
    NetNumberingDataLogs2,
    NetNumberingDataLogs3,
    NetNumberingDataLogs4,
    NetNumberingDataLogs5,
    NetNumberingDataLogs6,
    NetNumberingDataLogs7,
    NetNumberingDataLogs8,
    NetNumberingDataLogs9,

    WavixDataLogs0,
    WavixDataLogs1,
    WavixDataLogs2,
    WavixDataLogs3,
    WavixDataLogs4,
    WavixDataLogs5,
    WavixDataLogs6,
    WavixDataLogs7,
    WavixDataLogs8,
    WavixDataLogs9,


    DNCNumbersDataLogs0,
    DNCNumbersDataLogs1,
    DNCNumbersDataLogs2,
    DNCNumbersDataLogs3,
    DNCNumbersDataLogs4,
    DNCNumbersDataLogs5,
    DNCNumbersDataLogs6,
    DNCNumbersDataLogs7,
    DNCNumbersDataLogs8,
    DNCNumbersDataLogs9,

    UserDataLogs0,
    UserDataLogs1,
    UserDataLogs2,
    UserDataLogs3,
    UserDataLogs4,
    UserDataLogs5,
    UserDataLogs6,
    UserDataLogs7,
    UserDataLogs8,
    UserDataLogs9,

    DataEndato0,
    DataEndato1,
    DataEndato2,
    DataEndato3,
    DataEndato4,
    DataEndato5,
    DataEndato6,
    DataEndato7,
    DataEndato8,
    DataEndato9,

    UserDataLogsEndato0,
    UserDataLogsEndato1,
    UserDataLogsEndato2,
    UserDataLogsEndato3,
    UserDataLogsEndato4,
    UserDataLogsEndato5,
    UserDataLogsEndato6,
    UserDataLogsEndato7,
    UserDataLogsEndato8,
    UserDataLogsEndato9,
)
from api.models import APIData
from mdrdata.models import DNCNumberData
from uploadtoken.models import SignalwireNumberData, TelynxNumberData, InvalidNumberData
from core.models import CsvFile, CsvFileData,EndatoCsvFileData,EndatoApiResponse

from utils._base import format_dnctype, csvdata_model_required_fields,endato_csvdata_model_required_fields



# modified
def saveNetNumberingData(apidata):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """
    
    #storing into new table 
    try:
        number_starting_digit = apidata['number'][0]
    except:
        number_starting_digit = None

    try:
        dict_to_write = dict(
            number = apidata['number'],
            line_type = apidata['line_type'],
            carrier_name = str(apidata['carrier_name']).strip(),
            city = apidata['city'],
            state = apidata['state'],
            country = apidata['country']
        )
    except: 
        dict_to_write = None

    if dict_to_write is None or apidata['line_type'] == 'invalid': return

    try:
        if number_starting_digit == '0':
            NetNumberingDataLogs0.objects.create(**dict_to_write)
        elif number_starting_digit == '1':
            NetNumberingDataLogs1.objects.create(**dict_to_write)
        elif number_starting_digit == '2':
            NetNumberingDataLogs2.objects.create(**dict_to_write)
        elif number_starting_digit == '3':
            NetNumberingDataLogs3.objects.create(**dict_to_write)
        elif number_starting_digit == '4':
            NetNumberingDataLogs4.objects.create(**dict_to_write)
        elif number_starting_digit == '5':
            NetNumberingDataLogs5.objects.create(**dict_to_write)
        elif number_starting_digit == '6':
            NetNumberingDataLogs6.objects.create(**dict_to_write)
        elif number_starting_digit == '7':
            NetNumberingDataLogs7.objects.create(**dict_to_write)
        elif number_starting_digit == '8':
            NetNumberingDataLogs8.objects.create(**dict_to_write)
        elif number_starting_digit == '9':
            NetNumberingDataLogs9.objects.create(**dict_to_write)
    except:
        pass




# modified
def saveSignalwireData(apidata):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """
    
    #storing into new table 
    try:
        number_starting_digit = apidata['number'][0]
    except:
        number_starting_digit = None

    try:
        dict_to_write = dict(
            number = apidata['number'],
            line_type = apidata['line_type'],
            carrier_name = str(apidata['carrier_name']).strip(),
            city = apidata['city'],
            state = apidata['state'],
            country = apidata['country']
        )
    except: 
        dict_to_write = None

    if dict_to_write is None or apidata['line_type'] == 'invalid': return

    try:
        if number_starting_digit == '0':
            SignalwireNumbersDataLogs0.objects.create(**dict_to_write)
        elif number_starting_digit == '1':
            SignalwireNumbersDataLogs1.objects.create(**dict_to_write)
        elif number_starting_digit == '2':
            SignalwireNumbersDataLogs2.objects.create(**dict_to_write)
        elif number_starting_digit == '3':
            SignalwireNumbersDataLogs3.objects.create(**dict_to_write)
        elif number_starting_digit == '4':
            SignalwireNumbersDataLogs4.objects.create(**dict_to_write)
        elif number_starting_digit == '5':
            SignalwireNumbersDataLogs5.objects.create(**dict_to_write)
        elif number_starting_digit == '6':
            SignalwireNumbersDataLogs6.objects.create(**dict_to_write)
        elif number_starting_digit == '7':
            SignalwireNumbersDataLogs7.objects.create(**dict_to_write)
        elif number_starting_digit == '8':
            SignalwireNumbersDataLogs8.objects.create(**dict_to_write)
        elif number_starting_digit == '9':
            SignalwireNumbersDataLogs9.objects.create(**dict_to_write)
    except:
        pass




# modified
def saveWavixData(apidata):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """
    
    #storing into new table 
    try:
        number_starting_digit = apidata['number'][0]
    except:
        number_starting_digit = None

    try:
        dict_to_write = dict(
            number = apidata['number'],
            line_type = apidata['line_type'],
            carrier_name = str(apidata['carrier_name']).strip(),
            city = apidata['city'],
            state = apidata['state'],
            country = apidata['country']
        )
    except: 
        dict_to_write = None

    if dict_to_write is None or apidata['line_type'] == 'invalid': return

    try:
        if number_starting_digit == '0':
            WavixDataLogs0.objects.create(**dict_to_write)
        elif number_starting_digit == '1':
            WavixDataLogs1.objects.create(**dict_to_write)
        elif number_starting_digit == '2':
            WavixDataLogs2.objects.create(**dict_to_write)
        elif number_starting_digit == '3':
            WavixDataLogs3.objects.create(**dict_to_write)
        elif number_starting_digit == '4':
            WavixDataLogs4.objects.create(**dict_to_write)
        elif number_starting_digit == '5':
            WavixDataLogs5.objects.create(**dict_to_write)
        elif number_starting_digit == '6':
            WavixDataLogs6.objects.create(**dict_to_write)
        elif number_starting_digit == '7':
            WavixDataLogs7.objects.create(**dict_to_write)
        elif number_starting_digit == '8':
            WavixDataLogs8.objects.create(**dict_to_write)
        elif number_starting_digit == '9':
            WavixDataLogs9.objects.create(**dict_to_write)
    except Exception as e:
        print(f"ERROR SAVING DATA IN WAVIX - {e}")

def saveWavixDataV2(data_list):
    """
    - Takes a list of API data dictionaries.
    - Saves the data into the appropriate table in bulk based on the starting digit of the phone number.
    """
    wavix_data_logs_0 = []
    wavix_data_logs_1 = []
    wavix_data_logs_2 = []
    wavix_data_logs_3 = []
    wavix_data_logs_4 = []
    wavix_data_logs_5 = []
    wavix_data_logs_6 = []
    wavix_data_logs_7 = []
    wavix_data_logs_8 = []
    wavix_data_logs_9 = []

    for apidata in data_list:
        try:
            number_starting_digit = apidata['number'][0]
        except:
            number_starting_digit = None

        try:
            dict_to_write = dict(
                number=apidata['number'],
                line_type=apidata['line_type'],
                carrier_name=str(apidata['carrier_name']).strip(),
                city=apidata['city'],
                state=apidata['state'],
                country=apidata['country'],
                timestamp = now()
            )
        except KeyError:
            print(f"KeyError while preparing dict to write: {e}")
            dict_to_write = None

        if dict_to_write is None or apidata['line_type'] == 'invalid':
            print(f"{dict_to_write} DICT TO WRITE")

        try:
            if number_starting_digit == '0':
                wavix_data_logs_0.append(WavixDataLogs0(**dict_to_write))
            elif number_starting_digit == '1':
                wavix_data_logs_1.append(WavixDataLogs1(**dict_to_write))
            elif number_starting_digit == '2':
                wavix_data_logs_2.append(WavixDataLogs2(**dict_to_write))
            elif number_starting_digit == '3':
                wavix_data_logs_3.append(WavixDataLogs3(**dict_to_write))
            elif number_starting_digit == '4':
                wavix_data_logs_4.append(WavixDataLogs4(**dict_to_write))
            elif number_starting_digit == '5':
                wavix_data_logs_5.append(WavixDataLogs5(**dict_to_write))
            elif number_starting_digit == '6':
                wavix_data_logs_6.append(WavixDataLogs6(**dict_to_write))
            elif number_starting_digit == '7':
                wavix_data_logs_7.append(WavixDataLogs7(**dict_to_write))
            elif number_starting_digit == '8':
                wavix_data_logs_8.append(WavixDataLogs8(**dict_to_write))
            elif number_starting_digit == '9':
                wavix_data_logs_9.append(WavixDataLogs9(**dict_to_write))
        except Exception as e:
            print(f"Error adding data to respective lists: {e}")

    try:
        if wavix_data_logs_0:
            WavixDataLogs0.objects.bulk_create(wavix_data_logs_0)
        if wavix_data_logs_1:
            WavixDataLogs1.objects.bulk_create(wavix_data_logs_1)
        if wavix_data_logs_2:
            WavixDataLogs2.objects.bulk_create(wavix_data_logs_2)
        if wavix_data_logs_3:
            WavixDataLogs3.objects.bulk_create(wavix_data_logs_3)
        if wavix_data_logs_4:
            WavixDataLogs4.objects.bulk_create(wavix_data_logs_4)
        if wavix_data_logs_5:
            WavixDataLogs5.objects.bulk_create(wavix_data_logs_5)
        if wavix_data_logs_6:
            WavixDataLogs6.objects.bulk_create(wavix_data_logs_6)
        if wavix_data_logs_7:
            WavixDataLogs7.objects.bulk_create(wavix_data_logs_7)
        if wavix_data_logs_8:
            WavixDataLogs8.objects.bulk_create(wavix_data_logs_8)
        if wavix_data_logs_9:
            WavixDataLogs9.objects.bulk_create(wavix_data_logs_9)
    except Exception as e:
        print(f"Error during bulk insert: {e}")



#modified
def saveTelynxData(apidata):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """

    #storing into new table 
    try:
        number_starting_digit = apidata['number'][0]
    except:
        number_starting_digit = None

    try:
        dict_to_write = dict(
            number = apidata['number'],
            line_type = apidata['line_type'],
            carrier_name = str(apidata['carrier_name']).strip(),
            city = apidata['city'],
            state = apidata['state'],
            country = apidata['country']
        )
    except: 
        dict_to_write = None

    if dict_to_write is None or apidata['line_type'] == 'invalid': return

    try:
        if number_starting_digit == '0':
            TelynxNumbersDataLogs0.objects.create(**dict_to_write)
        elif number_starting_digit == '1':
            TelynxNumbersDataLogs1.objects.create(**dict_to_write)
        elif number_starting_digit == '2':
            TelynxNumbersDataLogs2.objects.create(**dict_to_write)
        elif number_starting_digit == '3':
            TelynxNumbersDataLogs3.objects.create(**dict_to_write)
        elif number_starting_digit == '4':
            TelynxNumbersDataLogs4.objects.create(**dict_to_write)
        elif number_starting_digit == '5':
            TelynxNumbersDataLogs5.objects.create(**dict_to_write)
        elif number_starting_digit == '6':
            TelynxNumbersDataLogs6.objects.create(**dict_to_write)
        elif number_starting_digit == '7':
            TelynxNumbersDataLogs7.objects.create(**dict_to_write)
        elif number_starting_digit == '8':
            TelynxNumbersDataLogs8.objects.create(**dict_to_write)
        elif number_starting_digit == '9':
            TelynxNumbersDataLogs9.objects.create(**dict_to_write)
    except:
        pass
        


#modified
def saveDNCData(apidata):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """

    #storing into new table 
    try:
        number_starting_digit = apidata['phonenumber'][0]
    except:
        number_starting_digit = None

    try:
        dict_to_write = dict(
            number = apidata['phonenumber'],
            dnc_type = 'n/a',
            dnc_type_original = apidata['dnc_type']
        )

        dnc_type = str(apidata['dnc_type']).lower()
        if 'tcpa' in dnc_type:
            dict_to_write['dnc_type'] = "litigator"
        elif 'dnc' in dnc_type:
            dict_to_write['dnc_type'] = "dnc"
        elif 'clean' in dnc_type:
            dict_to_write['dnc_type'] = "clean"
        else:
            dict_to_write['dnc_type'] = "n/a"
    except: 
        dict_to_write = None

    if dict_to_write is None: return 'n/a'

    try:
        if number_starting_digit == '0':
            DNCNumbersDataLogs0.objects.create(**dict_to_write)
        elif number_starting_digit == '1':
            DNCNumbersDataLogs1.objects.create(**dict_to_write)
        elif number_starting_digit == '2':
            DNCNumbersDataLogs2.objects.create(**dict_to_write)
        elif number_starting_digit == '3':
            DNCNumbersDataLogs3.objects.create(**dict_to_write)
        elif number_starting_digit == '4':
            DNCNumbersDataLogs4.objects.create(**dict_to_write)
        elif number_starting_digit == '5':
            DNCNumbersDataLogs5.objects.create(**dict_to_write)
        elif number_starting_digit == '6':
            DNCNumbersDataLogs6.objects.create(**dict_to_write)
        elif number_starting_digit == '7':
            DNCNumbersDataLogs7.objects.create(**dict_to_write)
        elif number_starting_digit == '8':
            DNCNumbersDataLogs8.objects.create(**dict_to_write)
        elif number_starting_digit == '9':
            DNCNumbersDataLogs9.objects.create(**dict_to_write)
    except:
        pass 
        

#util method for saveDNCData_Bulk
def updateDncModel(DjModel, objects_to_create):
    if len(objects_to_create) > 0:
        numbers_list = list(set([_.number for _ in objects_to_create]))
        numbers_list_already_exist = list(DjModel.objects.filter(number__in=numbers_list).values_list('number', flat=True))
        objects_to_create = [_ for _ in objects_to_create if not _.number in numbers_list_already_exist]
        DjModel.objects.bulk_create(objects_to_create, ignore_conflicts=True) 


def saveDNCData_Bulk(records_to_create):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """
    objects_to_create_0 = []
    objects_to_create_1 = []
    objects_to_create_2 = []
    objects_to_create_3 = []
    objects_to_create_4 = []
    objects_to_create_5 = []
    objects_to_create_6 = []
    objects_to_create_7 = []
    objects_to_create_8 = []
    objects_to_create_9 = []

    for number, org_type in records_to_create.items():
        org_type = org_type.replace(',','').strip()
        dict_to_write = dict(
            number = number,
            dnc_type = format_dnctype(org_type),
            dnc_type_original = org_type,
            timestamp = now()
        )

        number_starting_digit = number[0]
        if number_starting_digit == '0':
            objects_to_create_0.append(DNCNumbersDataLogs0(**dict_to_write))
        elif number_starting_digit == '1':
            objects_to_create_1.append(DNCNumbersDataLogs1(**dict_to_write))
        if number_starting_digit == '2':
            objects_to_create_2.append(DNCNumbersDataLogs2(**dict_to_write))
        elif number_starting_digit == '3':
            objects_to_create_3.append(DNCNumbersDataLogs3(**dict_to_write))
        elif number_starting_digit == '4':
            objects_to_create_4.append(DNCNumbersDataLogs4(**dict_to_write))
        elif number_starting_digit == '5':
            objects_to_create_5.append(DNCNumbersDataLogs5(**dict_to_write))
        elif number_starting_digit == '6':
            objects_to_create_6.append(DNCNumbersDataLogs6(**dict_to_write))
        elif number_starting_digit == '7':
            objects_to_create_7.append(DNCNumbersDataLogs7(**dict_to_write))
        elif number_starting_digit == '8':
            objects_to_create_8.append(DNCNumbersDataLogs8(**dict_to_write))
        elif number_starting_digit == '9':
            objects_to_create_9.append(DNCNumbersDataLogs9(**dict_to_write))

    updateDncModel(DNCNumbersDataLogs0, objects_to_create_0)
    updateDncModel(DNCNumbersDataLogs1, objects_to_create_1)
    updateDncModel(DNCNumbersDataLogs2, objects_to_create_2)
    updateDncModel(DNCNumbersDataLogs3, objects_to_create_3)
    updateDncModel(DNCNumbersDataLogs4, objects_to_create_4)
    updateDncModel(DNCNumbersDataLogs5, objects_to_create_5)
    updateDncModel(DNCNumbersDataLogs6, objects_to_create_6)
    updateDncModel(DNCNumbersDataLogs7, objects_to_create_7)
    updateDncModel(DNCNumbersDataLogs8, objects_to_create_8)
    updateDncModel(DNCNumbersDataLogs9, objects_to_create_9)
    

    return None



#modified july 23 - working
def saveInvalidNumberData(phone_clean):
    """
        - take 10 digit number
        - saving into invalid table incase all api return invalid data
    """
    #storing into new table 
    try:
        InvalidNumbersDataLogs.objects.create(number=phone_clean)
    except:
        pass 


    
# def saveAPIData(userprofile_obj, phone_clean, dnc_type, phone_data, added_through='api'):
#     try:
#         APIData.objects.get_or_create(
#             userprofile=userprofile_obj, 
#             phonenumber=phone_clean,
#             defaults = {
#                 "line_type" : phone_data.get('line_type'),
#                 "dnc_type" : dnc_type,
#                 "carrier_name" : phone_data.get('carrier_name'),
#                 "city" : phone_data.get('city'),
#                 "state" : phone_data.get('state'),
#                 "country" : phone_data.get('country'),
#                 "added_through" : added_through
#             }
#         )
#     except: 
#         pass


def saveAPIData(userprofile_obj, phone_clean, dnc_type, phone_data, added_through='api'):
    try:
        obj, created = APIData.objects.get_or_create(
            userprofile=userprofile_obj,
            phonenumber=phone_clean,
            defaults={
                "line_type": phone_data.get('line_type', 'invalid'),
                "dnc_type": dnc_type,
                "carrier_name": phone_data.get('carrier_name', 'n/a'),
                "city": phone_data.get('city', 'n/a'),
                "state": phone_data.get('state', 'n/a'),
                "country": phone_data.get('country', 'n/a'),
                "added_through": added_through,
                'number_checked_from_db':phone_data.get('found_from_db',False)
            }
        )
        if not created:
            # Update fields if the object already exists
            obj.line_type = phone_data.get('line_type', 'invalid')
            obj.dnc_type = dnc_type
            obj.carrier_name = phone_data.get('carrier_name', 'n/a')
            obj.city = phone_data.get('city', 'n/a')
            obj.state = phone_data.get('state', 'n/a')
            obj.country = phone_data.get('country', 'n/a')
            obj.added_through = added_through
            obj.number_checked_from_db = phone_data.get('found_from_db',False)
            obj.save()
    except Exception as e:
        print(f"Error saving APIData: {e}")




def saveAPIDataEndato(userprofile_obj, phone_clean, enriched_data, added_through='api'):
    try:
        obj, created = EndatoApiResponse.objects.get_or_create(
            userprofile=userprofile_obj,
            phone_number=phone_clean,
            defaults={
                "first_name": enriched_data.get('first_name', 'n/a'),
                "last_name": enriched_data.get('last_name', 'n/a'),
                "age": enriched_data.get('age', 'n/a'),
                "addresses": enriched_data.get('addresses', 'n/a'),
                "phones": enriched_data.get('phones', 'n/a'),
                "emails": enriched_data.get('emails', 'n/a'),
                "added_through": added_through,
                'data_enrichment_checked_from_db':enriched_data.get('found_in_db', 'n/a'),
            }
        )
        if not created:
            # Update fields if the object already exists
            obj.first_name = enriched_data.get('first_name', 'n/a')
            obj.last_name = enriched_data.get('last_name', 'n/a')
            obj.age = enriched_data.get('age', 'n/a')
            obj.addresses = enriched_data.get('addresses', 'n/a')
            obj.phones = enriched_data.get('phones', 'n/a')
            obj.emails =enriched_data.get('emails', 'n/a')
            obj.added_through = added_through
            obj.data_enrichment_checked_from_db = enriched_data.get('found_in_db', 'n/a')
            obj.save()
    except Exception as e:
        print(f"Error saving APIData: {e}")





# util method for saveUserCheckedDataIntoLogsTable
def util_updateUserDataLogsModel(DjModel, user_obj, objects_to_create):
    if len(objects_to_create) > 0:
        numbers_list = list(set([_.number for _ in objects_to_create]))
        numbers_list_already_exist = list(DjModel.objects.filter(user=user_obj, number__in=numbers_list).values_list('number', flat=True))
        objects_to_create = [_ for _ in objects_to_create if not _.number in numbers_list_already_exist]
        DjModel.objects.bulk_create(objects_to_create, ignore_conflicts=True) #batch_size=1000, 


def saveUserCheckedDataIntoLogsTable(file_uid,checkprrows=False):
    """
        - updated at aug 2023 | no more modification needed
        - take file id after successfully generated (charged & completed)
        - grab numbers and it's all relevant info
        - save into user data log table
        - helps for reuse and return credits the duplicate numbers
        - helps to minimize the table size
        - specifically build for bulk file upload option
    """
    csvfile_obj = CsvFile.objects.get(uid=file_uid)
    current_user = csvfile_obj.user 
    
    if checkprrows:
        distinct_queryset = CsvFileData.objects.filter(csvfile=csvfile_obj,is_processed=True).exclude(phonenumber='invalid_data').values(*csvdata_model_required_fields).order_by('phonenumber').distinct('phonenumber')
    else:
        distinct_queryset = CsvFileData.objects.filter(csvfile=csvfile_obj).exclude(phonenumber='invalid_data').values(*csvdata_model_required_fields).order_by('phonenumber').distinct('phonenumber')    

    paginator = Paginator(distinct_queryset, 2000)

    for page in range(1, paginator.num_pages+1):
        objects_list = paginator.page(page).object_list
        objects_to_create_0 = []
        objects_to_create_1 = []
        objects_to_create_2 = []
        objects_to_create_3 = []
        objects_to_create_4 = []
        objects_to_create_5 = []
        objects_to_create_6 = []
        objects_to_create_7 = []
        objects_to_create_8 = []
        objects_to_create_9 = []

        def updateObjData(obj):
            number_starting_digit = obj['phonenumber'][0]
            dict_to_create = dict(
                user = current_user, 
                number = obj['phonenumber'], 
                line_type = obj['line_type'],
                dnc_type = str(obj['dnc_type']).lower(),
                carrier_name = str(obj['carrier_name']).lower(),
                city = str(obj['city']).lower(),
                state = str(obj['state']).lower(),
                country = str(obj['country']).lower(),
                timestamp = csvfile_obj.uploaded_at
            )
            
            if number_starting_digit == '0':
                objects_to_create_0.append(UserDataLogs0(**dict_to_create))
            elif number_starting_digit == '1':
                objects_to_create_1.append(UserDataLogs1(**dict_to_create))
            if number_starting_digit == '2':
                objects_to_create_2.append(UserDataLogs2(**dict_to_create))
            elif number_starting_digit == '3':
                objects_to_create_3.append(UserDataLogs3(**dict_to_create))
            elif number_starting_digit == '4':
                objects_to_create_4.append(UserDataLogs4(**dict_to_create))
            elif number_starting_digit == '5':
                objects_to_create_5.append(UserDataLogs5(**dict_to_create))
            elif number_starting_digit == '6':
                objects_to_create_6.append(UserDataLogs6(**dict_to_create))
            elif number_starting_digit == '7':
                objects_to_create_7.append(UserDataLogs7(**dict_to_create))
            elif number_starting_digit == '8':
                objects_to_create_8.append(UserDataLogs8(**dict_to_create))
            elif number_starting_digit == '9':
                objects_to_create_9.append(UserDataLogs9(**dict_to_create))

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(updateObjData, objects_list)

        util_updateUserDataLogsModel(UserDataLogs0, current_user, objects_to_create_0)
        util_updateUserDataLogsModel(UserDataLogs1, current_user, objects_to_create_1)
        util_updateUserDataLogsModel(UserDataLogs2, current_user, objects_to_create_2)
        util_updateUserDataLogsModel(UserDataLogs3, current_user, objects_to_create_3)
        util_updateUserDataLogsModel(UserDataLogs4, current_user, objects_to_create_4)
        util_updateUserDataLogsModel(UserDataLogs5, current_user, objects_to_create_5)
        util_updateUserDataLogsModel(UserDataLogs6, current_user, objects_to_create_6)
        util_updateUserDataLogsModel(UserDataLogs7, current_user, objects_to_create_7)
        util_updateUserDataLogsModel(UserDataLogs8, current_user, objects_to_create_8)
        util_updateUserDataLogsModel(UserDataLogs9, current_user, objects_to_create_9)

    return None



from django.apps import apps


def saveUserCheckedDataIntoEndatoLogsTable(file_uid,DjModel,checkprrows=False):
    
    try:
        csvfile_obj = CsvFile.objects.get(uid=file_uid)
        current_user = csvfile_obj.user 
        
        ModelClass = apps.get_model('core', DjModel)

        if checkprrows:
            distinct_queryset = ModelClass.objects.filter(csvfile=csvfile_obj,is_processed=True).exclude(phonenumber='invalid_data').values(*endato_csvdata_model_required_fields).order_by('phonenumber').distinct('phonenumber')
        else:
            distinct_queryset = ModelClass.objects.filter(csvfile=csvfile_obj).exclude(phonenumber='invalid_data').values(*endato_csvdata_model_required_fields).order_by('phonenumber').distinct('phonenumber')    
        
        paginator = Paginator(distinct_queryset, 2000)

        for page in range(1, paginator.num_pages+1):
            objects_list = paginator.page(page).object_list
            objects_to_create_0 = []
            objects_to_create_1 = []
            objects_to_create_2 = []
            objects_to_create_3 = []
            objects_to_create_4 = []
            objects_to_create_5 = []
            objects_to_create_6 = []
            objects_to_create_7 = []
            objects_to_create_8 = []
            objects_to_create_9 = []

            def updateObjData(obj):
                number_starting_digit = obj['phonenumber'][0]
                dict_to_create = dict(
                    user = current_user, 
                    number = obj['phonenumber'], 
                    first_name = obj['first_name'],
                    last_name = obj['last_name'],
                    age = obj['age'],
                    addresses = obj['addresses'],
                    phones = obj['phones'],
                    emails = obj['emails'],
                    # identityScore = obj['identityScore'],
                    timestamp = csvfile_obj.uploaded_at
                )
                
                if number_starting_digit == '0':
                    objects_to_create_0.append(UserDataLogsEndato0(**dict_to_create))
                elif number_starting_digit == '1':
                    objects_to_create_1.append(UserDataLogsEndato1(**dict_to_create))
                if number_starting_digit == '2':
                    objects_to_create_2.append(UserDataLogsEndato2(**dict_to_create))
                elif number_starting_digit == '3':
                    objects_to_create_3.append(UserDataLogsEndato3(**dict_to_create))
                elif number_starting_digit == '4':
                    objects_to_create_4.append(UserDataLogsEndato4(**dict_to_create))
                elif number_starting_digit == '5':
                    objects_to_create_5.append(UserDataLogsEndato5(**dict_to_create))
                elif number_starting_digit == '6':
                    objects_to_create_6.append(UserDataLogsEndato6(**dict_to_create))
                elif number_starting_digit == '7':
                    objects_to_create_7.append(UserDataLogsEndato7(**dict_to_create))
                elif number_starting_digit == '8':
                    objects_to_create_8.append(UserDataLogsEndato8(**dict_to_create))
                elif number_starting_digit == '9':
                    objects_to_create_9.append(UserDataLogsEndato9(**dict_to_create))

            with ThreadPoolExecutor(max_workers=20) as executor:
                executor.map(updateObjData, objects_list)

            util_updateUserDataLogsModel(UserDataLogsEndato0, current_user, objects_to_create_0)
            util_updateUserDataLogsModel(UserDataLogsEndato1, current_user, objects_to_create_1)
            util_updateUserDataLogsModel(UserDataLogsEndato2, current_user, objects_to_create_2)
            util_updateUserDataLogsModel(UserDataLogsEndato3, current_user, objects_to_create_3)
            util_updateUserDataLogsModel(UserDataLogsEndato4, current_user, objects_to_create_4)
            util_updateUserDataLogsModel(UserDataLogsEndato5, current_user, objects_to_create_5)
            util_updateUserDataLogsModel(UserDataLogsEndato6, current_user, objects_to_create_6)
            util_updateUserDataLogsModel(UserDataLogsEndato7, current_user, objects_to_create_7)
            util_updateUserDataLogsModel(UserDataLogsEndato8, current_user, objects_to_create_8)
            util_updateUserDataLogsModel(UserDataLogsEndato9, current_user, objects_to_create_9)

        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")












# modified
def saveEndatoData(apidata):
    """
        - taking api data from api endpoint
        - saving into table for next use
    """
    
    #storing into new table 
    try:
        number_starting_digit = apidata['number'][0]
    except:
        number_starting_digit = None

    try:
        dict_to_write = dict(
            number = apidata['number'],
            first_name = apidata['first_name'],
            last_name = apidata['last_name'],
            age = apidata['age'],
            addresses = apidata['addresses'],
            phones = apidata['phones'],
            emails = apidata['emails'],
            # identityScore = apidata['identityScore']
        )
    except: 
        dict_to_write = None
    

    if dict_to_write is None or (apidata['first_name'] == 'n/a' and apidata['last_name'] == 'n/a' and apidata['age'] == 'n/a' and apidata['addresses'] == 'n/a' and apidata['phones'] == 'n/a' and apidata['emails']  == 'n/a')  : return
    try:
        if number_starting_digit == '0':
            DataEndato0.objects.create(**dict_to_write)
        elif number_starting_digit == '1':
            DataEndato1.objects.create(**dict_to_write)
        elif number_starting_digit == '2':
            DataEndato2.objects.create(**dict_to_write)
        elif number_starting_digit == '3':
            DataEndato3.objects.create(**dict_to_write)
        elif number_starting_digit == '4':
            DataEndato4.objects.create(**dict_to_write)
        elif number_starting_digit == '5':
            DataEndato5.objects.create(**dict_to_write)
        elif number_starting_digit == '6':
            DataEndato6.objects.create(**dict_to_write)
        elif number_starting_digit == '7':
            DataEndato7.objects.create(**dict_to_write)
        elif number_starting_digit == '8':
            DataEndato8.objects.create(**dict_to_write)
        elif number_starting_digit == '9':
            DataEndato9.objects.create(**dict_to_write)
    except Exception as e:
            print(f"An error occurred while updating Endoto data: {e}")





from api.models import CsvFileEmail, CsvFileDataEmail
def saveUserEmailCheckedDataIntoLogsTable(file_uid, checkprrows=False):
    """
        - updated at aug 2023 | no more modification needed
        - take file id after successfully generated (charged & completed)
        - grab numbers and it's all relevant info
        - save into user data log table
        - helps for reuse and return credits the duplicate numbers
        - helps to minimize the table size
        - specifically build for bulk file upload option
    """
    csvfile_obj = CsvFileEmail.objects.get(uid=file_uid)
    current_user = csvfile_obj.user

    if checkprrows:
        distinct_queryset = CsvFileDataEmail.objects.filter(csvfile=csvfile_obj, is_processed=True).exclude(
            email='invalid_data').values(*csvemaildata_model_required_fields).order_by('email').distinct(
            'email')
    else:
        distinct_queryset = CsvFileDataEmail.objects.filter(csvfile=csvfile_obj).exclude(email='invalid_data').values(
            *csvemaildata_model_required_fields).order_by('email').distinct('email')

    paginator = Paginator(distinct_queryset, 2000)

    for page in range(1, paginator.num_pages + 1):
        objects_list = paginator.page(page).object_list
        objects_to_create_0 = []
        objects_to_create_1 = []
        objects_to_create_2 = []
        objects_to_create_3 = []
        objects_to_create_4 = []
        objects_to_create_5 = []
        objects_to_create_6 = []
        objects_to_create_7 = []
        objects_to_create_8 = []
        objects_to_create_9 = []

        def updateObjData(obj):
            number_starting_digit = obj['phonenumber'][0]
            dict_to_create = dict(
                user=current_user,
                number=obj['phonenumber'],
                line_type=obj['line_type'],
                dnc_type=str(obj['dnc_type']).lower(),
                carrier_name=str(obj['carrier_name']).lower(),
                city=str(obj['city']).lower(),
                state=str(obj['state']).lower(),
                country=str(obj['country']).lower(),
                timestamp=csvfile_obj.uploaded_at
            )

            if number_starting_digit == '0':
                objects_to_create_0.append(UserDataLogs0(**dict_to_create))
            elif number_starting_digit == '1':
                objects_to_create_1.append(UserDataLogs1(**dict_to_create))
            if number_starting_digit == '2':
                objects_to_create_2.append(UserDataLogs2(**dict_to_create))
            elif number_starting_digit == '3':
                objects_to_create_3.append(UserDataLogs3(**dict_to_create))
            elif number_starting_digit == '4':
                objects_to_create_4.append(UserDataLogs4(**dict_to_create))
            elif number_starting_digit == '5':
                objects_to_create_5.append(UserDataLogs5(**dict_to_create))
            elif number_starting_digit == '6':
                objects_to_create_6.append(UserDataLogs6(**dict_to_create))
            elif number_starting_digit == '7':
                objects_to_create_7.append(UserDataLogs7(**dict_to_create))
            elif number_starting_digit == '8':
                objects_to_create_8.append(UserDataLogs8(**dict_to_create))
            elif number_starting_digit == '9':
                objects_to_create_9.append(UserDataLogs9(**dict_to_create))

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(updateObjData, objects_list)

        util_updateUserDataLogsModel(UserDataLogs0, current_user, objects_to_create_0)
        util_updateUserDataLogsModel(UserDataLogs1, current_user, objects_to_create_1)
        util_updateUserDataLogsModel(UserDataLogs2, current_user, objects_to_create_2)
        util_updateUserDataLogsModel(UserDataLogs3, current_user, objects_to_create_3)
        util_updateUserDataLogsModel(UserDataLogs4, current_user, objects_to_create_4)
        util_updateUserDataLogsModel(UserDataLogs5, current_user, objects_to_create_5)
        util_updateUserDataLogsModel(UserDataLogs6, current_user, objects_to_create_6)
        util_updateUserDataLogsModel(UserDataLogs7, current_user, objects_to_create_7)
        util_updateUserDataLogsModel(UserDataLogs8, current_user, objects_to_create_8)
        util_updateUserDataLogsModel(UserDataLogs9, current_user, objects_to_create_9)

    return None
  