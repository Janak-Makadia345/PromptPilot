import os

def clear_proxy_env_vars():
    """Clear proxy-related environment variables."""
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        os.environ.pop(var, None)