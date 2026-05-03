# انتشار بسته‌ها روی GitHub برای AZSOS

English version: [GITHUB_PUBLISHING_EN.md](GITHUB_PUBLISHING_EN.md)

منبع پیش‌فرض برنامه این branch است:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

برای اینکه کاربرها داخل برنامه روی **Fetch** بزنند و بسته‌ها را ببینند، دو روش داری.

## روش پیشنهادی: packages.index.json

این روش سریع‌تر، قابل‌اعتمادتر و بدون مشکل rate limit است.

1. فایل‌های `.azsos` را در یک فولدر، مثلاً `packages/` بگذار.
2. رجیستری بساز:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

3. این فایل‌ها را روی branch `IR-packages` آپلود کن:

```text
packages.index.json
packages/first-aid.azsos
packages/digital-safety.azsos
```

برنامه اول دنبال `packages.index.json` می‌گردد و اگر آن را پیدا کند، بدون GitHub API بسته‌ها را می‌خواند.

## روش ساده: فقط فایل .azsos

می‌توانی فایل‌های `.azsos` را مستقیم در branch بگذاری. AZSOS تلاش می‌کند صفحه tree گیت‌هاب را اسکن کند و لینک‌ها را پیدا کند.

```text
first-aid.azsos
digital-safety.azsos
```

این روش معمولاً کار می‌کند، اما رجیستری بهتر است چون metadata، size، SHA-256، عنوان و fingerprint را هم می‌دهد.

## اگر باز هم GitHub rate limit دیدی

نسخه 0.3.3 اول از مسیرهای non-API استفاده می‌کند؛ اما برای GitHub Releases هنوز ممکن است API لازم شود. برای افزایش محدودیت، قبل از اجرای برنامه یکی از این environment variableها را ست کن:

```powershell
$env:AZSOS_GITHUB_TOKEN="ghp_xxx"
python run_app.py
```

یا:

```powershell
$env:GITHUB_TOKEN="ghp_xxx"
python run_app.py
```

توکن لازم نیست دسترسی write داشته باشد؛ read-only برای repo عمومی کافی است.
