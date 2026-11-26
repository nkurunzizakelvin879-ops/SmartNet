# SmartNet — Network Management

SmartNet ni Flask app yo gucunga ibikoresho bya network n'abakiriya.

## Ibirimo
- Login na dashboard ya admin
- Device inventory: add, status, delete
- Customer management: add, view, delete
- Account settings
- Monthly fees (RWF)
- SQLite by default; optional MySQL via `DATABASE_URL`
- CSRF protection and protected session cookies
- Network ping scan: online/offline, latency (ms), last successful check (UTC)

## Windows setup
1. Clone or download the project and open PowerShell in its folder.
2. `py -m venv .venv` then `..venv\Scripts\Activate.ps1`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`; configure a strong `SECRET_KEY` and optionally `ADMIN_PASSWORD`.
5. Run `python run.py` and visit http://127.0.0.1:5000

## Live network monitoring
SmartNet runs a background ping scan every 60 seconds by default (configurable using `MONITOR_INTERVAL_SECONDS`). The Devices table refreshes status data approximately every 15 seconds. You can also click **Run network scan** to request an immediate scan. It pings only registered, valid IP addresses, using bounded timeouts, and stores online/offline status, approximate round-trip latency, and last successful ping timestamp (UTC). Devices without IP addresses are skipped. A ping failure does not necessarily prove a device is down; firewalls may block ICMP. Set `MONITORING_ENABLED=0` in `.env` to disable the background scanner.

Monitoring database fields are added through a small, additive startup migration; existing device records and customer data are retained.

## Initial administrator
Default email: `admin@smartnet.local`. Set `ADMIN_PASSWORD` before first launch or save the temporary password printed to the terminal.

## MySQL (optional)
Set `DATABASE_URL`, for example: `mysql+pymysql://username:password@127.0.0.1:3306/smartnet_db?charset=utf8mb4`.

## Security / deployment
Use a strong secret, HTTPS for secure cookies, a production WSGI server, regular backups, and only monitor devices you administer or have permission to check. The Flask development server is for local development.


## Phase 3: Live dashboard overview

- Dashboard network-health percentage and status counts are recalculated from registered devices.
- Dashboard totals and monthly active-customer revenue update automatically approximately every 15 seconds without reloading the page.
- A live-updated timestamp indicates when the dashboard refresh succeeded.
- The dashboard overview endpoint is authenticated and returns summary JSON for the logged-in user.


## Phase 4: Device management improvements

- Search registered devices by name, IP address, type, location, or row text.
- Filter the table by status and device type.
- Edit device name, type, IP address, location, and notes.
- Existing manual scan and periodic status refresh remain available.
