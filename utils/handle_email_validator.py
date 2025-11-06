import re
import dns.resolver
import smtplib
from datetime import datetime
from tld import get_tld
import pandas as pd
import logging
from api.models import DisposableEmail,FreeDomains,Role

# Configure logging
logger = logging.getLogger(__name__)
# Validate email format
def validate_email_format(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(regex, email):
        return 'valid'
    else:
        return 'invalid'


# Check MX records and validate domain
# def validate_mx_record(email):
#     domain = email.split('@')[-1]
#     try:
#         answers = dns.resolver.resolve(domain, 'MX')
#         if len(answers) > 0:
#             return 'available'
#     except dns.resolver.NXDOMAIN:
#         return 'not available'


def validate_mx_record(email):
    domain = email.split('@')[-1]
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        if len(answers) > 0:
            return 'available'
        else:
            return 'not available'
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        # No MX record found or DNS lookup failed
        return 'not available'
    except Exception as e:
        print(f"Unexpected MX lookup error for {domain}: {e}")
        return 'not available'

# Check if domain exists by pinging DNS records
# def validate_domain_exists(email):
#     domain = email.split('@')[-1]
#     try:
#         dns.resolver.resolve(domain, 'A')
#         return True
#     except dns.resolver.NXDOMAIN:
#         try:
#             dns.resolver.resolve(domain, 'AAAA')
#             return True
#         except dns.resolver.NXDOMAIN:
#             return False

def validate_domain_exists(email):
    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'A')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        try:
            dns.resolver.resolve(domain, 'AAAA')
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            return False
    except Exception as e:
        print(f"Domain existence check failed for {domain}: {e}")
        return False

# Perform SMTP validation
# def validate_smtp(email):
#     domain = email.split('@')[-1]
#     try:
#         mx_records = dns.resolver.resolve(domain, 'MX')
#         smtp_server = str(mx_records[0].exchange)
#         with smtplib.SMTP(smtp_server) as smtp:
#             smtp.helo('example.com')
#             smtp.mail('info@example.com')
#             code, _ = smtp.rcpt(email)
#             return code == 250
#     except Exception:
#         return False
def validate_smtp(email):
    domain = email.split('@')[-1]
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        smtp_server = str(mx_records[0].exchange)
        with smtplib.SMTP(smtp_server, timeout=10) as smtp:
            smtp.helo('example.com')
            smtp.mail('info@example.com')
            code, _ = smtp.rcpt(email)
            return code == 250
    except Exception as e:
        print(f"SMTP validation failed for {email}: {e}")
        return False

# Detect disposable email domains
def is_disposable_email(email):
    disposable_domains = list(DisposableEmail.objects.values('email'))
    domain = email.split('@')[-1]
    return domain in disposable_domains


# Detect role-based email addresses
def is_role_account(email):
    role_based_usernames = list(Role.objects.values('role'))
    username = email.split('@')[0].lower()
    return username in role_based_usernames


# Detect common typos in domain names
def is_common_typo(email):
    domain = email.split('@')[-1]
    common_typos = {
       "gmail.com" : "gmail.com",
        "yahooo.com" : "yahoo.com",
        "outllook.com" : "outlook.com",
        "hotmial.com" : "hotmail.com",
        "gnail.com" : "gmail.com",
        "googl.com" : "google.com",
        "ymail.com" : "yahoo.com",
        "yahho.com" : "yahoo.com",
        "yaho.com" : "yahoo.com",
        "hotmail.co" : "hotmail.com",
        "hotmail.con" : "hotmail.com",
        "hotmal.com" : "hotmail.com",
        "hormail.com" : "hotmail.com",
        "outlok.com" : "outlook.com",
        "outllok.com" : "outlook.com",
        "icloud.co" : "icloud.com",
        "icloud.con" : "icloud.com",
        "gmaill.com" : "gmail.com",
        "gmial.com" : "gmail.com",
        "gemail.com" : "gmail.com",
        "gmaik.com" : "gmail.com",
        "me.com" : "icloud.com",  
        "msn.co" : "msn.com",
        "msnn.com" : "msn.com",
        "gamil.co" : "gmail.com",
        "protonmial.com" : "protonmail.com",
        "protomail.com" : "protonmail.com",
        "protnmail.com" : "protonmail.com",
        "aol.cm" : "aol.com",
        "aoll.com" : "aol.com",
        "zoho.cm" : "zoho.com",
        "zohomail.com" : "zoho.com",
        "gmai.com" : "gmail.com",
        "yahoom.com" : "yahoo.com",
        "yahol.com" : "yahoo.com",
        "yhoo.com" : "yahoo.com",
        "gmal.com" : "gmail.com",
        "gmail.co" : "gmail.com",
        "g-mail.com" : "gmail.com",
        "gimail.com" : "gmail.com",
        "gmail.con" : "gmail.com",
        "live.co" : "live.com",
        "liv.com" : "live.com",
        "aol.con" : "aol.com",
        "fastmial.com" : "fastmail.com",
        "fassmail.com" : "fastmail.com"
    }
    domain = common_typos.get(domain)
    return True if domain else False


# Check SPF record for domain
# def check_spf(email):
#     domain = email.split('@')[-1]
#     try:
#         answers = dns.resolver.resolve(domain, 'TXT')
#         for rdata in answers:
#             if 'v=spf1' in rdata.to_text():
#                 return True
#     except Exception:
#         return False
#     return False

def check_spf(email):
    domain = email.split('@')[-1]
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        for rdata in answers:
            if 'v=spf1' in rdata.to_text():
                return True
        return False
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        return False
    except Exception as e:
        print(f"SPF check error for {domain}: {e}")
        return False

# Check DKIM record for domain
# def check_dkim(email):
#     domain = email.split('@')[-1]
#     dkim_record = f"default._domainkey.{domain}"
#     try:
#         answers = dns.resolver.resolve(dkim_record, 'TXT')
#         return len(answers) > 0
#     except dns.resolver.NXDOMAIN:
#         return False
#     except Exception:
#         return False
def check_dkim(email):
    domain = email.split('@')[-1]
    dkim_record = f"default._domainkey.{domain}"
    try:
        answers = dns.resolver.resolve(dkim_record, 'TXT')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        return False
    except Exception as e:
        print(f"DKIM check error for {domain}: {e}")
        return False

# Check DMARC record for domain
# def check_dmarc(email):
#     domain = email.split('@')[-1]
#     dmarc_record = f"_dmarc.{domain}"
#     try:
#         answers = dns.resolver.resolve(dmarc_record, 'TXT')
#         return len(answers) > 0
#     except dns.resolver.NXDOMAIN:
#         return False

def check_dmarc(email):
    domain = email.split('@')[-1]
    dmarc_record = f"_dmarc.{domain}"
    try:
        answers = dns.resolver.resolve(dmarc_record, 'TXT')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        # No DMARC record found or DNS issue
        return False
    except Exception as e:
        print(f"Unexpected DMARC error for {domain}: {e}")
        return False
        
# Check if the domain is recently registered (placeholder for WHOIS API)
def is_new_domain(email):
    domain = email.split('@')[-1]
    recently_registered_domains = ["example-new.com", "test123.com"]
    return domain in recently_registered_domains


# Validate Top-Level Domain (TLD)
def validate_tld(email):
    try:
        tld = get_tld(email, as_object=True).fld.split('.')[-1]
        valid_tlds = ["com", "net", "org", "io", "co", "ai", "info", "ly", "edu", "gov"]
        return tld in valid_tlds
    except Exception:
        return False



import dns.resolver
import re

# List of DNSBLs
dnsbl_list = [
    "zen.spamhaus.org",       
    "bl.spamcop.net",         
    "dnsbl.sorbs.net",        
    "b.barracudacentral.org", 
    "dnsbl-1.uceprotect.net", 
    "dnsbl-2.uceprotect.net", 
    "dnsbl-3.uceprotect.net", 
    "bl.rbl.msrbl.net",       
    "blacklist.woody.ch",     
    "cbl.abuseat.org",        
    "bl.spamrbl.com",         
    "psbl.surriel.com",       
    "db.wpbl.info",           
    "dnsbl.spfbl.net",       
    "dul.dnsbl.sorbs.net",    
    "multi.surbl.org",        
    "noptr.spamrats.com",     
    "sbl.spamhaus.org",       
    "xbl.spamhaus.org"        
]


def check_domain_in_dnsbl(email):
    domain = email.split('@')[1]
    resolver = dns.resolver.Resolver()
    resolver.timeout = 10  # Increase timeout to 10 seconds
    resolver.lifetime = 15  # Set the maximum lifetime for a DNS query

    for dnsbl in dnsbl_list:
        try:
            query = '.'.join(reversed(domain.split('.'))) + '.' + dnsbl
            # Resolve DNS query for blacklisted domain
            dns.resolver.resolve(query, "A")
            logger.info(f"Domain {domain} is listed in {dnsbl}.")
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            continue  # Ignore these exceptions and continue with the next DNSBL
        except Exception as e:
            # Catch all other DNS exceptions (SERVFAIL, network errors, etc.)
            # Log the error but don't fail the entire validation
            logger.warning(f"DNSBL check failed for {dnsbl} with error: {str(e)}")
            continue

    logger.debug(f"Domain {domain} is not listed in any of the DNSBLs.")
    return False





def renderCsvFileOnUpload(filepath):
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    df_columns = list(df.columns)
    df_columns_dict = {}
    if 'EMV_Email' in df_columns:
        df_columns_dict['EMV_Email'] = 'EMV_Email_Old'
    if df_columns_dict:
        df.rename(columns = df_columns_dict, inplace = True)

    total_records = df.shape[0]
    head_data = df.head(n=10)
    header = df.to_dict(orient='records')[0].keys()
    return total_records, header, head_data


    
def cleanCSVreturnTotalRows(filepath, phone_col):
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)

    df_columns = list(df.columns)
    df_columns_dict = {}
    if 'EMV_Email' in df_columns:
        df_columns_dict['EMV_Email'] = 'EMV_Email_Old'
    if df_columns_dict:
        df.rename(columns = df_columns_dict, inplace = True)

    df.dropna(how="all", inplace=True)
    datas = df.to_dict(orient='records')
    for data in datas[:]:
        if len(phone_col) == 10:
            data['EMV_Email'] = phone_col
        else:
            data['EMV_Email'] = 'invalid_data'
    new_df = pd.DataFrame(datas)
    # new_df.dropna(axis=0, subset=['LLR_PhoneNumber'], inplace=True)
    new_df.to_csv(filepath, encoding='latin-1', header=True, index=False)
    return new_df.shape[0]



def returnCsvTotalRecords(filepath):
    df = pd.read_csv(filepath, encoding='latin-1', low_memory=True, on_bad_lines='skip', skip_blank_lines=True, dtype=str)
    return df.shape[0]



def is_free_domain(email):
    domain = email.split('@')[-1]
    domain_exist = FreeDomains.objects.filter(domain=domain).first()
    if domain_exist:
        return True
    else:
        return False


