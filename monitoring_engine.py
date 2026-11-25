import ipaddress
import platform
import subprocess
import time

def ping_address(address):
    """Ping a validated IP address; never executes through a shell."""
    try:
        ipaddress.ip_address(address)
    except (ValueError, TypeError):
        return False, None
    system = platform.system().lower()
    if system == "windows":
        args = ["ping", "-n", "1", "-w", "1200", address]
    else:
        args = ["ping", "-c", "1", address]
    started = time.perf_counter()
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=2.5, shell=False)
        if result.returncode == 0:
            return True, round((time.perf_counter()-started)*1000, 2)
    except (subprocess.TimeoutExpired, OSError):
        pass
    return False, None
