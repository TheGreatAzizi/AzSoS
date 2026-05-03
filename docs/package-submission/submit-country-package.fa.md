# ارسال پکیج کشوری برای AZSOS

> Language: [English](submit-country-package.en.md) | [فارسی](submit-country-package.fa.md) | [العربية](submit-country-package.ar.md) | [Türkçe](submit-country-package.tr.md)

این راهنما برای کسانی است که می‌خواهند برای کشور یا منطقه خودشان یک فایل `.azsos` بسازند و با Pull Request ارسال کنند تا بعد از بررسی، به کاتالوگ عمومی AZSOS اضافه شود.

## ۱. پکیج کشوری چیست؟

پکیج کشوری یک فایل امضاشده `.azsos` است که اطلاعات آفلاین، قابل جستجو و کاربردی برای مردم یک کشور یا منطقه را داخل خودش دارد. کاربر می‌تواند این فایل را قبل از قطعی اینترنت دانلود کند، با فلش منتقل کند، روی شبکه محلی پخش کند، یا از داخل کاتالوگ AZSOS نصب کند.

نمونه‌های خوب:

- شماره‌های اضطراری و تماس‌های عمومی
- راهنمای کمک‌های اولیه پایه
- چک‌لیست آماده‌باش خانواده
- راهنمای دوام کسب‌وکارهای کوچک در قطعی اینترنت
- نکات پایه امنیت دیجیتال
- نقشه یا فهرست منابع محلی، فقط وقتی مجوز بازنشر داده‌ها اجازه می‌دهد

این موارد را قرار ندهید:

- اطلاعات شخصی خصوصی
- کلید خصوصی یا signing key
- کتاب، مقاله یا محتوای پولی/کپی‌رایتی بدون اجازه
- توصیه پزشکی بدون منبع و هشدار مناسب
- محتوایی که کاربر را بی‌دلیل در معرض خطر قرار دهد

## ۲. ریپوی مقصد

Pull Request را برای ریپو/برنچ محتوایی AZSOS باز کنید:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

اگر بعداً maintainer برای کشورها branch جدا ساخت، طبق آخرین دستورالعمل همان ریپو عمل کنید.

## ۳. ساختار فولدر پیشنهادی

برای نظم بهتر، پکیج‌ها را داخل فولدر کد کشور بگذارید:

```text
packages/
  IR/
    first-aid-basic-fa.azsos
    digital-safety-basic-fa.azsos
  TR/
    emergency-contacts-tr.azsos
  IQ/
    first-aid-basic-ar.azsos
```

در صورت امکان از کدهای رایج کشور استفاده کنید؛ مثلاً `IR`، `TR`، `IQ`، `AF`، `DE`، `FR`، `US`.

## ۴. ساخت فولدر محتوا

اول محتوا را با Markdown یا HTML آماده کنید:

```text
my-country-pack/
  index.html
  pages/
    emergency-numbers.html
    first-aid.html
    family-checklist.html
  assets/
    icon.webp
```

محتوا باید کم‌حجم، خوانا و منبع‌دار باشد. صفحه اول بهتر است توضیح دهد پکیج شامل چیست، ناشر کیست، و آخرین بازبینی چه زمانی بوده است.

## ۵. ساخت کلید ناشر

این دستور را فقط روی سیستم خودتان اجرا کنید. کلید خصوصی را هیچ‌وقت commit نکنید.

```powershell
python azsos.py keygen --out-dir keys
```

کلید خصوصی برای امضای پکیج است. fingerprint کلید عمومی به کاربر کمک می‌کند ناشر را بررسی کند.

## ۶. ساخت فایل `.azsos`

مثال:

```powershell
python azsos.py pack `
  --content .\my-country-pack `
  --id ir.first-aid-basic.fa `
  --title "کمک‌های اولیه پایه - ایران" `
  --version 1.0.0 `
  --publisher-name "نام شما یا تیم شما" `
  --key .\keys\publisher_private.pem `
  --out .\packages\IRirst-aid-basic-fa.azsos
```

فرمت پیشنهادی برای package id:

```text
<country-code>.<topic>.<language>
```

مثال‌ها:

```text
ir.first-aid-basic.fa
tr.emergency-contacts.tr
iq.family-preparedness.ar
```

## ۷. تست قبل از ارسال

```powershell
python azsos.py verify .\packages\IRirst-aid-basic-fa.azsos
```

بعد پکیج را نصب و تست کنید:

```powershell
python azsos.py install .\packages\IRirst-aid-basic-fa.azsos
python azsos.py search کمک
```

داخل برنامه دسکتاپ هم چک کنید:

- عنوان پکیج درست است
- محتوا بدون اینترنت باز می‌شود
- جستجو نتیجه مفید می‌دهد
- اطلاعات ضروری وابسته به لینک آنلاین نیست
- وضعیت پکیج valid است

## ۸. ساخت یا به‌روزرسانی registry

معمولاً maintainer بعد از merge کردن، registry را دوباره می‌سازد؛ ولی اگر خواسته شد، این دستور را اجرا کنید:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-community-packages
```

registry فقط برای پیدا کردن پکیج‌هاست. اعتماد اصلی از امضای خود پکیج می‌آید.

## ۹. ارسال Pull Request

PR شما بهتر است شامل این موارد باشد:

- فایل `.azsos`
- توضیح منابع و مجوز محتوا
- کشور و زبان پکیج
- fingerprint ناشر
- توضیح کوتاه تست‌ها

نمونه عنوان خوب برای PR:

```text
Add IR first-aid basic package (fa)
Add TR emergency contacts package (tr)
Add IQ family preparedness package (ar)
```

## ۱۰. قالب توضیح PR

این متن را داخل PR کپی کنید:

```markdown
## Package information

- Country:
- Language:
- Package title:
- Package id:
- Version:
- Publisher name:
- Publisher fingerprint:

## Content sources and licenses

- Source 1:
- Source 2:
- License/permission notes:

## Testing

- [ ] `python azsos.py verify <package>.azsos` passes
- [ ] The package installs in AZSOS Desktop
- [ ] Search works offline
- [ ] Essential pages open without internet
- [ ] No private keys are included
- [ ] No private personal data is included

## Notes for reviewer

Write anything the maintainer should know.
```

## ۱۱. مواردی که ممکن است باعث رد یا تأخیر شوند

- پکیج verify نشود
- منبع محتوا نامشخص باشد
- داده خصوصی یا ناامن داخل پکیج باشد
- حجم پکیج بی‌دلیل زیاد باشد
- ادعاهای گمراه‌کننده داشته باشد
- کلید خصوصی یا secret داخل PR باشد
- محتوای اصلی بدون اینترنت قابل استفاده نباشد

## ۱۲. نکات امنیتی مهم

- فایل `publisher_private.pem` را commit نکنید.
- secret، token یا فایل خصوصی منتشر نکنید.
- هر پکیج باید امضا شود.
- از private key خودتان بکاپ امن و آفلاین نگه دارید.
- اگر کلید لو رفت، دیگر از آن استفاده نکنید و به کاربران اطلاع دهید.

## ۱۳. روند merge برای maintainer

بعد از قبول شدن PR، maintainer می‌تواند:

1. پکیج را verify کند،
2. metadata را inspect کند،
3. فایل `packages.index.json` را دوباره بسازد،
4. branch کاتالوگ را push کند،
5. Fetch داخل AZSOS Desktop را تست کند.

بعد از آن کاربرها داخل برنامه به **Get content** می‌روند، **Fetch** می‌زنند و پکیج جدید را نصب می‌کنند.
