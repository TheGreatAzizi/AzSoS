# AZSOS

> زبان: **فارسی** | [English](README_EN.md)

AZSOS یک کش آفلاین‌اول برای محتوای ضروری روی ویندوز است. این برنامه بسته‌های قابل‌اعتماد `.azsos` را نگه‌داری، اعتبارسنجی، جستجو، به‌روزرسانی، خروجی‌گیری و در شبکه محلی اشتراک‌گذاری می‌کند؛ بدون اینکه به یک سرور مرکزی وابسته باشد.

## سورس‌های پیش‌فرض

سورس پیش‌فرض بسته‌ها:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

سورس پیش‌فرض آپدیت نرم‌افزار:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

## قابلیت‌های AZSOS

- وارد کردن و اعتبارسنجی بسته‌های `.azsos`.
- جستجوی آفلاین در محتوای نصب‌شده با SQLite FTS5.
- باز کردن محتوای HTML بسته در مرورگر سیستم.
- دریافت محتوا از GitHub branch، GitHub Releases، لینک مستقیم `.azsos`، فولدر محلی یا فایل registry JSON.
- افزودن، ذخیره و حذف سورس‌های محتوا داخل خود برنامه.
- نصب چند بسته ریموت بعد از verify.
- inspect کردن بسته قبل از نصب.
- حذف بسته‌های نصب‌شده.
- خروجی گرفتن از بسته نصب‌شده به فایل `.azsos`.
- اشتراک‌گذاری محلی روی Wi-Fi، hotspot یا LAN.
- نمایش QR برای Local Share.
- trust کردن fingerprint ناشر فقط روی دستگاه کاربر.
- بررسی آپدیت نرم‌افزار از branch `UPDATE`.
- تب Docs انگلیسی و Markdown-style داخل برنامه.

## مستندات

- [فهرست مستندات فارسی](docs/fa/README.md)
- [English documentation index](docs/en/README.md)
- [راهنمای کاربر](docs/fa/USER_GUIDE.md)
- [راهنمای انتشار بسته‌ها](docs/fa/PUBLISHING_PACKAGES.md)
- [راهنمای انتشار روی GitHub](docs/fa/GITHUB_PUBLISHING.md)
- [راهنمای انتشار آپدیت نرم‌افزار](docs/fa/UPDATES.md)
- [مشخصات فرمت](docs/fa/FORMAT.md)
- [مدل امنیتی](docs/fa/SECURITY.md)

## لینک‌های پروژه

- X: https://x.com/the_azzi
- GitHub: https://github.com/TheGreatAzizi
- Git شخصی: https://git.theazizi.ir/TheAzizi
- Telegram: https://t.me/luluch_code

## راه‌اندازی برای توسعه

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_app.py
```

## ساخت فایل اجرایی ویندوز

```powershell
pip install -r requirements-dev.txt
pyinstaller --noconsole --onefile --name AZSOS run_app.py
```

یا:

```powershell
.\scriptsuild_windows.ps1
```

## مثال‌های CLI

```powershell
python azsos.py verify sample-packages/first-aid-demo.azsos
python azsos.py install sample-packages/first-aid-demo.azsos
python azsos.py search help
python azsos.py catalog fetch "https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages"
```

ساخت registry JSON برای انتشار:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## مدل اعتماد

کشف بسته به معنی اعتماد نیست. AZSOS فقط وقتی یک بسته را نصب می‌کند که ساختار بسته، `hashes.json`، هش‌های SHA-256، امضای Ed25519 و در صورت وجود SHA-256 داخل registry را بررسی کرده باشد. کاربر می‌تواند بعد از بررسی fingerprint ناشر از یک مسیر قابل‌اعتماد، آن ناشر را فقط روی دستگاه خودش trusted کند.

## فرمت بسته

فایل‌های `.azsos` در واقع ZIP هستند و از فرمت `azsos.v1` استفاده می‌کنند:

```text
package.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
```

جزئیات بیشتر: [مشخصات فرمت](docs/fa/FORMAT.md)

## لایسنس

MIT
