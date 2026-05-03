# انتشار آپدیت نرم‌افزار AZSOS

English version: [UPDATES_EN.md](UPDATES_EN.md)

از نسخه 0.3.3، داخل برنامه دکمه **Check updates** وجود دارد. این دکمه به‌صورت پیش‌فرض این آدرس را بررسی می‌کند:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

## روش پیشنهادی

روی branch `UPDATE` یک فایل `update.index.json` بگذارید و فایل‌های نصاب/آرشیو را داخل یک فولدر مثل `releases/` نگه دارید.

ساختار پیشنهادی:

```text
UPDATE branch:
  update.index.json
  releases/
    AZSOS-Desktop-v0.3.3.exe
    AZSOS-Desktop-v0.3.3.zip
```

نمونه `update.index.json`:

```json
{
  "format": "azsos.update.v1",
  "name": "AZSOS app updates",
  "updates": [
    {
      "name": "AZSOS-Desktop-v0.3.3.exe",
      "version": "0.3.3",
      "download_url": "./releases/AZSOS-Desktop-v0.3.3.exe",
      "sha256": "PUT_SHA256_HERE",
      "notes": "Windows desktop build"
    }
  ]
}
```

لینک‌های relative مثل `./releases/...` پشتیبانی می‌شوند. برنامه اول دنبال `update.index.json` می‌گردد. اگر نبود، خود branch را برای فایل‌های `.exe`، `.msi` و `.zip` اسکن می‌کند. GitHub Releases هم به‌عنوان fallback بررسی می‌شود، ولی Releaseهای GitHub branch-specific نیستند؛ برای کنترل دقیق‌تر، branch `UPDATE` + فایل `update.index.json` بهتر است.

## رفتار برنامه

AZSOS آپدیت را خودکار اجرا نمی‌کند. کاربر دکمه **Download selected** را می‌زند، فایل در مسیر زیر ذخیره می‌شود و بعد کاربر آن را دستی اجرا/باز می‌کند:

```text
~/AZSOS/updates/
```

این رفتار امن‌تر است و جلوی اجرای ناخواسته فایل‌های دانلودی را می‌گیرد.
