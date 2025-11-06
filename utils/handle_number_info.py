#django imports
from django.core.exceptions import MultipleObjectsReturned
from functools import reduce
from django.utils import timezone
from site_settings.models import ApiPriorities
from utils.handle_EndatoApi import API_Endato
from utils.handle_wavix_bulk_api import API_WAVIX_BULK
from utils.handle_PersonSearchAPI import API_PersonSearch
from django.db.models import Sum

from datetime import timedelta
from django.utils.timezone import now
# import models
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
    UserDataLogsEndato9, OneYearOldData,

)
from django.db.models import Sum
from api.models import CsvFileEmail

from api.models import (
    StartWithA, StartWithB, StartWithC, StartWithD, StartWithE,
    StartWithF, StartWithG, StartWithH, StartWithI, StartWithJ,
    StartWithK, StartWithL, StartWithM, StartWithN, StartWithO,
    StartWithP, StartWithQ, StartWithR, StartWithS, StartWithT,
    StartWithU, StartWithV, StartWithW, StartWithX, StartWithY, StartWithZ
)


from api.models import APIData
from core.models import CsvFile,CsvFileData,CheckEndatoApi,EndatoApiResponse,CreditAnalytics

# import utils
from utils.handle_dnctcpa_split import API_DNCTCPA_SPLIT
from utils.handle_saving_data import (saveSignalwireData, saveTelynxData, saveWavixData,
                                      saveDNCData, saveInvalidNumberData, saveDNCData_Bulk, saveNetNumberingData,saveEndatoData,saveWavixDataV2)
from utils.handle_signalwire import API_Singalwire
from utils.handle_telynx import API_TELNYX
from utils.handle_dnctcpa import API_TcpaLitigatorlist
from utils.handle_netnumbering import API_NetNumbering
from utils.handle_wavix import API_Wavix
from utils._base import format_dnctype, returnCleanCarrierName,endato_apidata_model_required_fields,endato_userdatalogs_model_required_fields



from utils._base import (
    apidata_model_required_fields, 
    userdatalogs_model_required_fields
)

number_fields_list = ('number', 'line_type', 'carrier_name', 'city', 'state', 'country')
number_fields_list_two = ('number', 'line_type', 'carrier_name', 'city', 'state', 'country','timestamp')
endato_number_fields_list = ('number','first_name','last_name','age','addresses','phones','emails')
dnc_number_fields_list = ('number', 'dnc_type')


# util of util method - handle get or filter number on models
def util_get_or_filter_number_exist(clean_phone, DjModel):
    try:
        oneNumber = DjModel.objects.values(*number_fields_list).get(number=clean_phone)
    except MultipleObjectsReturned:
        oneNumber = DjModel.objects.filter(number=clean_phone).values(*number_fields_list)
        if oneNumber:
            oneNumber = oneNumber[0]
    except:
        oneNumber = {}
    if oneNumber:
        update_date_after_1_year(oneNumber,DjModel)
    return oneNumber


# util of util method - handle get or filter number on models
def util_get_or_filter_number_exist_endato(clean_phone, DjModel):
    try:
        oneNumber = DjModel.objects.values(*endato_number_fields_list).get(number=clean_phone)
    except MultipleObjectsReturned:
        oneNumber = DjModel.objects.filter(number=clean_phone).values(*endato_number_fields_list)
        if oneNumber:
            oneNumber = oneNumber[0]
    except:
        oneNumber = {}
    return oneNumber


# util of util method - handle get or filter number on DNC Model
def util_get_or_filter_number_exist_dnc_models(clean_phone, DjModel):
    try:
        oneNumber = DjModel.objects.values(*dnc_number_fields_list).get(number=clean_phone)
    except MultipleObjectsReturned:
        oneNumber = DjModel.objects.filter(number=clean_phone).values(*dnc_number_fields_list)
        if oneNumber:
            oneNumber = oneNumber[0]
    except:
        oneNumber = {}
    return oneNumber


# util helping method - check if number exist in telynx tables
def NetNumbering_CheckNumberDataThroughDatabase(clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs0)
    elif number_starting_digit == '1':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs1)
    elif number_starting_digit == '2':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs2)
    elif number_starting_digit == '3':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs3)
    elif number_starting_digit == '4':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs4)
    elif number_starting_digit == '5':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs5)
    elif number_starting_digit == '6':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs6)
    elif number_starting_digit == '7':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs7)
    elif number_starting_digit == '8':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs8)
    elif number_starting_digit == '9':
        oneNumber = util_get_or_filter_number_exist(clean_phone, NetNumberingDataLogs9)
    return oneNumber


# util helping method - check number through api and save into table if found
def NetNumbering_CheckNumberDataThroughAPI(clean_phone):
    apidata = API_NetNumbering(clean_phone)
    if apidata['line_type'] != 'invalid':
        saveNetNumberingData(apidata)
        return apidata
    return {}


# util helping method - check if number exist in telynx tables
def Telynx_CheckNumberDataThroughDatabase(clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs0)
    elif number_starting_digit == '1':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs1)
    elif number_starting_digit == '2':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs2)
    elif number_starting_digit == '3':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs3)
    elif number_starting_digit == '4':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs4)
    elif number_starting_digit == '5':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs5)
    elif number_starting_digit == '6':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs6)
    elif number_starting_digit == '7':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs7)
    elif number_starting_digit == '8':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs8)
    elif number_starting_digit == '9':
        oneNumber = util_get_or_filter_number_exist(clean_phone, TelynxNumbersDataLogs9)
    return oneNumber


# util helping method - check number through api and save into table if found
def Telynx_CheckNumberDataThroughAPI(clean_phone):
    apidata = API_TELNYX(clean_phone)
    if apidata['line_type'] != 'invalid':
        saveTelynxData(apidata)
        apidata.pop('data', None) #pop out data key to save memory
        return apidata
    return {}

 
# util helping method - check if number exist in signalwire tables
def Signalwire_CheckNumberDataThroughDatabase(clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs0)
    elif number_starting_digit == '1':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs1)
    elif number_starting_digit == '2':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs2)
    elif number_starting_digit == '3':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs3)
    elif number_starting_digit == '4':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs4)
    elif number_starting_digit == '5':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs5)
    elif number_starting_digit == '6':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs6)
    elif number_starting_digit == '7':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs7)
    elif number_starting_digit == '8':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs8)
    elif number_starting_digit == '9':
        oneNumber = util_get_or_filter_number_exist(clean_phone, SignalwireNumbersDataLogs9)
    return oneNumber


# util helping method - check number through api and save into table if found
def Signalwire_CheckNumberDataThroughAPI(clean_phone):
    apidata = API_Singalwire(clean_phone)
    if apidata['line_type'] != 'invalid':
        saveSignalwireData(apidata)
        apidata.pop('data', None) #pop out data key to save memory
        return apidata
    return {}


"""util helping method - check if number exist in Wavix tables
   new method added on 08-10-2024
"""
def Wavix_CheckNumberDataThroughDatabase(clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs0)
    elif number_starting_digit == '1':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs1)
    elif number_starting_digit == '2':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs2)
    elif number_starting_digit == '3':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs3)
    elif number_starting_digit == '4':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs4)
    elif number_starting_digit == '5':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs5)
    elif number_starting_digit == '6':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs6)
    elif number_starting_digit == '7':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs7)
    elif number_starting_digit == '8':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs8)
    elif number_starting_digit == '9':
        oneNumber = util_get_or_filter_number_exist(clean_phone, WavixDataLogs9)
    return oneNumber


# util helping method - check number through api and save into table if found
def Wavix_CheckNumberDataThroughAPI(clean_phone):
    apidata = API_Wavix(clean_phone)
    if apidata['line_type'] not in ['invalid', '', 'n/a','unknown']:
        saveWavixData(apidata)
        return apidata
    return {}


# util helping method - check if number exist in dnc tables
def DNC_CheckNumberDataThroughDatabase(clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs0)
    elif number_starting_digit == '1':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs1)
    elif number_starting_digit == '2':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs2)
    elif number_starting_digit == '3':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs3)
    elif number_starting_digit == '4':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs4)
    elif number_starting_digit == '5':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs5)
    elif number_starting_digit == '6':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs6)
    elif number_starting_digit == '7':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs7)
    elif number_starting_digit == '8':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs8)
    elif number_starting_digit == '9':
        oneNumber = util_get_or_filter_number_exist_dnc_models(clean_phone, DNCNumbersDataLogs9)
    return oneNumber


# util helping method - check number through api and save into table if found
def DNC_CheckNumberDataThroughAPI(clean_phone):
    apidata = API_TcpaLitigatorlist(clean_phone)
    if apidata['dnc_type'] !='clean':
        saveDNCData(apidata)
    return apidata


# util helping method - check if number exist in dnc tables
def UserDataLogs_CheckNumberDataThroughDatabase(user_obj, clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = UserDataLogs0.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)
    elif number_starting_digit == '1':
        oneNumber = UserDataLogs1.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)    
    elif number_starting_digit == '2':
        oneNumber = UserDataLogs2.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)    
    elif number_starting_digit == '3':
        oneNumber = UserDataLogs3.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)        
    elif number_starting_digit == '4':
        oneNumber = UserDataLogs4.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)        
    elif number_starting_digit == '5':
        oneNumber = UserDataLogs5.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)        
    elif number_starting_digit == '6':
        oneNumber = UserDataLogs6.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)        
    elif number_starting_digit == '7':
        oneNumber = UserDataLogs7.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)        
    elif number_starting_digit == '8':
        oneNumber = UserDataLogs8.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)        
    elif number_starting_digit == '9':
        oneNumber = UserDataLogs9.objects.filter(user=user_obj, number=clean_phone).values(*userdatalogs_model_required_fields)      
        
    if oneNumber: 
        return oneNumber[0]
    return None







def Endato_UserDataLogs_CheckNumberDataThroughDatabase(user_obj, clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = UserDataLogsEndato0.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)
    elif number_starting_digit == '1':
        oneNumber = UserDataLogsEndato1.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)    
    elif number_starting_digit == '2':
        oneNumber = UserDataLogsEndato2.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)    
    elif number_starting_digit == '3':
        oneNumber = UserDataLogsEndato3.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)        
    elif number_starting_digit == '4':
        oneNumber = UserDataLogsEndato4.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)        
    elif number_starting_digit == '5':
        oneNumber = UserDataLogsEndato5.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)        
    elif number_starting_digit == '6':
        oneNumber = UserDataLogsEndato6.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)        
    elif number_starting_digit == '7':
        oneNumber = UserDataLogsEndato7.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)        
    elif number_starting_digit == '8':
        oneNumber = UserDataLogsEndato8.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)        
    elif number_starting_digit == '9':
        oneNumber = UserDataLogsEndato9.objects.filter(user=user_obj, number=clean_phone).values(*endato_userdatalogs_model_required_fields)      
        
    if oneNumber: 
        return oneNumber[0]
    return None











# util helping method - check if number exist in invalid table
def Invalid_CheckNumberDataThroughDatabase(clean_phone):
    try:
        oneNumber = InvalidNumbersDataLogs.objects.values('number').get(number=clean_phone)
    except:
        oneNumber = {}
    return oneNumber


api_function_mapping = {
    "NetNumbering_CheckNumberDataThroughAPI": NetNumbering_CheckNumberDataThroughAPI,
    # "Wavix_CheckNumberDataThroughAPI": Wavix_CheckNumberDataThroughAPI,
    "Signalwire_CheckNumberDataThroughAPI": Signalwire_CheckNumberDataThroughAPI,
}

from utils.handle_email_info import API_EmailValidation
def returnEmailData_v3(clean_email, shuffle=False):
    """
    - It will take a 10-digit phone number and check tables for full info or get from APIs.
    - Save API data into the table if not found in the table.
    - Return a dictionary of data or empty {}.
    """
    clean_email = str(clean_email).strip()

    email_data = API_EmailValidation(clean_email)
    if email_data:
        return email_data


"""modify method returnNumberData_v3 on 08/10/2024
   added wavix api integration and dynamic api calling priority according to admin selection
"""
def returnNumberData_v3(clean_phone,shuffle=False):
    """
    - It will take a 10-digit phone number and check tables for full info or get from APIs.
    - Save API data into the table if not found in the table.
    - Return a dictionary of data or empty {}.
    """
    clean_phone = str(clean_phone).strip()

    phone_data = Wavix_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data: 
        phone_data['found_from_db'] = True
        return phone_data

    phone_data = NetNumbering_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data: 
        phone_data['found_from_db'] = True
        return phone_data

    phone_data = Signalwire_CheckNumberDataThroughDatabase(clean_phone) 
    if phone_data:
        phone_data['found_from_db'] = True 
        return phone_data

    phone_data = Invalid_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data: 
        return {}

    current_priority = ApiPriorities.objects.first()

    # if current_priority and current_priority.api_first_priority == ApiPriorities.APITYPE_FIRST_PRIORITY.WAVIX and current_priority.wavix_bulk_check_api:
    #    return {}    
    
    if current_priority:
        first_priority_function = api_function_mapping.get(current_priority.api_first_priority)
        if first_priority_function:
            phone_data = first_priority_function(clean_phone)
            if phone_data:
                phone_data['found_from_db'] = False
                return phone_data
        
        if current_priority.api_second_priority == ApiPriorities.APITYPE_SECOND_PRIORITY.SIGNALWIRE:

            if current_priority.signalwire_status == True:
                second_priority_function = api_function_mapping.get(current_priority.api_second_priority)
                if second_priority_function:
                    phone_data = second_priority_function(clean_phone)
                    if phone_data:
                        phone_data['found_from_db'] = False
                        return phone_data
                
                # default_priority_function = api_function_mapping.get(current_priority.fallback)
                # if default_priority_function:
                #     phone_data = default_priority_function(clean_phone)
                #     if phone_data:
                #         phone_data['found_from_db'] = False
                #         return phone_data
        else:
                second_priority_function = api_function_mapping.get(current_priority.api_second_priority)
                if second_priority_function:
                    phone_data = second_priority_function(clean_phone)
                    if phone_data:
                        phone_data['found_from_db'] = False
                        return phone_data
                
                # default_priority_function = api_function_mapping.get(current_priority.fallback)
                # if default_priority_function:
                #     phone_data = default_priority_function(clean_phone)
                #     if phone_data:
                #         phone_data['found_from_db'] = False
                #         return phone_data

        # phone_data = Signalwire_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data
        
        # phone_data = NetNumbering_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data

    else:
        print("No Api Priorities found")
        # phone_data = Signalwire_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data
    
    return {}


def returnNumberData_v4(clean_phone_list):
    founded_number = []
    print("Starting returnNumberData_v4 with phone list")
    """
    - It will take a 10-digit phone number and check tables for full info or get from APIs.
    - Save API data into the table if not found in the table.
    - Return a dictionary of data or empty {}.
    """
    for clean_phone in clean_phone_list:
        clean_phone = str(clean_phone).strip()
        phone_data = Wavix_CheckNumberDataThroughDatabase(clean_phone)
        if phone_data: 
            founded_number.append(phone_data.get('number'))
            continue

        phone_data = NetNumbering_CheckNumberDataThroughDatabase(clean_phone)
        if phone_data: 
            founded_number.append(phone_data.get('number'))
            continue

        phone_data = Signalwire_CheckNumberDataThroughDatabase(clean_phone) 
        if phone_data: 
            founded_number.append(phone_data.get('number'))
            continue

        phone_data = Invalid_CheckNumberDataThroughDatabase(clean_phone)
        if phone_data: 
            founded_number.append(phone_data.get('number'))
            continue
        
    unique_NUMBERS = list(set(clean_phone_list) ^ set(founded_number))   
        
    return unique_NUMBERS
 

# new callable method - working fine
def returnNumberDncData_v3(clean_phone):
    clean_phone = str(clean_phone).strip()

    # phone_data = DNC_CheckNumberDataThroughDatabase(clean_phone) 
    # if phone_data:
    #     return phone_data['dnc_type']

    phone_data = DNC_CheckNumberDataThroughAPI(clean_phone)
    if phone_data:
        return format_dnctype(phone_data['dnc_type'])
    return 'n/a'


def returnNumberData_v5(clean_phone, shuffle=False):
    """
    - It will take a 10-digit phone number and check tables for full info or get from APIs.
    - Save API data into the table if not found in the table.
    - Return a dictionary of data or empty {}.
    """
    clean_phone = str(clean_phone).strip()

    phone_data = NetNumbering_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data:
        return phone_data

    phone_data = Signalwire_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data:
        return phone_data

    phone_data = Wavix_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data:
        return phone_data

    phone_data = Invalid_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data:
        return {}

    current_priority = ApiPriorities.objects.first()

    if current_priority:
        first_priority_function = api_function_mapping.get(current_priority.api_first_priority)
        if first_priority_function:
            phone_data = first_priority_function(clean_phone)
            if phone_data:
                return phone_data

        if current_priority.api_second_priority == ApiPriorities.APITYPE_SECOND_PRIORITY.SIGNALWIRE:

            if current_priority.signalwire_status == True:
                second_priority_function = api_function_mapping.get(current_priority.api_second_priority)
                if second_priority_function:
                    phone_data = second_priority_function(clean_phone)
                    if phone_data:
                        phone_data['found_from_db'] = False
                        return phone_data
                
                # default_priority_function = api_function_mapping.get(current_priority.fallback)
                # if default_priority_function:
                #     phone_data = default_priority_function(clean_phone)
                #     if phone_data:
                #         phone_data['found_from_db'] = False
                #         return phone_data
        else:
                second_priority_function = api_function_mapping.get(current_priority.api_second_priority)
                if second_priority_function:
                    phone_data = second_priority_function(clean_phone)
                    if phone_data:
                        phone_data['found_from_db'] = False
                        return phone_data
                
                # default_priority_function = api_function_mapping.get(current_priority.fallback)
                # if default_priority_function:
                #     phone_data = default_priority_function(clean_phone)
                #     if phone_data:
                #         phone_data['found_from_db'] = False
                #         return phone_data
        # phone_data = Signalwire_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data
        
        # phone_data = NetNumbering_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data
    else:
        # phone_data = Signalwire_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     return phone_data
        print("No Api Priorities found")
    return {}




# def isNumberAlreadyChecked_v3(userprofile_obj, clean_phone):
#     oneNumber = isNumberAlreadyChecked_v3_util(userprofile_obj, clean_phone)
#     if oneNumber is None:
#         return oneNumber
#     print(oneNumber)
#     return oneNumber

"""
    - temp modified for use
    - need to remodify asap 
"""
def isNumberAlreadyChecked_v3(userprofile_obj, clean_phone):
    """
        # mainly build for single api call or single check number
        # this function will take params: userprofile obj, clean phone 
        # and will lookup in API Data and csv file data into 10 other tables. 
    """
    oneNumber = APIData.objects.filter(userprofile=userprofile_obj, phonenumber=clean_phone).values(*apidata_model_required_fields)
    if oneNumber:
        oneNumber = oneNumber[0]
        oneNumber['number'] = oneNumber['phonenumber']
        del oneNumber['phonenumber']
        #print(oneNumber)
        return oneNumber
        
    oneNumber = UserDataLogs_CheckNumberDataThroughDatabase(userprofile_obj.user, clean_phone)
    if oneNumber:
        #print("getting through UserDataLogs_CheckNumberDataThroughDatabase")
        phone_data = returnNumberData_v5(clean_phone)
        if phone_data.get('line_type', 'invalid') == 'invalid':
            dnc_type = "n/a"
        else:
            dnc_type = returnNumberDncData_v3(clean_phone) #returnCleanDNCType(isDncNumberFound(clean_phone)).lower()
        return {'line_type': phone_data.get('line_type', 'invalid'), 
                'dnc_type': dnc_type, 
                'carrier_name': returnCleanCarrierName(phone_data.get('carrier_name', 'n/a')), 
                'city': phone_data.get('city', 'n/a'), 
                'state': phone_data.get('state', 'n/a'), 
                'country': phone_data.get('country', 'n/a'), 
                'number': clean_phone}
    
    return None






def isNumberAlreadyCheckedEndato_v1(userprofile_obj, clean_phone):
    oneNumber = EndatoApiResponse.objects.filter(userprofile=userprofile_obj, phone_number=clean_phone).values(*endato_apidata_model_required_fields)
    if oneNumber:
        return True   
    oneNumber = Endato_UserDataLogs_CheckNumberDataThroughDatabase(userprofile_obj.user, clean_phone)
    if oneNumber:
        return True
    
    return False




# def handleDNCBULKAPI_v3(numbers_list):
#     """
#         - taking number list and running it against db, api
#         - returning data
#         - saving new data
#     """
#     numbsers_startswith_0 = []
#     numbsers_startswith_1 = []
#     numbsers_startswith_2 = []
#     numbsers_startswith_3 = []
#     numbsers_startswith_4 = []
#     numbsers_startswith_5 = []
#     numbsers_startswith_6 = []
#     numbsers_startswith_7 = []
#     numbsers_startswith_8 = []
#     numbsers_startswith_9 = []
#     for num in numbers_list:
#         number_starting_digit = num[0]
#         if number_starting_digit == '0':
#             numbsers_startswith_0.append(num)
#         elif number_starting_digit == '1':
#             numbsers_startswith_1.append(num)
#         if number_starting_digit == '2':
#             numbsers_startswith_2.append(num)
#         elif number_starting_digit == '3':
#             numbsers_startswith_3.append(num)
#         elif number_starting_digit == '4':
#             numbsers_startswith_4.append(num)
#         elif number_starting_digit == '5':
#             numbsers_startswith_5.append(num)
#         elif number_starting_digit == '6':
#             numbsers_startswith_6.append(num)
#         elif number_starting_digit == '7':
#             numbsers_startswith_7.append(num)
#         elif number_starting_digit == '8':
#             numbsers_startswith_8.append(num)
#         elif number_starting_digit == '9':
#             numbsers_startswith_9.append(num)

#     found_in_db_0 = [_ for _ in DNCNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_0).values('number', 'dnc_type')]
#     found_in_db_1 = [_ for _ in DNCNumbersDataLogs1.objects.filter(number__in=numbsers_startswith_1).values('number', 'dnc_type')]
#     found_in_db_2 = [_ for _ in DNCNumbersDataLogs2.objects.filter(number__in=numbsers_startswith_2).values('number', 'dnc_type')]
#     found_in_db_3 = [_ for _ in DNCNumbersDataLogs3.objects.filter(number__in=numbsers_startswith_3).values('number', 'dnc_type')]
#     found_in_db_4 = [_ for _ in DNCNumbersDataLogs4.objects.filter(number__in=numbsers_startswith_4).values('number', 'dnc_type')]
#     found_in_db_5 = [_ for _ in DNCNumbersDataLogs5.objects.filter(number__in=numbsers_startswith_5).values('number', 'dnc_type')]
#     found_in_db_6 = [_ for _ in DNCNumbersDataLogs6.objects.filter(number__in=numbsers_startswith_6).values('number', 'dnc_type')]
#     found_in_db_7 = [_ for _ in DNCNumbersDataLogs7.objects.filter(number__in=numbsers_startswith_7).values('number', 'dnc_type')]
#     found_in_db_8 = [_ for _ in DNCNumbersDataLogs8.objects.filter(number__in=numbsers_startswith_8).values('number', 'dnc_type')]
#     found_in_db_9 = [_ for _ in DNCNumbersDataLogs9.objects.filter(number__in=numbsers_startswith_9).values('number', 'dnc_type')]

#     found_in_db = found_in_db_0 + found_in_db_1 + found_in_db_2 + found_in_db_3 + found_in_db_4 + found_in_db_5 + found_in_db_6 + found_in_db_7 + found_in_db_8 + found_in_db_9
#     numbers_found_in_db = [str(ob1["number"]).strip() for ob1 in found_in_db]
#     yet_to_crawl_numbers = list(set(numbers_list) - set(numbers_found_in_db))
#     matched_records, cleaned_records = API_DNCTCPA_SPLIT().GetSmallList(yet_to_crawl_numbers)

#     if len(matched_records) > 0:
#         saveDNCData_Bulk(matched_records)

#     for number, org_type in matched_records.items():
#         org_type = org_type.replace(',','').strip()
#         matched_records[number] = format_dnctype(org_type)

#     try:
#         #convert found_in_db to one dict and merge with others 
#         found_in_db = [{mr['number']:mr['dnc_type']} for mr in found_in_db]
#         found_in_db = reduce(lambda a, b: {**a, **b}, found_in_db)
#     except:
#         found_in_db = {}
    
#     found_in_db.update(matched_records)
#     found_in_db.update(cleaned_records)
#     matched_records = cleaned_records = None 
#     return found_in_db


def handleDNCBULKAPI_v3(numbers_list):
    
    yet_to_crawl_numbers = numbers_list

    matched_records, cleaned_records = API_DNCTCPA_SPLIT().GetSmallList(yet_to_crawl_numbers)


    if len(matched_records) > 0:
        saveDNCData_Bulk(matched_records)

    for number, org_type in matched_records.items():
        org_type = org_type.replace(',', '').strip()
        matched_records[number] = format_dnctype(org_type)


    found_in_db = matched_records.copy()
    found_in_db.update(cleaned_records)

    return found_in_db



# need modifications
def handleUserDataLogsLookup_v3(user, numbers_list, timestamp=None):
    
    """
        - taking number list and running it against db, api
        - returning data
    """
    numbsers_startswith_0 = []
    numbsers_startswith_1 = []
    numbsers_startswith_2 = []
    numbsers_startswith_3 = []
    numbsers_startswith_4 = []
    numbsers_startswith_5 = []
    numbsers_startswith_6 = []
    numbsers_startswith_7 = []
    numbsers_startswith_8 = []
    numbsers_startswith_9 = []

    for num in numbers_list:
        number_starting_digit = num[0]
        if number_starting_digit == '0':
            numbsers_startswith_0.append(num)
        elif number_starting_digit == '1':
            numbsers_startswith_1.append(num)
        if number_starting_digit == '2':
            numbsers_startswith_2.append(num)
        elif number_starting_digit == '3':
            numbsers_startswith_3.append(num)
        elif number_starting_digit == '4':
            numbsers_startswith_4.append(num)
        elif number_starting_digit == '5':
            numbsers_startswith_5.append(num)
        elif number_starting_digit == '6':
            numbsers_startswith_6.append(num)
        elif number_starting_digit == '7':
            numbsers_startswith_7.append(num)
        elif number_starting_digit == '8':
            numbsers_startswith_8.append(num)
        elif number_starting_digit == '9':
            numbsers_startswith_9.append(num)
    found_in_db_0 = list(UserDataLogs0.objects.filter(user=user, number__in=numbsers_startswith_0, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_1 = list(UserDataLogs1.objects.filter(user=user, number__in=numbsers_startswith_1, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_2 = list(UserDataLogs2.objects.filter(user=user, number__in=numbsers_startswith_2, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_3 = list(UserDataLogs3.objects.filter(user=user, number__in=numbsers_startswith_3, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_4 = list(UserDataLogs4.objects.filter(user=user, number__in=numbsers_startswith_4, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_5 = list(UserDataLogs5.objects.filter(user=user, number__in=numbsers_startswith_5, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_6 = list(UserDataLogs6.objects.filter(user=user, number__in=numbsers_startswith_6, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_7 = list(UserDataLogs7.objects.filter(user=user, number__in=numbsers_startswith_7, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_8 = list(UserDataLogs8.objects.filter(user=user, number__in=numbsers_startswith_8, timestamp__lt=timestamp).values_list('number', flat=True))
    found_in_db_9 = list(UserDataLogs9.objects.filter(user=user, number__in=numbsers_startswith_9, timestamp__lt=timestamp).values_list('number', flat=True))

    found_in_db = (found_in_db_0 + found_in_db_1 + found_in_db_2 + found_in_db_3 + found_in_db_4 + found_in_db_5 + found_in_db_6 + found_in_db_7 + found_in_db_8 + found_in_db_9)
   
    return list(set(found_in_db))





def Endato_CheckNumberDataThroughDatabase(clean_phone):
    number_starting_digit = clean_phone[0]
    if number_starting_digit == '0':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato0)
    elif number_starting_digit == '1':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato1)
    elif number_starting_digit == '2':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato2)
    elif number_starting_digit == '3':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato3)
    elif number_starting_digit == '4':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato4)
    elif number_starting_digit == '5':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato5)
    elif number_starting_digit == '6':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato6)
    elif number_starting_digit == '7':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato7)
    elif number_starting_digit == '8':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato8)
    elif number_starting_digit == '9':
        oneNumber = util_get_or_filter_number_exist_endato(clean_phone, DataEndato9)
    return oneNumber





def endatoHandleUserDataLogsLookup_v3(user, numbers_list, timestamp=None):
    
    """
        - taking number list and running it against db, api
        - returning data
    """
    try:
        numbsers_startswith_0 = []
        numbsers_startswith_1 = []
        numbsers_startswith_2 = []
        numbsers_startswith_3 = []
        numbsers_startswith_4 = []
        numbsers_startswith_5 = []
        numbsers_startswith_6 = []
        numbsers_startswith_7 = []
        numbsers_startswith_8 = []
        numbsers_startswith_9 = []
        
        
        for num in numbers_list:
            number_starting_digit = num[0]
            if number_starting_digit == '0':
                numbsers_startswith_0.append(num)
            elif number_starting_digit == '1':
                numbsers_startswith_1.append(num)
            if number_starting_digit == '2':
                numbsers_startswith_2.append(num)
            elif number_starting_digit == '3':
                numbsers_startswith_3.append(num)
            elif number_starting_digit == '4':
                numbsers_startswith_4.append(num)
            elif number_starting_digit == '5':
                numbsers_startswith_5.append(num)
            elif number_starting_digit == '6':
                numbsers_startswith_6.append(num)
            elif number_starting_digit == '7':
                numbsers_startswith_7.append(num)
            elif number_starting_digit == '8':
                numbsers_startswith_8.append(num)
            elif number_starting_digit == '9':
                numbsers_startswith_9.append(num)
        found_in_db_0 = list(UserDataLogsEndato0.objects.filter(user=user, number__in=numbsers_startswith_0, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_1 = list(UserDataLogsEndato1.objects.filter(user=user, number__in=numbsers_startswith_1, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_2 = list(UserDataLogsEndato2.objects.filter(user=user, number__in=numbsers_startswith_2, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_3 = list(UserDataLogsEndato3.objects.filter(user=user, number__in=numbsers_startswith_3, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_4 = list(UserDataLogsEndato4.objects.filter(user=user, number__in=numbsers_startswith_4, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_5 = list(UserDataLogsEndato5.objects.filter(user=user, number__in=numbsers_startswith_5, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_6 = list(UserDataLogsEndato6.objects.filter(user=user, number__in=numbsers_startswith_6, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_7 = list(UserDataLogsEndato7.objects.filter(user=user, number__in=numbsers_startswith_7, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_8 = list(UserDataLogsEndato8.objects.filter(user=user, number__in=numbsers_startswith_8, timestamp__lt=timestamp).values_list('number', flat=True))
        found_in_db_9 = list(UserDataLogsEndato9.objects.filter(user=user, number__in=numbsers_startswith_9, timestamp__lt=timestamp).values_list('number', flat=True))

        found_in_db = (found_in_db_0 + found_in_db_1 + found_in_db_2 + found_in_db_3 + found_in_db_4 + found_in_db_5 + found_in_db_6 + found_in_db_7 + found_in_db_8 + found_in_db_9)
        return list(set(found_in_db))
    except Exception as e:
        print(f"An error occurred: {str(e)}")




def Endato_CheckNumberDataThroughAPI(clean_phone):
    apidata = API_PersonSearch(clean_phone)
    saveEndatoData(apidata)
    return apidata


def returnNumberData_v6(clean_phone,shuffle=False):
    clean_phone = str(clean_phone).strip()
    phone_data = Endato_CheckNumberDataThroughDatabase(clean_phone)
    if phone_data: 
        phone_data['found_in_db'] = True
        return phone_data
    
    phone_data = Endato_CheckNumberDataThroughAPI(clean_phone)
    if phone_data: 
        phone_data['found_in_db'] = False
        return phone_data
    return {}





from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

def handleUserDataLogsLookup_Email_v3(email):
    """
    Determines the starting letter of the provided email and saves/retrieves the email
    metadata in/from the corresponding models.

    Args:
        email (str): The email to process.

    Returns:
        dict: A dictionary with information about the email record (e.g., saved or retrieved).
    """
    if not email or not isinstance(email, str):
        return {"success": False, "message": "Invalid email provided."}

    # Get the starting letter of the email
    starting_letter = email[0].upper()

    # Check if the starting letter is a valid alphabet
    if starting_letter < "A" or starting_letter > "Z":
        return {"success": False, "message": "Email does not start with a valid alphabet."}

    # Dynamically determine the models name based on the starting letter
    model_name = f"StartWith{starting_letter}"
    try:
        # Dynamically retrieve the models class
        model_class = apps.get_model(app_label="api", model_name=model_name)
    except LookupError:
        return {"success": False, "message": f"Model '{model_name}' not found."}

    try:
        # Check if the email already exists in the corresponding models
        email_record = model_class.objects.get(email=email)
        return {"success": True, "message": "Email found.", "data": email_record}
    except ObjectDoesNotExist:
        # If the email doesn't exist, create a new record
        email_record = model_class.objects.create(email=email)
        return {"success": True, "message": "Email saved.", "data": email_record}
    except Exception as e:
        # Handle any unexpected errors
        return {"success": False, "message": f"An error occurred: {str(e)}"}





def handleWavixBulkApi_v1(numbers_list,file_uid):

    numbsers_startswith_0 = []
    numbsers_startswith_1 = []
    numbsers_startswith_2 = []
    numbsers_startswith_3 = []
    numbsers_startswith_4 = []
    numbsers_startswith_5 = []
    numbsers_startswith_6 = []
    numbsers_startswith_7 = []
    numbsers_startswith_8 = []
    numbsers_startswith_9 = []
    for num in numbers_list:
        number_starting_digit = num[0]
        if number_starting_digit == '0':
            numbsers_startswith_0.append(num)
        elif number_starting_digit == '1':
            numbsers_startswith_1.append(num)
        if number_starting_digit == '2':
            numbsers_startswith_2.append(num)
        elif number_starting_digit == '3':
            numbsers_startswith_3.append(num)
        elif number_starting_digit == '4':
            numbsers_startswith_4.append(num)
        elif number_starting_digit == '5':
            numbsers_startswith_5.append(num)
        elif number_starting_digit == '6':
            numbsers_startswith_6.append(num)
        elif number_starting_digit == '7':
            numbsers_startswith_7.append(num)
        elif number_starting_digit == '8':
            numbsers_startswith_8.append(num)
        elif number_starting_digit == '9':
            numbsers_startswith_9.append(num)
    
    wx_found_in_db_0 = [_ for _ in WavixDataLogs0.objects.filter(number__in=numbsers_startswith_0).values('number', 'line_type')]
    wx_found_in_db_1 = [_ for _ in WavixDataLogs1.objects.filter(number__in=numbsers_startswith_1).values('number', 'line_type')]
    wx_found_in_db_2 = [_ for _ in WavixDataLogs2.objects.filter(number__in=numbsers_startswith_2).values('number', 'line_type')]
    wx_found_in_db_3 = [_ for _ in WavixDataLogs3.objects.filter(number__in=numbsers_startswith_3).values('number', 'line_type')]
    wx_found_in_db_4 = [_ for _ in WavixDataLogs4.objects.filter(number__in=numbsers_startswith_4).values('number', 'line_type')]
    wx_found_in_db_5 = [_ for _ in WavixDataLogs5.objects.filter(number__in=numbsers_startswith_5).values('number', 'line_type')]
    wx_found_in_db_6 = [_ for _ in WavixDataLogs6.objects.filter(number__in=numbsers_startswith_6).values('number', 'line_type')]
    wx_found_in_db_7 = [_ for _ in WavixDataLogs7.objects.filter(number__in=numbsers_startswith_7).values('number', 'line_type')]
    wx_found_in_db_8 = [_ for _ in WavixDataLogs8.objects.filter(number__in=numbsers_startswith_8).values('number', 'line_type')]
    wx_found_in_db_9 = [_ for _ in WavixDataLogs9.objects.filter(number__in=numbsers_startswith_9).values('number', 'line_type')]


    nn_found_in_db_0 = [_ for _ in NetNumberingDataLogs0.objects.filter(number__in=numbsers_startswith_0).values('number', 'line_type')]
    nn_found_in_db_1 = [_ for _ in NetNumberingDataLogs1.objects.filter(number__in=numbsers_startswith_1).values('number', 'line_type')]
    nn_found_in_db_2 = [_ for _ in NetNumberingDataLogs2.objects.filter(number__in=numbsers_startswith_2).values('number', 'line_type')]
    nn_found_in_db_3 = [_ for _ in NetNumberingDataLogs3.objects.filter(number__in=numbsers_startswith_3).values('number', 'line_type')]
    nn_found_in_db_4 = [_ for _ in NetNumberingDataLogs4.objects.filter(number__in=numbsers_startswith_4).values('number', 'line_type')]
    nn_found_in_db_5 = [_ for _ in NetNumberingDataLogs5.objects.filter(number__in=numbsers_startswith_5).values('number', 'line_type')]
    nn_found_in_db_6 = [_ for _ in NetNumberingDataLogs6.objects.filter(number__in=numbsers_startswith_6).values('number', 'line_type')]
    nn_found_in_db_7 = [_ for _ in NetNumberingDataLogs7.objects.filter(number__in=numbsers_startswith_7).values('number', 'line_type')]
    nn_found_in_db_8 = [_ for _ in NetNumberingDataLogs8.objects.filter(number__in=numbsers_startswith_8).values('number', 'line_type')]
    nn_found_in_db_9 = [_ for _ in NetNumberingDataLogs9.objects.filter(number__in=numbsers_startswith_9).values('number', 'line_type')]
    

    sw_found_in_db_0 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_0).values('number', 'line_type')]
    sw_found_in_db_1 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_1).values('number', 'line_type')]
    sw_found_in_db_2 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_2).values('number', 'line_type')]
    sw_found_in_db_3 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_3).values('number', 'line_type')]
    sw_found_in_db_4 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_4).values('number', 'line_type')]
    sw_found_in_db_5 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_5).values('number', 'line_type')]
    sw_found_in_db_6 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_6).values('number', 'line_type')]
    sw_found_in_db_7 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_7).values('number', 'line_type')]
    sw_found_in_db_8 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_8).values('number', 'line_type')]
    sw_found_in_db_9 = [_ for _ in SignalwireNumbersDataLogs0.objects.filter(number__in=numbsers_startswith_9).values('number', 'line_type')]



    found_in_wx_db = wx_found_in_db_0 + wx_found_in_db_1 + wx_found_in_db_2 + wx_found_in_db_3 + wx_found_in_db_4 + wx_found_in_db_5 + wx_found_in_db_6 + wx_found_in_db_7 + wx_found_in_db_8 + wx_found_in_db_9 
    found_in_nn_db = nn_found_in_db_0 + nn_found_in_db_1 + nn_found_in_db_2 + nn_found_in_db_3 + nn_found_in_db_4 + nn_found_in_db_5 + nn_found_in_db_6 + nn_found_in_db_7 + nn_found_in_db_8 + nn_found_in_db_9
    found_in_sw_db = sw_found_in_db_0 + sw_found_in_db_1 +  sw_found_in_db_2 + sw_found_in_db_3 + sw_found_in_db_4 + sw_found_in_db_5 + sw_found_in_db_6 + sw_found_in_db_7 + sw_found_in_db_8 + sw_found_in_db_9
    found_in_db = found_in_wx_db + found_in_nn_db + found_in_sw_db
    
    
    numbers_found_in_db = [str(ob1["number"]).strip() for ob1 in found_in_db]
    yet_to_crawl_numbers = list(set(numbers_list) - set(numbers_found_in_db))

    
    all_number_set = set()
  
    for num in yet_to_crawl_numbers:
        all_number_set.add('1' + num.strip())
    
    all_number_list = list(all_number_set)  

    if len(all_number_list) > 0:
        records_to_create = API_WAVIX_BULK().createSmallList(all_number_list,file_uid)
    else:
        records_to_create = []
    
    

    if len(records_to_create) > 0:
        saveWavixDataV2(records_to_create)
    return 



def get_monthwise_creditsAnalytics_for_textDrip_webHook(first_day, last_day):
    return (
        CreditAnalytics.objects.filter(
            created_at__gte=first_day,
            created_at__lte=last_day,
            service=CreditAnalytics.SERVICE_TYPE.NUMBER_CHECK,
        )
        .aggregate(total_sum=Sum("total_numbers"))["total_sum"]
        or 0
    )



def get_monthwise_creditsAnalytics_dbCheck_for_textDrip_webHook(first_day, last_day):
    return (
        CreditAnalytics.objects.filter(
            created_at__gte=first_day,
            created_at__lte=last_day,
            service=CreditAnalytics.SERVICE_TYPE.NUMBER_CHECK,
        )
        .aggregate(db_checked_numbers=Sum("db_checked_numbers"))["db_checked_numbers"]
        or 0
    )

def get_monthwise_creditsAnalytics_APICheck_for_textDrip_webHook(first_day, last_day):
    return (
        CreditAnalytics.objects.filter(
            created_at__gte=first_day,
            created_at__lte=last_day,
            service=CreditAnalytics.SERVICE_TYPE.NUMBER_CHECK,
        )
        .aggregate(api_called_numbers=Sum("api_called_numbers"))["api_called_numbers"]
        or 0
    )




# def webhookTotalNumber_checksMonth(first_day_of_previous_month,last_day_of_previous_month):
    
#     log_models = [
#         UserDataLogs0, UserDataLogs1, UserDataLogs2, UserDataLogs3,
#         UserDataLogs4, UserDataLogs5, UserDataLogs6, UserDataLogs7,
#         UserDataLogs8, UserDataLogs9
#     ]

#     total_logs = 0

#     for models in log_models:
#         count = models.objects.filter(
#             timestamp__gte=first_day_of_previous_month,
#             timestamp__lte=last_day_of_previous_month
#         ).count()
#         total_logs += count

#     month_name = first_day_of_previous_month.strftime('%B %Y')
#     # print(f"Total logs for {month_name}: {total_logs}")
#     return total_logs

# def total_checked_with_service_provider_wavix(first_day_of_previous_month,last_day_of_previous_month):
#     wavix_models = [
#         WavixDataLogs0, WavixDataLogs1, WavixDataLogs2, WavixDataLogs3,
#         WavixDataLogs4, WavixDataLogs5, WavixDataLogs6, WavixDataLogs7,
#         WavixDataLogs8, WavixDataLogs9
#     ]

#     total_wavix = 0

#     for models in wavix_models:
#         count = models.objects.filter(
#             timestamp__gte=first_day_of_previous_month,
#             timestamp__lte=last_day_of_previous_month
#         ).count()
#         total_wavix += count

#     month_name = first_day_of_previous_month.strftime('%B %Y')
#     # print(f"Total logs for {month_name}: {total_wavix}")
#     return total_wavix

def total_checked_with_service_provider_netnumbering(first_day_of_previous_month,last_day_of_previous_month):  
    netnumbering_models = [
        NetNumberingDataLogs0,NetNumberingDataLogs1,NetNumberingDataLogs2,NetNumberingDataLogs4,
        NetNumberingDataLogs5,NetNumberingDataLogs6,NetNumberingDataLogs7,NetNumberingDataLogs8,
        NetNumberingDataLogs9
    ]

    total_netnumbering = 0

    for model in netnumbering_models:
        count = model.objects.filter(
            timestamp__gte=first_day_of_previous_month,
            timestamp__lte=last_day_of_previous_month
        ).count()
        total_netnumbering += count

    month_name = first_day_of_previous_month.strftime('%B %Y')
    # print(f"Total logs for {month_name}: {total_netnumbering}")
    return total_netnumbering


def total_checked_with_service_provider_signalwire(first_day_of_previous_month,last_day_of_previous_month):
    signalwire_models = [
        SignalwireNumbersDataLogs0,SignalwireNumbersDataLogs1,SignalwireNumbersDataLogs2,SignalwireNumbersDataLogs3,
        SignalwireNumbersDataLogs4,SignalwireNumbersDataLogs5,SignalwireNumbersDataLogs6,SignalwireNumbersDataLogs7,SignalwireNumbersDataLogs8,
        SignalwireNumbersDataLogs9
    ]

    total_signalwire = 0

    for model in signalwire_models:
        count = model.objects.filter(
            timestamp__gte=first_day_of_previous_month,
            timestamp__lte=last_day_of_previous_month
        ).count()
        total_signalwire += count

    month_name = first_day_of_previous_month.strftime('%B %Y')
    # print(f"Total logs for {month_name}: {total_signalwire}")
    return total_signalwire






def get_total_credits_revenue_for_previous_month(first_day_of_previous_month,last_day_of_previous_month):
    total_rows_charged = CsvFile.objects.filter(
        uploaded_at__gte=first_day_of_previous_month,
        uploaded_at__lte=last_day_of_previous_month
    ).aggregate(total_rows_charged=Sum('total_rows_charged'))['total_rows_charged'] or 0

    return total_rows_charged

def get_total_email_checks_performed(first_day_of_selected_month, last_day_of_selected_month):
    """Fetch total email checks from all concrete tables within a date range."""
    total_checks = 0
    models = [StartWithA, StartWithB, StartWithC, StartWithD, StartWithE,
              StartWithF, StartWithG, StartWithH, StartWithI, StartWithJ,
              StartWithK, StartWithL, StartWithM, StartWithN, StartWithO,
              StartWithP, StartWithQ, StartWithR, StartWithS, StartWithT,
              StartWithU, StartWithV, StartWithW, StartWithX, StartWithY, StartWithZ]

    for model in models:
        total_checks += model.objects.filter(
            validation_date__range=(first_day_of_selected_month, last_day_of_selected_month)
        ).count()

    return total_checks

def get_total_email_credits_revenue(first_day_of_selected_month, last_day_of_selected_month):
    """Fetch total revenue from email credits within a date range."""
    total_rows_charged = CsvFileEmail.objects.filter(
        uploaded_at__gte=first_day_of_selected_month,
        uploaded_at__lte=last_day_of_selected_month
    ).aggregate(total_rows_charged=Sum('total_rows_charged'))['total_rows_charged'] or 0

    return total_rows_charged




def update_date_after_1_year(oneNumber, DjModel):
    try:
        instance = DjModel.objects.get(number=oneNumber['number'])
    except MultipleObjectsReturned:
        instance = DjModel.objects.filter(number=oneNumber['number']).first()
    except DjModel.DoesNotExist:
        return None

    one_year_ago = now() - timedelta(days=365)
    six_months_old = now() - timedelta(days=180)

    if (
        instance.timestamp is None or 
        instance.last_check is None or 
        (instance.timestamp < one_year_ago and instance.last_check < six_months_old)
    ):
        new_data = returnNumberData_v9(instance.number)

        if not instance.update_history or not isinstance(instance.update_history, dict):
            instance.update_history = {}

        if new_data.get('line_type') and new_data['line_type'] != instance.line_type:
            
            current_time = str(now())
            instance.update_history[current_time] = {
                "previous_line_type": instance.line_type,
                "new_line_type": new_data['line_type']
            }

            # New changes to store data in models .
            model_name = DjModel.__name__.lower()

            if 'netnumbering' in model_name:
                checked_value = OneYearOldData.Checkedthrough.NETNUMBERING
            elif 'signalwire' in model_name:
                checked_value = OneYearOldData.Checkedthrough.SIGNALWIRE
            elif 'wavix' in model_name:
                checked_value = OneYearOldData.Checkedthrough.WAVIX
            else:
                checked_value = None

            obj, created = OneYearOldData.objects.update_or_create(
                number=instance.number,
                defaults={
                    'old_line_type': instance.line_type,
                    'new_line_type': new_data['line_type'],
                    'checked_through': checked_value,
                    'carrier_name': instance.carrier_name,
                    'city': instance.city,
                    'state': instance.state,
                    'country': instance.country,
                    'timestamp': instance.timestamp,
                    'last_check': instance.last_check,
                }
            )

            instance.line_type = new_data['line_type']
            instance.timestamp = now()

        instance.last_check = now()
        instance.save()

    return instance

def returnNumberData_v9(clean_phone,shuffle=False):
   
    clean_phone = str(clean_phone).strip()

    current_priority = ApiPriorities.objects.first()

    if current_priority:
        first_priority_function = api_function_mapping.get(current_priority.api_first_priority)
        if first_priority_function:
            phone_data = first_priority_function(clean_phone)
            if phone_data:
                return phone_data
        
        if current_priority.api_second_priority == ApiPriorities.APITYPE_SECOND_PRIORITY.SIGNALWIRE:

            if current_priority.signalwire_status == True:
                second_priority_function = api_function_mapping.get(current_priority.api_second_priority)
                if second_priority_function:
                    phone_data = second_priority_function(clean_phone)
                    if phone_data:
                        phone_data['found_from_db'] = False
                        return phone_data
                
                # default_priority_function = api_function_mapping.get(current_priority.fallback)
                # if default_priority_function:
                #     phone_data = default_priority_function(clean_phone)
                #     if phone_data:
                #         phone_data['found_from_db'] = False
                #         return phone_data
        else:
                second_priority_function = api_function_mapping.get(current_priority.api_second_priority)
                if second_priority_function:
                    phone_data = second_priority_function(clean_phone)
                    if phone_data:
                        phone_data['found_from_db'] = False
                        return phone_data
                
                # default_priority_function = api_function_mapping.get(current_priority.fallback)
                # if default_priority_function:
                #     phone_data = default_priority_function(clean_phone)
                #     if phone_data:
                #         phone_data['found_from_db'] = False
                #         return phone_data

        # phone_data = Signalwire_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data
        
        # phone_data = NetNumbering_CheckNumberDataThroughAPI(clean_phone)
        # if phone_data:
        #     phone_data['found_from_db'] = False
        #     return phone_data
    else:
        phone_data = Signalwire_CheckNumberDataThroughAPI(clean_phone)
        if phone_data:
            return phone_data
    return {}
