import csv, json, requests
from django.utils.crypto import get_random_string
import string, os
import pandas as pd
import uuid
import datetime
from dateutil.relativedelta import relativedelta
import io



def get_last_months(start_date, no_of_months=12):
    for i in range(no_of_months):
        yield (start_date.strftime("%B"), start_date.year, start_date.month)
        start_date += relativedelta(months = -1)

def is_valid_uuid(val):
    try:
        data = uuid.UUID(str(val))
        return data
    except ValueError:
        return None

def getUserIpAddress(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return str(ip.strip())


def getUserBrowserAgent(request):
    """
        Get the user agent from the Django request object.
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return user_agent


def generateAPIKEY():
    return get_random_string(40, allowed_chars=string.ascii_uppercase + string.digits + string.ascii_lowercase)

class DummyFile:
    def write(self, value_to_write):
        return value_to_write


def returnCleanPhone(number):
    phone_clean = ''.join([n for n in number if n.isdigit()])[-10:]
    return str(phone_clean).strip()


def returnCleanPhone_Or_None(number):
    phone_clean = ''.join([n for n in number if n.isdigit()])[-10:]
    phone_clean = str(phone_clean).strip()
    if len(phone_clean) == 10:
        return phone_clean
    return None

def get_delimiter(file_path, bytes = 4096):
    sniffer = csv.Sniffer()
    data = open(file_path, "r").read(bytes)
    delimiter = sniffer.sniff(data).delimiter
    return delimiter

def returnCsvTotalRecords(filepath):
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    return df.shape[0]

def returnEmailCsvTotalRecords(filepath):
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    return df.shape[0]




def renderCsvFileOnUpload(file_obj):
    try:
        try:
            df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
                except UnicodeDecodeError:
                    df = pd.read_csv(file_obj, encoding='ISO-8859-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)


        df_columns = list(df.columns)
        df_columns_dict = {}
        if 'LLR_PhoneNumber' in df_columns:
            df_columns_dict['LLR_PhoneNumber'] = 'LLR_PhoneNumber_Old'
        if 'LLR_LineType' in df_columns:
            df_columns_dict['LLR_LineType'] = 'LLR_LineType_Old'
        if 'LLR_DNCType' in df_columns:
            df_columns_dict['LLR_DNCType'] = 'LLR_DNCType_Old'
        if 'LLR_CarrierName' in df_columns:
            df_columns_dict['LLR_CarrierName'] = 'LLR_CarrierName_Old'
        if 'LLR_City' in df_columns:
            df_columns_dict['LLR_City'] = 'LLR_City_Old'
        if 'LLR_State' in df_columns:
            df_columns_dict['LLR_State'] = 'LLR_State_Old'
        if 'LLR_Country' in df_columns:
            df_columns_dict['LLR_Country'] = 'LLR_Country_Old'
        if df_columns_dict:
            df.rename(columns=df_columns_dict, inplace=True)

        total_records = df.shape[0]
        head_data = df.head(n=10)  
        header = list(df.columns)  

        return total_records, header, head_data

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise ValueError("Failed to read CSV file. Please check the file encoding.")





def renderCsvFileOnUploadForEmail(file_obj):
    try:
        # Try reading the file with different encodings
        try:
            df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
                except UnicodeDecodeError:
                    df = pd.read_csv(file_obj, encoding='ISO-8859-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)


        # Process column renaming if needed
        df_columns = list(df.columns)
        df_columns_dict = {}
        if 'LLR_PhoneNumber' in df_columns:
            df_columns_dict['LLR_PhoneNumber'] = 'LLR_PhoneNumber_Old'
        if 'LLR_LineType' in df_columns:
            df_columns_dict['LLR_LineType'] = 'LLR_LineType_Old'
        if 'LLR_DNCType' in df_columns:
            df_columns_dict['LLR_DNCType'] = 'LLR_DNCType_Old'
        if df_columns_dict:
            df.rename(columns=df_columns_dict, inplace=True)

        # Retrieve required data
        total_records = df.shape[0]
        head_data = df.head(n=10)  # Get the first 10 rows
        header = list(df.columns)  # List of column headers

        return total_records, header, head_data

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise ValueError("Failed to read CSV file. Please check the file encoding.")



def getCSVHeaderRow(filepath):
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    return df.to_dict(orient='records')[0].keys()


def cleanCSVreturnTotalRows(file_obj, phone_col, first_name_col='', last_name_col=''):
    try:
        df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True,
                         dtype=str)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True,
                             dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip',
                             skip_blank_lines=True, dtype=str)

    df_columns = list(df.columns)

    df_columns_dict = {}

    # if first_name_col and last_name_col:
    #     if first_name_col not in df.columns or last_name_col not in df.columns:
    #         raise ValueError(f"Columns '{first_name_col}' and/or '{last_name_col}' not found in the CSV file.")

    if 'LLR_PhoneNumber' in df_columns:
        df_columns_dict['LLR_PhoneNumber'] = 'LLR_PhoneNumber_Old'
    if 'LLR_LineType' in df_columns:
        df_columns_dict['LLR_LineType'] = 'LLR_LineType_Old'
    if 'LLR_DNCType' in df_columns:
        df_columns_dict['LLR_DNCType'] = 'LLR_DNCType_Old'
    if 'LLR_CarrierName' in df_columns:
        df_columns_dict['LLR_CarrierName'] = 'LLR_CarrierName_Old'
    if 'LLR_City' in df_columns:
        df_columns_dict['LLR_City'] = 'LLR_City_Old'
    if 'LLR_State' in df_columns:
        df_columns_dict['LLR_State'] = 'LLR_State_Old'
    if 'LLR_Country' in df_columns:
        df_columns_dict['LLR_Country'] = 'LLR_Country_Old'

    if first_name_col and last_name_col:
        if 'LLR_FirstName' in df_columns:
            df_columns_dict['LLR_FirstName'] = 'LLR_FirstName_Old'
        if 'LLR_LastName' in df_columns:
            df_columns_dict['LLR_LastName'] = 'LLR_LastName_Old'

    if df_columns_dict:
        print("Columns to be renamed:", df_columns_dict)
        df.rename(columns=df_columns_dict, inplace=True)


    df.dropna(how="all", inplace=True)

    datas = df.to_dict(orient='records')
    for data in datas[:]:
        phone_number = returnCleanPhone(str(data.get(phone_col, "")))
        if len(phone_number) == 10:
            data['LLR_PhoneNumber'] = phone_number
        else:
            data['LLR_PhoneNumber'] = 'invalid_data'
        if first_name_col and last_name_col:
            data['LLR_FirstName'] = str(data.get(first_name_col, ""))
            data['LLR_LastName'] = str(data.get(last_name_col, ""))

    new_df = pd.DataFrame(datas)

    csv_buffer = io.BytesIO()
    try:
        new_df.to_csv(csv_buffer, encoding='utf-8', header=True, index=False)
    except UnicodeDecodeError:
        try:
            new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False)
        except UnicodeDecodeError:
            new_df.to_csv(csv_buffer, encoding='windows-1252', header=True, index=False)

    csv_buffer.seek(0)

    return csv_buffer, new_df.shape[0]





import re
def cleanCSVreturnTotalRowsForEmail(file_obj, email_col):
    # Read the CSV data from the file object
    try:
        df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)

    df_columns = list(df.columns)
    df_columns_dict = {}
    if 'LLR_PhoneNumber' in df_columns:
        df_columns_dict['LLR_PhoneNumber'] = 'LLR_PhoneNumber_Old'
    if 'LLR_LineType' in df_columns:
        df_columns_dict['LLR_LineType'] = 'LLR_LineType_Old'
    if 'LLR_DNCType' in df_columns:
        df_columns_dict['LLR_DNCType'] = 'LLR_DNCType_Old'
    if df_columns_dict:
        df.rename(columns=df_columns_dict, inplace=True)

    df.dropna(how="all", inplace=True)
    datas = df.to_dict(orient='records')
    for data in datas[:]:
        user_email = data.get(email_col)
        # print("User Email =================>", user_email)
        if user_email:
            data['LLR_Email'] = user_email
        else:
            data['LLR_Email'] = 'invalid_data'

    new_df = pd.DataFrame(datas)

    # Use BytesIO to write the DataFrame to an in-memory binary file object
    csv_buffer = io.BytesIO()
    try:
        new_df.to_csv(csv_buffer, encoding='utf-8', header=True, index=False)
    except UnicodeDecodeError:
        try:
            new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False)
        except UnicodeDecodeError:
            new_df.to_csv(csv_buffer, encoding='windows-1252', header=True, index=False)

    # new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False)

    # Seek to the beginning of the buffer before returning
    csv_buffer.seek(0)

    # Return the buffer and the total number of rows
    return csv_buffer, new_df.shape[0]

def getFilePathsFromDirectory(dir_name):
    files_path = []
    for r, d, f in os.walk(dir_name):
        for file in f:
            files_path.append(os.path.join(r, file))
    return sorted(files_path)


def returnCleanDNCType(dnc_type):
    dnc_type = str(dnc_type).lower()
    if 'tcpa' in dnc_type:
        return "LITIGATOR"
    elif 'dnc' in dnc_type:
        return 'DNC'
    elif 'clean' in dnc_type:
        return 'CLEAN'
    else:
        return 'UNKNOWN'


def get_blog_image_filename(filename, request):
    return filename.lower()

def split_list_into_chunks(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]




def renderendatoCsvFileOnUpload(file_obj):
    try:
        # Try reading the file with different encodings
        try:
            df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
                except UnicodeDecodeError:
                    df = pd.read_csv(file_obj, encoding='ISO-8859-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)


        # Process column renaming if needed
        df_columns = list(df.columns)
        df_columns_dict = {}
        if 'LLR_FirstName' in df_columns:
            df_columns_dict['LLR_FirstName'] = 'LLR_FirstName_Old'
        if 'LLR_LastName' in df_columns:
            df_columns_dict['LLR_LastName'] = 'LLR_LastName_Old'
        if df_columns_dict:
            df.rename(columns=df_columns_dict, inplace=True)

        # Retrieve required data
        total_records = df.shape[0]
        head_data = df.head(n=10)  # Get the first 10 rows
        header = list(df.columns)  # List of column headers

        return total_records, header, head_data

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        raise ValueError("Failed to read CSV file. Please check the file encoding.")





def endatocleanCSVreturnTotalRows(file_obj, phone_col, first_name_col='', last_name_col=''):
    try:
        df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True,
                         dtype=str)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True,
                             dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip',
                             skip_blank_lines=True, dtype=str)

    df_columns = list(df.columns)

    df_columns_dict = {}

    if phone_col and first_name_col and last_name_col:
        if phone_col not in df.columns and first_name_col not in df.columns or last_name_col not in df.columns:
            raise ValueError(f"Columns '{phone_col}'and/or {first_name_col}' and/or '{last_name_col}' not found in the CSV file.")

    if 'LLR_PhoneNumber' in df_columns:
        df_columns_dict['LLR_PhoneNumber'] = 'LLR_PhoneNumber_Old'
    if first_name_col and last_name_col:
        if 'LLR_FirstName' in df_columns:
            df_columns_dict['LLR_FirstName'] = 'LLR_FirstName_Old'
        if 'LLR_LastName' in df_columns:
            df_columns_dict['LLR_LastName'] = 'LLR_LastName_Old'

    if df_columns_dict:
        print("Columns to be renamed:", df_columns_dict)
        df.rename(columns=df_columns_dict, inplace=True)


    df.dropna(how="all", inplace=True)

    datas = df.to_dict(orient='records')
    for data in datas[:]:
        phone_number = returnCleanPhone(str(data.get(phone_col, "")))
        if len(phone_number) == 10:
            data['LLR_PhoneNumber'] = phone_number
        else:
            data['LLR_PhoneNumber'] = 'invalid_data'
        if first_name_col and last_name_col:
            data['LLR_FirstName'] = str(data.get(first_name_col, ""))
            data['LLR_LastName'] = str(data.get(last_name_col, ""))

    new_df = pd.DataFrame(datas)

    # Use BytesIO to write the DataFrame to an in-memory binary file object
    csv_buffer = io.BytesIO()
    try:
        new_df.to_csv(csv_buffer, encoding='utf-8', header=True, index=False)
    except UnicodeDecodeError:
        try:
            new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False)
        except UnicodeDecodeError:
            new_df.to_csv(csv_buffer, encoding='windows-1252', header=True, index=False)

    # Seek to the beginning of the buffer before returning
    csv_buffer.seek(0)

    # Return the buffer and the total number of rows
    return csv_buffer, new_df.shape[0]


def cleanCSVreturnTotalRowsForEmailBULK(file_obj, email_col):
    try:
        df = pd.read_csv(file_obj, encoding='utf-8', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_obj, encoding='latin-1', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
        except UnicodeDecodeError:
            df = pd.read_csv(file_obj, encoding='windows-1252', encoding_errors='ignore', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)

    df_columns = list(df.columns)
    df_columns_dict = {}
    if 'LLR_Email' in df_columns:
        df_columns_dict['LLR_Email'] = 'LLR_Email_Old'

    if df_columns_dict:
        df.rename(columns=df_columns_dict, inplace=True)

    df.dropna(how="all", inplace=True)

    datas = df.to_dict(orient='records')
    for data in datas[:]:
        user_email = data.get(email_col)
        if user_email:
            data['LLR_Email'] = user_email
        else:
            data['LLR_Email'] = 'invalid_data'

    new_df = pd.DataFrame(datas)

    csv_buffer = io.BytesIO()
    try:
        new_df.to_csv(csv_buffer, encoding='utf-8', header=True, index=False)
    except UnicodeDecodeError:
        try:
            new_df.to_csv(csv_buffer, encoding='latin-1', header=True, index=False)
        except UnicodeDecodeError:
            new_df.to_csv(csv_buffer, encoding='windows-1252', header=True, index=False)

    csv_buffer.seek(0)

    return csv_buffer, new_df.shape[0]
