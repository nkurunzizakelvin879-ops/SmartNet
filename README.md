# SmartNet — Network Management

## Ibirimo
- Login ya admin na dashboard
- Device inventory: kongeramo, kureba, guhindura status no gusiba
- Customer management: kongeramo, kureba no gusiba abakiriya
- Account Settings: guhindura izina, username/email na password ukoresheje page ya Settings
- Monthly fee summary
- Responsive navy/cyan interface na network icons
- SQLite default; MySQL ishobora gukoreshwa ukoresheje DATABASE_URL

## Gukoresha kuri Windows
1. Kuramo ZIP, fungura PowerShell muri folder ya `SmartNet`.
2. `py -m venv .venv`
3. `\.venv\Scripts\Activate.ps1`
4. `python -m pip install --upgrade pip`
5. `pip install -r requirements.txt`
6. Kora copy ya `.env.example` uyite `.env`, uhindure SECRET_KEY.
7. `python run.py`
8. Fungura http://127.0.0.1:5000

## Login ya mbere
Email: `admin@smartnet.local`
Password: `ChangeMe123!`

Hindura iyi password muri **Settings** nyuma yo kwinjira. Muri Settings ushobora no guhindura username/email. Guhindura password bisaba kwemeza password ya kera; password nshya igomba kugira nibura inyuguti 8.

## MySQL
Kora database yawe, hanyuma shyira DATABASE_URL muri `.env` ukoresheje format iri muri `.env.example`. Encode special characters ziri muri password.

## Icyitonderwa
Device status muri iyi version ihindurwa n'umukoresha; ntirakora automatic ping cyangwa live monitoring. Forms zikeneye CSRF protection, admin user management na migrations mbere yo gushyirwa kuri public production server. Server background image, Font Awesome na Google Fonts bisaba internet.
"# SmartNet" 
