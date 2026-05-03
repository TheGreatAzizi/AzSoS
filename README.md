# AZSOS

**English:** AZSOS is an offline-first emergency content cache for Windows. It stores, verifies, searches, updates, and shares trusted `.azsos` packages without depending on a central server.

**فارسی:** AZSOS یک کش آفلاین‌اول برای محتوای ضروری در ویندوز است. این برنامه بسته‌های `.azsos` را نگه‌داری، اعتبارسنجی، جستجو، به‌روزرسانی و بدون نیاز به سرور مرکزی به‌صورت محلی اشتراک‌گذاری می‌کند.

Default package source / منبع پیش‌فرض بسته‌ها:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

Default update source / منبع پیش‌فرض آپدیت نرم‌افزار:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

## Documentation / مستندات

GitHub documentation is available in **English and Persian**. The in-app manual is **English only**.

مستندات گیت‌هاب به **انگلیسی و فارسی** موجود است. راهنمای داخل برنامه فقط **انگلیسی** است.

- [English documentation index](docs/README_EN.md)
- [فهرست مستندات فارسی](docs/README_FA.md)
- [In-app English manual](docs/IN_APP_MANUAL_EN.md)
- [English user guide](docs/USER_GUIDE_EN.md)
- [راهنمای فارسی کاربر](docs/USER_GUIDE_FA.md)

## What it does

- Imports and verifies `.azsos` packages
- Searches installed content offline with SQLite FTS5
- Opens package content locally in the browser
- Fetches packages from GitHub trees, GitHub Releases, direct `.azsos` links, local folders, or registry JSON files
- Lets users add their own Git/content sources inside the app
- Installs multiple remote packages after verification
- Deletes installed packages
- Exports installed packages back to `.azsos`
- Shares installed packages over local Wi-Fi/hotspot/LAN
- Shows a QR code for local share
- Lets users mark publisher fingerprints as trusted on their device
- Checks software updates from the UPDATE branch
- Includes an English Docs tab inside the desktop app

## قابلیت‌ها

- وارد کردن و اعتبارسنجی بسته‌های `.azsos`
- جستجوی آفلاین در محتوای نصب‌شده با SQLite FTS5
- باز کردن محتوای بسته در مرورگر سیستم
- دریافت بسته از GitHub tree، GitHub Releases، لینک مستقیم `.azsos`، فولدر محلی یا registry JSON
- افزودن source جدید داخل خود برنامه
- نصب چند بسته ریموت بعد از verify
- حذف بسته‌های نصب‌شده
- خروجی گرفتن از بسته نصب‌شده به فایل `.azsos`
- اشتراک‌گذاری محلی روی Wi-Fi، hotspot یا LAN
- نمایش QR برای Local Share
- Trust کردن fingerprint ناشر روی همان دستگاه
- بررسی آپدیت نرم‌افزار از branch `UPDATE`
- تب Docs انگلیسی داخل نرم‌افزار

## Social / project links

- X: https://x.com/the_azzi
- GitHub: https://github.com/TheGreatAzizi
- Self-hosted Git: https://git.theazizi.ir/TheAzizi
- Telegram: https://t.me/luluch_code

## Install for development / نصب برای توسعه

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_app.py
```

## Build a Windows executable / ساخت فایل اجرایی ویندوز

```powershell
pip install -r requirements-dev.txt
pyinstaller --noconsole --onefile --name AZSOS run_app.py
```

Or use / یا:

```powershell
.\scripts\build_windows.ps1
```

## Build a test package / ساخت بسته تست

```powershell
python azsos.py keygen --out-dir keys

python azsos.py pack `
  --content examples/first-aid/content `
  --id first-aid.fa.demo `
  --title "First Aid Demo" `
  --version 0.1.0 `
  --publisher-name "AZSOS Demo Publisher" `
  --key keys/publisher_private.pem `
  --out dist/first-aid-demo.azsos
```

## CLI examples / مثال‌های CLI

```powershell
python azsos.py verify sample-packages/first-aid-demo.azsos
python azsos.py install sample-packages/first-aid-demo.azsos
python azsos.py search help
python azsos.py catalog fetch "https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages"
```

Build a registry JSON for publishing / ساخت registry برای انتشار:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## Trust model / مدل اعتماد

Discovery is not trust. A package is installed only after AZSOS verifies package structure, `hashes.json`, SHA-256 hashes, Ed25519 signature, and optional registry SHA-256.

کشف بسته به معنی اعتماد نیست. AZSOS فقط بعد از بررسی ساختار بسته، `hashes.json`، هش‌های SHA-256، امضای Ed25519 و در صورت وجود SHA-256 رجیستری، بسته را نصب می‌کند.

Users can mark a publisher fingerprint as trusted locally after checking it through a trusted channel.

کاربر می‌تواند بعد از بررسی fingerprint ناشر از یک مسیر قابل‌اعتماد، آن ناشر را فقط روی دستگاه خودش trusted کند.

## Format / فرمت

`.azsos` files are ZIP packages using the `azsos.v1` format:

```text
package.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
```

See / ببینید: [`docs/FORMAT.md`](docs/FORMAT.md)

## License / لایسنس

MIT
