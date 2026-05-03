# کشف محتوا

> زبان: **فارسی** | [English](../en/CONTENT_DISCOVERY.md)


## هدف

کشف محتوا به AZSOS اجازه می‌دهد بدون نیاز به سرور مرکزی، بسته‌های `.azsos` را پیدا کند. سورس می‌تواند GitHub branch، صفحه release، لینک مستقیم فایل، فولدر محلی یا فایل registry JSON باشد.

## سورس پیش‌فرض

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

AZSOS ابتدا روش‌های سبک‌تر را امتحان می‌کند:

1. پیدا کردن `packages.index.json`.
2. خواندن صفحه GitHub tree وقتی ممکن باشد.
3. استفاده از GitHub API فقط به عنوان fallback.
4. بررسی GitHub Releases به صورت best-effort.

## انواع سورس

### GitHub tree

مثال:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

ساختار پیشنهادی:

```text
packages.index.json
packages/
  first-aid.azsos
  digital-safety.azsos
```

### لینک مستقیم `.azsos`

هر لینکی که به فایل `.azsos` برسد می‌تواند بعد از verify نصب شود.

### Registry JSON

فایل `packages.index.json` متادیتا و لینک دانلود بسته‌ها را نگه می‌دارد. این قابل‌اعتمادترین روش برای کشف محتواست.

### فولدر محلی

سورس فولدر محلی برای اسکن فایل‌های `.azsos` از دیسک، فلش یا آرشیو extract شده کاربرد دارد.

## کشف به معنی اعتماد نیست

بسته‌ای که در catalog پیدا می‌شود به صورت خودکار trusted نیست. AZSOS قبل از نصب، فایل را verify می‌کند.
