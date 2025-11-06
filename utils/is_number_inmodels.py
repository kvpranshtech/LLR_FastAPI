from mdrdata.models import DNCNumberData
from uploadtoken.models import ( 
                InvalidNumberData, 
                SignalwireNumberData,
                TelynxNumberData
)
from .handle_dnctcpa import API_TcpaLitigatorlist
from .handle_signalwire import API_Singalwire
from utils.handle_telynx import API_TELNYX

from api.models import APIData
from core.models import CsvFileData

# utils imports
from utils.handle_saving_data import (
    saveSignalwireData,
    saveTelynxData,
    saveInvalidNumberData,
)
from utils._base import required_data_fields_list, required_data_fields_list_full



# new method - done - working _ move to new file which is updated to multiple tables
# delete this too after testing
def returnPhoneRequiredData(phone_clean, shuffle=False):
    """
        - it will take 10 digit phone number and check into tables for full info or get from apis
        - save api data into table if not found in table
        - return dictionary of data or empty {}
    """
    if shuffle:
        oneNumber = TelynxNumberData.objects.filter(number=phone_clean).values(*required_data_fields_list)
        if oneNumber:
            return oneNumber[0]
        
        oneNumber = SignalwireNumberData.objects.filter(number=phone_clean).values(*required_data_fields_list)
        if oneNumber:
            return oneNumber[0]
        
    else:
        oneNumber = SignalwireNumberData.objects.filter(number=phone_clean).values(*required_data_fields_list)
        if oneNumber:
            return oneNumber[0]
        
        oneNumber = TelynxNumberData.objects.filter(number=phone_clean).values(*required_data_fields_list)
        if oneNumber:
            return oneNumber[0]
        
    try: 
        oneNumber = InvalidNumberData.objects.get(number=phone_clean)
        if oneNumber:
            return {}
    except:
        pass 
    
    if shuffle:
        apidata = API_TELNYX(phone_clean)
        if apidata['line_type'] != 'invalid':
            saveTelynxData(apidata)
            apidata.pop('data', None) #pop out data key to save memory
            return apidata
        
        apidata = API_Singalwire(phone_clean)
        if apidata['line_type'] != 'invalid':
            saveSignalwireData(apidata)
            apidata.pop('data', None) #pop out data key to save memory
            return apidata
    else:
        apidata = API_Singalwire(phone_clean)
        if apidata['line_type'] != 'invalid':
            saveSignalwireData(apidata)
            apidata.pop('data', None) #pop out data key to save memory
            return apidata
        
        apidata = API_TELNYX(phone_clean)
        if apidata['line_type'] != 'invalid':
            saveTelynxData(apidata)
            apidata.pop('data', None) #pop out data key to save memory
            return apidata

    saveInvalidNumberData(phone_clean)
    return {}


"""
    - modified version shifted to handle number info
    - after migrating to all new version
    - delete below code
"""
# working 
def isDncNumberFound(phone_clean):
    oneNumber = DNCNumberData.objects.filter(phonenumber=phone_clean).values('dnc_type')
    if oneNumber:
        return oneNumber[0]['dnc_type']

    data = API_TcpaLitigatorlist(phone_clean)
    if data['dnc_type'] !='clean':
        try:
            DNCNumberData.objects.create(phonenumber = data['phonenumber'], 
                dnc_type = data['dnc_type'],
                api_data = data['api_data'])
        except: 
            pass 
    return data['dnc_type']


"""
    - modified version shifted to handle number info
    - after migrating to all new version
    - delete below code
"""
# new method - working - done
def isNumberAlreadyChecked_V2(userprofile, clean_phone):
    """
        # mainly build for single api call 
        # this function will take params: userprofile obj, clean phone 
        # and will lookup in API Data and csv file data tables. 
    """
    oneNumber = APIData.objects.filter(userprofile=userprofile, phonenumber=clean_phone).values(*required_data_fields_list_full)
    if oneNumber:
        return oneNumber.first()

    oneNumber = CsvFileData.objects.filter(csvfile__user=userprofile.user, csvfile__is_charged=True, 
                                           csvfile__is_complete=True, phonenumber=clean_phone).values(*required_data_fields_list_full)
    
    if oneNumber:
        return oneNumber.first()
    return None


"""
    - modified version shifted to handle number info
    - after migrating to all new version
    - delete below code
"""
# todo - needs modifications
def isNumberAlreadyChecked(userprofile, clean_phone):
    """
        # mainly build for single api call 
        # this function will take params: userprofile obj, clean phone 
        # and will lookup in API Data and csv file data tables. 
    """
    oneNumber = APIData.objects.filter(userprofile=userprofile, phonenumber=clean_phone).values('phonenumber', 'line_type', 'dnc_type')
    # oneNumber = APIData.objects.filter(userprofile=userprofile, phonenumber=clean_phone).values(*required_data_fields_list_full)

    if oneNumber:
        return oneNumber.first()

    oneNumber = CsvFileData.objects.filter(csvfile__user=userprofile.user, 
                                        csvfile__is_charged=True, 
                                        csvfile__is_complete=True, 
                                        phonenumber=clean_phone).values('phonenumber', 'line_type', 'dnc_type')
    if oneNumber:
        return oneNumber.first()
    return None



# todo - need modifications
def isNumberFoundInModels_2(phone_clean):
    oneNumber = SignalwireNumberData.objects.filter(number=phone_clean).values('line_type')
    if oneNumber:
        return oneNumber[0]['line_type']


    oneNumber = TelynxNumberData.objects.filter(number=phone_clean).values('line_type')
    if oneNumber:
        return oneNumber[0]['line_type']
    

    try: 
        oneNumber = InvalidNumberData.objects.get(number=phone_clean)
        if oneNumber:
            return 'invalid'
    except:
        pass 

    apidata = API_Singalwire(phone_clean)
    if apidata['line_type'] != 'invalid':
        try:
            SignalwireNumberData.objects.create(
                number = apidata['number'],
                line_type = apidata['line_type'],
                line_type_original = apidata['line_type_original'],
                data = apidata['data']
            )
        except:
            pass
        return apidata['line_type']

    apidata = API_TELNYX(phone_clean)
    if apidata['line_type'] != 'invalid':
        try:
            TelynxNumberData.objects.create(
                number = apidata['number'],
                line_type = apidata['line_type'],
                line_type_original = apidata['line_type_original'],
                carrier_name = apidata['carrier_name'],
                data = apidata['data']
            )
        except:
            pass
        return apidata['line_type']

    try:
        InvalidNumberData.objects.create(number = phone_clean)
        return 'invalid'
    except:pass 

    return None


# todo - need modifications
def isNumberFoundInModels(phone_clean):
    oneNumber = TelynxNumberData.objects.filter(number=phone_clean).values('line_type')
    if oneNumber:
        return oneNumber[0]['line_type']
    
    oneNumber = SignalwireNumberData.objects.filter(number=phone_clean).values('line_type')
    if oneNumber:
        return oneNumber[0]['line_type']

    try: 
        oneNumber = InvalidNumberData.objects.get(number=phone_clean)
        if oneNumber:
            return 'invalid'
    except:
        pass 


    apidata = API_TELNYX(phone_clean)
    if apidata['line_type'] != 'invalid':
        try:
            TelynxNumberData.objects.create(
                number = apidata['number'],
                line_type = apidata['line_type'],
                line_type_original = apidata['line_type_original'],
                carrier_name = apidata['carrier_name'],
                data = apidata['data']
            )
        except:
            pass
        return apidata['line_type']


    apidata = API_Singalwire(phone_clean)
    if apidata['line_type'] != 'invalid':
        try:
            SignalwireNumberData.objects.create(
                number = apidata['number'],
                line_type = apidata['line_type'],
                line_type_original = apidata['line_type_original'],
                data = apidata['data']
            )
        except:
            pass
        return apidata['line_type']

    try:
        InvalidNumberData.objects.create(number = phone_clean)
        return 'invalid'
    except:pass 

    return None




