from typing import Optional

from fastapi import Request
from user_agents import parse
import geoip2.database

from auth.config import config

try:
    _geoip_reader = geoip2.database.Reader(config.GEOIP_DB_PATH)
except Exception:
    _geoip_reader = None

TRUSTED_PROXIES: set[str] = {"127.0.0.1", "::1"}


def _get_country_by_ip(
    ip_address: str,
) -> Optional[str]:
    if _geoip_reader is None or ip_address is None:
        return None
    try:
        response = _geoip_reader.country(ip_address)
        return response.country.iso_code or None
    except Exception:
        return None


def _get_real_ip(
    request: Request,
) -> Optional[str]:
    direct_ip = request.client.host if request.client else None

    if direct_ip in TRUSTED_PROXIES:
        xff = request.headers.get("x-forwarded-for", "")
        if xff:
            return xff.split(",")[0].strip()

    return direct_ip or None


def get_client_info(
    request: Request,
) -> dict:
    ip_address = _get_real_ip(request)

    user_agent_string = request.headers.get("user-agent", "")
    ua = parse(user_agent_string)
    device_name = (
        ua.device.model if ua.device.model else f"{ua.os.family} / {ua.browser.family}"
    )
    if ua.is_mobile:
        device_type = "Mobile"
    elif ua.is_tablet:
        device_type = "Tablet"
    elif ua.is_pc:
        device_type = "PC"
    elif ua.is_bot:
        device_type = "Bot"
    else:
        device_type = "Unknown"

    country = _get_country_by_ip(ip_address)

    return {
        "ip_address": ip_address,
        "user_agent": user_agent_string,
        "device_name": device_name,
        "device_type": device_type,
        "country": country,
    }
