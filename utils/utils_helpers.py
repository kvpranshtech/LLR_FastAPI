import os

def get_current_env():
    env = os.environ.get("LLR_ENV", "").lower()
    if env in ["local", "staging", "live"]:
        return env

def get_proxy_settings():
    env = get_current_env()
    if env == "local":
        proxy_domain = str(str(os.environ.get('PROXY_SERVER_DOMAIN_LOCAL')).strip())
        proxy_token = str(str(os.environ.get('PROXY_SERVER_TOKEN_LOCAL')).strip())

    else:
        proxy_domain = str(str(os.environ.get('PROXY_SERVER_DOMAIN')).strip())
        proxy_token = str(str(os.environ.get('PROXY_SERVER_TOKEN')).strip())

    server_ip = str(str(os.environ.get('SERVER_IP')).strip())

    if not proxy_domain or not proxy_token:
        raise RuntimeError(f"Proxy settings not set for environment '{env}'")

    return proxy_domain, proxy_token, server_ip
