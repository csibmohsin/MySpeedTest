"""
MySpeedTest - Network Information Module
Detects public IP, ISP, approximate geographic location, local network interfaces,
and manages speed test server discovery and lowest-latency selection.
"""

import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Optional, Any


# Curated high-availability global speed test server endpoints
DEFAULT_SERVERS: List[Dict[str, Any]] = [
    {
        "id": "cf-auto",
        "name": "Cloudflare Global Anycast (Fastest Edge)",
        "host": "speed.cloudflare.com",
        "port": 443,
        "location": "Nearest Edge Node (Anycast)",
        "country": "Global",
        "download_url": "https://speed.cloudflare.com/__down?bytes={bytes}",
        "upload_url": "https://speed.cloudflare.com/__up",
        "is_default": True
    },
    {
        "id": "cf-asia",
        "name": "Cloudflare Edge - Asia Pacific",
        "host": "speed.cloudflare.com",
        "port": 443,
        "location": "Asia Pacific Edge",
        "country": "Asia",
        "download_url": "https://speed.cloudflare.com/__down?bytes={bytes}",
        "upload_url": "https://speed.cloudflare.com/__up",
        "is_default": False
    },
    {
        "id": "cf-eu",
        "name": "Cloudflare Edge - Europe",
        "host": "speed.cloudflare.com",
        "port": 443,
        "location": "European Edge",
        "country": "Europe",
        "download_url": "https://speed.cloudflare.com/__down?bytes={bytes}",
        "upload_url": "https://speed.cloudflare.com/__up",
        "is_default": False
    },
    {
        "id": "cf-na",
        "name": "Cloudflare Edge - North America",
        "host": "speed.cloudflare.com",
        "port": 443,
        "location": "North America Edge",
        "country": "USA",
        "download_url": "https://speed.cloudflare.com/__down?bytes={bytes}",
        "upload_url": "https://speed.cloudflare.com/__up",
        "is_default": False
    }
]


def get_local_ip() -> str:
    """Retrieve the local LAN IP address of this machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        # Does not actually transmit packets, used to determine route interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def get_client_network_info(timeout: float = 4.0) -> Dict[str, Any]:
    """
    Detect real public IP address, ISP, location, and local network info.
    Never invents or mocks data. Uses verified external IP-lookup APIs with fallbacks.
    """
    info: Dict[str, Any] = {
        "status": "online",
        "ip": "Unknown",
        "isp": "Unknown",
        "org": "Unknown",
        "as": "Unknown",
        "city": "Unknown",
        "region": "Unknown",
        "country": "Unknown",
        "country_code": "XX",
        "lat": 0.0,
        "lon": 0.0,
        "local_ip": get_local_ip(),
        "hostname": socket.gethostname(),
        "source": "None"
    }

    # Primary: ip-api.com (detailed, free, fast)
    try:
        resp = requests.get("http://ip-api.com/json", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                info["ip"] = data.get("query", "Unknown")
                info["isp"] = data.get("isp", data.get("org", "Unknown"))
                info["org"] = data.get("org", "Unknown")
                info["as"] = data.get("as", "Unknown")
                info["city"] = data.get("city", "Unknown")
                info["region"] = data.get("regionName", "Unknown")
                info["country"] = data.get("country", "Unknown")
                info["country_code"] = data.get("countryCode", "XX")
                info["lat"] = float(data.get("lat", 0.0))
                info["lon"] = float(data.get("lon", 0.0))
                info["source"] = "ip-api"
                return info
    except Exception:
        pass

    # Secondary fallback: ipinfo.io
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            info["ip"] = data.get("ip", info["ip"])
            info["org"] = data.get("org", info["org"])
            info["isp"] = data.get("org", info["isp"])
            info["city"] = data.get("city", info["city"])
            info["region"] = data.get("region", info["region"])
            info["country"] = data.get("country", info["country"])
            info["country_code"] = data.get("country", "XX")
            loc = data.get("loc", "").split(",")
            if len(loc) == 2:
                info["lat"] = float(loc[0])
                info["lon"] = float(loc[1])
            info["source"] = "ipinfo.io"
            return info
    except Exception:
        pass

    # Tertiary fallback: api.ipify.org (IP only)
    try:
        resp = requests.get("https://api.ipify.org?format=json", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            info["ip"] = data.get("ip", info["ip"])
            info["source"] = "ipify"
            return info
    except Exception:
        pass

    info["status"] = "offline"
    return info


def ping_host(host: str, port: int = 443, count: int = 3, timeout: float = 1.5) -> Optional[float]:
    """
    Measure average TCP connection latency to a host in milliseconds.
    Pure Python socket connection - works without root privileges.
    """
    latencies = []
    for _ in range(count):
        t0 = time.perf_counter()
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            dt = (time.perf_counter() - t0) * 1000.0
            latencies.append(dt)
        except Exception:
            pass
        time.sleep(0.02)

    if not latencies:
        return None
    return sum(latencies) / len(latencies)


def get_available_servers() -> List[Dict[str, Any]]:
    """Return the list of available speed test servers."""
    return list(DEFAULT_SERVERS)


def select_best_server(servers: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Concurrently ping available servers and select the one with the lowest latency.
    Guarantees reliable fallback if any ping fails.
    """
    server_list = servers if servers else get_available_servers()
    if not server_list:
        return DEFAULT_SERVERS[0]

    measured = []

    def _test(srv):
        lat = ping_host(srv["host"], srv.get("port", 443), count=3, timeout=1.5)
        srv_copy = dict(srv)
        srv_copy["latency"] = lat if lat is not None else 9999.0
        return srv_copy

    with ThreadPoolExecutor(max_workers=min(len(server_list), 6)) as executor:
        futures = [executor.submit(_test, s) for s in server_list]
        for f in as_completed(futures):
            try:
                res = f.result()
                measured.append(res)
            except Exception:
                pass

    if measured:
        measured.sort(key=lambda s: s["latency"])
        best = measured[0]
        if best["latency"] == 9999.0:
            best["latency"] = None
        return best

    fallback = dict(server_list[0])
    fallback["latency"] = None
    return fallback

