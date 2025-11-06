import inspect
import inspect
from os.path import basename as os_path_basename


from site_settings.models import CustomSiteLogs
from utils.utils import getUserIpAddress


def create_log_(request=None, level=CustomSiteLogs.LogLevel.LEVEL_3_WARNING, 
                log_type=None, message=None, exception_message=None, 
                metadata=None, user_email=None, user_ip_address=None, inspect_stack=1):

    try:
        frame_info = inspect.stack()[inspect_stack]
        calling_frame = frame_info[0]
        file_name = os_path_basename(calling_frame.f_code.co_filename) 
        function_name = calling_frame.f_code.co_name
        line_number = calling_frame.f_lineno
    except:
        file_name = None
        function_name = None
        line_number = None
        
    if request is not None:
        user_ip_address = getUserIpAddress(request)
        if request.user.is_authenticated:
            user_email = request.user.email

    try:
        CustomSiteLogs.objects.create(
            level = level,
            log_type = log_type,
            message = message,
            exception_message = exception_message,
            source_file_name  =  file_name,
            source_function_name  =  function_name,
            source_line_number  =  line_number,
            metadata = metadata,
            user_email = user_email,
            user_ip_address = user_ip_address,
        )
    except:
        CustomSiteLogs.objects.create(
            level = CustomSiteLogs.LogLevel.LEVEL_1_DEBUG,
            log_type = "CreateLogError",
            message = "Unable to Create Log",
            exception_message = None,
            source_file_name  =  file_name,
            source_function_name  =  function_name,
            source_line_number  =  line_number,
            metadata = None,
            user_email = None,
            user_ip_address = None,
        )


