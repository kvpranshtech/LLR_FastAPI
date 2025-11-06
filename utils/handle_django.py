from django.db.models import Count
from django.db.models.functions import Lower


from core.models import CsvFile, CsvFileInfo, CsvFileData,EndatoCsvFileData
from api.models import APIData, APIBULK


def check_FileAlreadyExist(user, filename, total_records):
    objects = CsvFile.objects.filter(user=user, 
                                    is_charged=True, 
                                    csvfile_name__iexact=filename,
                                    total_rows=total_records
                                    )
    if objects.count() > 0:
        return objects.latest('pk')
    return None


def createAPIData(userprofile, clean_phone, line_type, dnc_type, added_through='api'):
    try:
        APIData.objects.get_or_create(
            userprofile=userprofile, 
            phonenumber=clean_phone,
            defaults = {
                "line_type" : line_type.lower(),
                "dnc_type" : dnc_type.lower(),
                "added_through" : added_through
            }
        )
    except: 
        pass


def UpdateBulkAPIDetailInfo(file_uid):
    apibulk_obj = APIBULK.objects.get(uid=file_uid)

    linetype_result = {}
    dnctype_result = {}

    apibulk_data = APIData.objects.filter(apibulk=apibulk_obj)
    linetypes = list(apibulk_data.annotate(line_type_clean=Lower('line_type')).values('line_type_clean').annotate(Count('id')).order_by())
    dnctypes = list(apibulk_data.annotate(dnc_type_clean=Lower('dnc_type')).values('dnc_type_clean').annotate(Count('id')).order_by())

    for line in linetypes: line['line_type_clean'] = str(line['line_type_clean']).lower()
    for dnc in dnctypes: dnc['dnc_type_clean'] = str(dnc['dnc_type_clean']).lower()
    

    for line in linetypes:
        linetype_result[line['line_type_clean']] = line['id__count']

    for dnc in dnctypes:
        dnctype_result[dnc['dnc_type_clean']] = dnc['id__count']


    apibulk_obj.line_type_info = linetype_result
    apibulk_obj.dnc_type_info = dnctype_result
    apibulk_obj.save()
    return None



def UpdateCSVDetailInfo(file_uid, override=False,checkprrows=False):
    try:
        csvfile_obj = CsvFile.objects.get(uid=file_uid)
        linetype_result = {}
        dnctype_result = {}

        if override is False:
            if CsvFileInfo.objects.filter(csvfile=csvfile_obj).exists(): 
                return None
        
        if checkprrows:
          csv_filedata = CsvFileData.objects.filter(csvfile=csvfile_obj,is_processed=True)
        else:    
            csv_filedata = CsvFileData.objects.filter(csvfile=csvfile_obj)
        linetypes = list(csv_filedata.annotate(line_type_clean=Lower('line_type')).values('line_type_clean').annotate(Count('id')).order_by())
        dnctypes = list(csv_filedata.annotate(dnc_type_clean=Lower('dnc_type')).values('dnc_type_clean').annotate(Count('id')).order_by())
        
        for line in linetypes: line['line_type_clean'] = str(line['line_type_clean']).lower()
        for dnc in dnctypes: dnc['dnc_type_clean'] = str(dnc['dnc_type_clean']).lower()
        
        for line in linetypes:
            linetype_result[line['line_type_clean']] =  line['id__count']

        for dnc in dnctypes:
            dnctype_result[dnc['dnc_type_clean']] =  dnc['id__count']

        CsvFileInfo.objects.update_or_create(
            csvfile=csvfile_obj,
            defaults={'line_type_info': linetype_result, 'dnc_type_info': dnctype_result},
        )
        return True
    except:
        return False


def updateProcessedRows(file_uid):
    try:
        csvfile_obj = CsvFile.objects.get(uid=file_uid)
        csv_filedata_counts = CsvFileData.objects.filter(csvfile=csvfile_obj, is_processed=True).count()
        csvfile_obj.processed_rows = csv_filedata_counts
        csvfile_obj.save()
        return csv_filedata_counts
    except CsvFile.DoesNotExist:
        print(f"CsvFile with UID {file_uid} does not exist.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0



def updateProcessedRowsv2(file_uid):
    try:
        csvfile_obj = CsvFile.objects.get(uid=file_uid)
        csv_filedata_counts = EndatoCsvFileData.objects.filter(csvfile=csvfile_obj, is_processed=True).count()
        csvfile_obj.processed_rows = csv_filedata_counts
        csvfile_obj.save()
        return csv_filedata_counts
    except CsvFile.DoesNotExist:
        print(f"CsvFile with UID {file_uid} does not exist.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
    

from api.models import CsvFileEmail, CsvFileDataEmail
def updateEmailProcessedRows(file_uid):
    try:
        csvfile_obj = CsvFileEmail.objects.get(uid=file_uid)
        csv_filedata_counts = CsvFileDataEmail.objects.filter(csvfile=csvfile_obj, is_processed=True).count()
        csvfile_obj.processed_rows = csv_filedata_counts
        csvfile_obj.save()
        return csv_filedata_counts
    except CsvFileEmail.DoesNotExist:
        print(f"CsvFile with UID {file_uid} does not exist.")
        return 0
    except Exception as e:
        print(f"An error occurred data: {e}")
        return 0
