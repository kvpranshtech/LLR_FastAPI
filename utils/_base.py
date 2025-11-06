from django.apps import apps

required_data_fields_list = ('line_type', 'carrier_name', 'city', 'state', 'country')
required_data_fields_list_full = ('phonenumber', 'line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country')
required_data_fields_list_full_two = ('phonenumber', 'line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country','first_name','last_name','age','addresses','phones','emails')
endato_required_data_fields_list_full = ('phonenumber','first_name','last_name','age','addresses','phones','emails')
required_data_fields_list_no_phone = ('line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country')
csv_output_columns = ['LLR_PhoneNumber', 'LLR_LineType',  'LLR_DNCType', 'LLR_CarrierName', 'LLR_City', 'LLR_State', 'LLR_Country']
csv_output_columns_two = ['LLR_PhoneNumber', 'LLR_LineType',  'LLR_DNCType', 'LLR_CarrierName', 'LLR_City', 'LLR_State', 'LLR_Country','LLR_First_Name','LLR_Last_Name','LLR_Age','LLR_Addresses','LLR_Phones','LLR_Emails']
endato_csv_output_columns = ['LLR_PhoneNumber','LLR_First_Name','LLR_Last_Name','LLR_Age','LLR_Addresses','LLR_Phones','LLR_Emails']
apidata_model_required_fields = ('phonenumber', 'line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country')
endato_apidata_model_required_fields = ('phone_number', 'first_name', 'last_name', 'age', 'addresses', 'phones', 'emails')
userdatalogs_model_required_fields = ('number', 'line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country')
endato_userdatalogs_model_required_fields = ('number', 'first_name', 'last_name', 'age', 'addresses', 'phones', 'emails')
csvdata_model_required_fields = ('phonenumber', 'line_type', 'dnc_type', 'carrier_name', 'city', 'state', 'country')
endato_csvdata_model_required_fields = ('phonenumber', 'first_name', 'last_name', 'age', 'addresses', 'phones', 'emails')

# csvemaildata_model_required_fields = ('email', 'is_processed', 'email_format', 'mx_record', 'domain_exists', 'disposable_email', 'role_account')

csv_output_email_columns = ['LLR_Email', 'LLR_Processed',  'LLR_Email_Format', 'LLR_MX_Record', 'LLR_Domain_Exists', 'LLR_Disposable_Email', 'LLR_Role_Account', 'LLR_Common_Typo', 'LLR_SPF_Record', 'LLR_DKIM_Record', 'LLR_New_Domain', 'LLR_Valid_TLD', 'LLR_Is_Spam', 'LLR_Free_Domain']
csvemaildata_model_required_fields = ('email', 'is_processed', 'email_format', 'mx_record', 'domain_exists', 'disposable_email', 'role_account', 'common_typo', 'spf_record', 'dkim_record', 'new_domain', 'valid_tld', 'is_spam', 'feee_domain')


def returnDjModels(app_name, models_names_list):
    dj_models = []
    for model_name in models_names_list:
        dj_models.append(apps.get_model(app_label=app_name, model_name=model_name))
    return dj_models



def get_state(state_input):
    usa_states = [
        ['alabama', 'al'],
        ['alaska', 'ak'],
        ['arizona', 'az'],
        ['arkansas', 'ar'],
        ['california', 'ca'],
        ['colorado', 'co'],
        ['connecticut', 'ct'],
        ['delaware', 'de'],
        ['florida', 'fl'],
        ['georgia', 'ga'],
        ['hawaii', 'hi'],
        ['idaho', 'id'],
        ['illinois', 'il'],
        ['indiana', 'in'],
        ['iowa', 'ia'],
        ['kansas', 'ks'],
        ['kentucky', 'ky'],
        ['louisiana', 'la'],
        ['maine', 'me'],
        ['maryland', 'md'],
        ['massachusetts', 'ma'],
        ['michigan', 'mi'],
        ['minnesota', 'mn'],
        ['mississippi', 'ms'],
        ['missouri', 'mo'],
        ['montana', 'mt'],
        ['nebraska', 'ne'],
        ['nevada', 'nv'],
        ['new hampshire', 'nh'],
        ['new jersey', 'nj'],
        ['new mexico', 'nm'],
        ['new york', 'ny'],
        ['north carolina', 'nc'],
        ['north dakota', 'nd'],
        ['ohio', 'oh'],
        ['oklahoma', 'ok'],
        ['oregon', 'or'],
        ['pennsylvania', 'pa'],
        ['rhode island', 'ri'],
        ['south carolina', 'sc'],
        ['south dakota', 'sd'],
        ['tennessee', 'tn'],
        ['texas', 'tx'],
        ['utah', 'ut'],
        ['vermont', 'vt'],
        ['virginia', 'va'],
        ['washington', 'wa'],
        ['west virginia', 'wv'],
        ['wisconsin', 'wi'],
        ['wyoming', 'wy']
    ]

    state_input = state_input.lower()

    for state in usa_states:
        if state_input == state[1]:
            return state[0]
        elif state_input == state[0]:
            return state[1]
    return state_input


def format_number(number):
    suffixes = ['', 'K', 'M', 'B', 'T', 'Q', 'QQ', 'S', 'SS', 'O', 'N']
    number = int(number)  # Convert the number to an integer
    suffix_index = 0
    while number >= 1000 and suffix_index < len(suffixes) - 1:
        number /= 1000
        suffix_index += 1
    formatted_number = f"{number:.2f}{suffixes[suffix_index]}"
    return formatted_number


def format_dnctype(dnc_type):
    dnc_type = str(dnc_type).lower()
    if 'tcpa' in dnc_type or 'troll' in dnc_type or 'litigator' in dnc_type:
        return "litigator"
    elif 'dnc' in dnc_type or 'federal' in dnc_type or 'state' in dnc_type:
        return 'dnc'
    elif 'clean' in dnc_type:
        return 'clean'
    elif 'invalid' == dnc_type:
        return 'invalid'
    else:
        return 'n/a'
    
    
def returnCleanPhone_Or_None(number):
    if not number: return None 
    phone_clean = ''.join([n for n in number if n.isdigit()])[-10:]
    phone_clean = str(phone_clean).strip()
    if len(phone_clean) == 10:
        return phone_clean
    return None 


_verizon_carrier_contains_list = [
    'affinity cellular',
    "amp'd mobile",
    'caffee communications',
    'charity mobile',
    'credo mobile',
    'envie mobile',
    'flash wireless',
    'fmp wireless',
    'lexvor',
    'lively',
    'lucky wireless',
    'next g mobile',
    'page plus cellular',
    'pure mobile',
    'scratch wireless',
    'selectel wireless',
    'spectrum mobile',
    'talkforgood',
    'total wireless',
    'twigby',
    'visible',
    'wireless services us',
    'verizon'
]

_att_carrier_contains_list = [
    'allvoi wireless',
    'beast mobile',
    'black wireless',
    'cellular abroad',
    'choice wireless',
    'circle-k talk-and-go',
    'community phone',
    'cricket wireless',
    'easygo wireless',
    'feelsafe wireless',
    'firefly mobile',
    'freedompop',
    'freeup mobile',
    'fuzion mobile',
    'gtc wireless',
    'h2o wireless',
    'jolt mobile',
    'kddi mobile',
    'netbuddy',
    'never throttled',
    'pure talk',
    'pure unlimited',
    'rok mobile',
    'skyview wireless',
    'swt mobile',
    'voce',
    'zero11 wireless',
    'airlink mobile',
    'att', 
    'at&t', 
    'cingular', 
    'tracfone'
]

_tmobile_carrier_contains_list = [
    'access wireless',
    'airvoice wireless',
    'americas favorite mobile',
    'assist wireless',
    'assurance wireless',
    'brightspot',
    'bzrmobile',
    'charge',
    'china telecom ctexcel',
    'china unicom cuniq us',
    'cloven',
    'comcast',
    'common cents mobile',
    'cox',
    'datajack',
    'disney mobile',
    'earthlink',
    'embarq',
    'enc mobile',
    'espanol mobile',
    'espn mvp',
    'gen mobile',
    'giv mobile',
    'google fi wireless',
    'gosmart mobile',
    'helio',
    'helium mobile',
    'hello mobile',
    'ideal mobile',
    'internet on the go',
    'itel utel',
    'jaguar mobile',
    'jethro mobile',
    'karma mobility',
    'kidsconnect',
    'kroger wireless',
    'kynect',
    'liberty wireless',
    'lycamobile',
    'metro by t-mobile',
    'mi gente mobile',
    'mingo wireless',
    'mint mobile',
    'mobal',
    'movida',
    'nettalk connect',
    'netzero',
    'optimum mobile',
    'otg mobile',
    'otr mobile',
    'pond mobile',
    'prepayd wireless',
    'ptel mobile',
    'q link wireless',
    'qwest wireless',
    'reach mobile',
    'red state wireless',
    'ring plus, inc',
    'roam mobility',
    'safetynet wireless',
    'seawolf wireless',
    'shaka mobile',
    'simple mobile',
    'solavei',
    'speedtalk mobile',
    'spot mobile',
    'standup wireless',
    'sti mobile',
    'telcel america',
    'tello mobile',
    'teltik',
    'tempo telecom',
    'terracom wireless',
    'textnow',
    'the people operator usa',
    'total call mobile',
    'touch mobile',
    'truconnect',
    'trumpet mobile',
    'tuyo mobile',
    'ultra mobile',
    'univision mobile',
    'uppwireless',
    'uva mobile',
    'value wireless',
    'venn mobile',
    'virgin mobile usa',
    'votel mobile',
    'voyager mobile',
    'wow mobile pcs',
    'xcellular usa',
    'xfinity mobile',
    'zact',
    'zapp',
    'zuma prepaid',
    'simple freedom',
    'jump mobile',
    'tmobile', 
    't-mobile', 
    't mobile', 
    'metro pcs', 
    'sprint', 
    'boost', 
    'virgin',
    'power atlanta licenses',
    'openmarket',
]

_verizon_att_carrier_contains_list = [
    'clearway',
    'dataxoom',
    'mettel mobile'
]

_verizon_tmobile_carrier_contains_list = [
    'blue jay wireless',
    'boom! mobile',
    'boom mobile',
    'budget mobile',
    'byo wireless',
    'datapass',
    'ecomobile',
    'entouch wireless',
    'expo mobile',
    'hello us mobile',
    'infinium wireless',
    'proven services',
    'puppy wireless',
    'red stick wireless',
    'tag mobile',
    'ting mobile',
    'us mobile',
    'walmart family mobile',
    'knowroaming'
]

_att_tmobile_carrier_contains_list = [
    '7-eleven speak out wireless',
    'aeris communications inc',
    'aio wireless',
    'boost infinite',
    'boost mobile',
    'consumer cellular',
    'extremeconnect .me',
    'extremeconnect',
    'flexiroam',
    'good2go mobile',
    'ladybug wireless',
    'life wireless',
    'madstar mobile',
    'naked mobile',
    'net10 wireless',
    'patriot mobile',
    'republic wireless',
    'secure phone',
    'travelsim',
    'truphone',
    'unreal mobile',
    'uwt mobile',
    'telna',
    'project genesis'
]

_verizon_att_tmobile_carrier_contains_list = [
    'best cellular',
    'cellnuvo',
    'chatsim',
    'datablaze',
    'familytalk wireless',
    'global data telecom',
    'iq cellular',
    'kajeet',
    'kore wireless',
    'mastrack (mobile asset solutions)',
    'millenicom',
    'ntt docomo usa',
    'phonata',
    'pix wireless',
    'pulse cellular',
    'red pocket mobile',
    'sierra wireless',
    'straight talk',
    'telit',
    'tracfone',
    'ubigi',
    'wing',
    'zing wireless'
]



def returnCleanCarrierName(carrier_name):
    carrier_name = str(carrier_name).strip().lower()
    if any(substr in carrier_name for substr in _verizon_carrier_contains_list):
        return 'verizon'
    elif any(substr in carrier_name for substr in _att_carrier_contains_list):
        return 'at&t'
    elif any(substr in carrier_name for substr in _tmobile_carrier_contains_list):
        return 'tmobile'
    elif any(substr in carrier_name for substr in _verizon_att_carrier_contains_list):
        return 'verizon or at&t'
    elif any(substr in carrier_name for substr in _verizon_tmobile_carrier_contains_list):
        return 'verizon or tmobile'
    elif any(substr in carrier_name for substr in _att_tmobile_carrier_contains_list):
        return 'at&t or tmobile'
    elif any(substr in carrier_name for substr in _verizon_att_tmobile_carrier_contains_list):
        return 'verizon or at&t or tmobile'
    elif 'twilio' in carrier_name:
        return 'twilio'
    else:
        return carrier_name