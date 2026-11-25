# SmartNet — Network Management

SmartNet ni urubuga rwa Flask rwo gucunga ibikoresho bya network n'abakiriya.

## Ibirimo
- Login na dashboard ya admin
- Device inventory: kongeramo, kureba, guhindura status no gusiba devices
- Customer management: kongeramo, kureba no gusiba abakiriya
- Account settings: guhindura izina, email na password
- Monthly fee summary (RWF)
- SQLite ku buryo busanzwe; MySQL ishobora gukoreshwa ukoresheje `DATABASE_URL`
- CSRF protection ku mafomu yose ya POST
- Session cookies zirinzwe na HTTP-only na SameSite

## Gukoresha kuri Windows
1. Kuramo ZIP cyangwa clone repository, hanyuma fungura PowerShell muri folder ya `SmartNet`.
2. Kora virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Shyiramo dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Kora kopi ya environment file:
   ```powershell
   Copy-Item .env.example .env
   ```
5. Fungura `.env`, ushyiremo `SECRET_KEY` ikomeye. Ushobora kuyibyaza ukoresheje:
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Ushyireho na `ADMIN_PASSWORD` mbere yo gutangira bwa mbere niba ushaka guhitamo password ya admin. Ntushyireho password yoroshye.
6. Tangiza:
   ```powershell
   python run.py
   ```
7. Fungura http://127.0.0.1:5000

## Konti ya mbere ya admin
- Email isanzwe: `admin@smartnet.local` (ushobora kuyihindura ukoresheje `ADMIN_EMAIL` muri `.env`).
- Niba `ADMIN_PASSWORD` itashyizweho, SmartNet ikora password y'agateganyo ikomeye ikayerekana muri terminal bwa mbere gusa. Yibike, winjire, hanyuma uhite uyihindura muri **Settings**.
- Niba admin asanzwe ari muri database, SmartNet ntihindura password ye cyangwa ngo isibe amakuru ye.

## MySQL (optional)
Kora database yawe, hanyuma shyira `DATABASE_URL` muri `.env`, urugero:
`mysql+pymysql://username:password@127.0.0.1:3306/smartnet_db?charset=utf8mb4`
Encode special characters ziri muri password ya database.

## Igenamiterere rya production
- Shyiraho `SECRET_KEY` ikomeye kandi uyigire ibanga.
- Shyiraho `COOKIE_SECURE=1` gusa igihe urubuga rukorera kuri HTTPS.
- `FLASK_DEBUG` isanzwe ni `0`; ntukayishyire kuri `1` kuri public server.
- Koresha WSGI server ibereye production; Flask development server igenewe development gusa.
- Bika backup ya database buri gihe mbere yo gukora migrations cyangwa impinduka zikomeye.

## Live Network Monitoring (branch feature/live-network-monitoring)
- Kuri Devices, kanda **Check now** kugira ngo SmartNet ipinge IP address.
- Status, latency (ms), last check na last seen bibikwa.
- Alert history iboneka kuri Alerts, igihe status yahindutse (Unknown initial status ntibara alert).
- ICMP/ping ishobora kuba blocked na firewall ya device cyangwa network; Offline hano ntibihamya ko device yazimye.
- Ubu checks ni manual (Check now); recurring background monitoring iracyari mu phase ikurikira.
- Startup migration yongeramo monitoring columns mu table ya device; backup database mbere yo upgrade.

## Ibitari byashyirwamo
Recurring background monitoring, admin user management na database migrations zikomeye biracyategereje. Background images, Font Awesome na Google Fonts bishobora gusaba internet.
