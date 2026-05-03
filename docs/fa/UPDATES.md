# آپدیت نرم‌افزار

> زبان: **فارسی** | [English](../en/UPDATES.md)


## سورس پیش‌فرض آپدیت

```text
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE
```

## ساختار branch آپدیت

ساختار پیشنهادی:

```text
update.index.json
AZSOS-0.3.6-windows.exe
AZSOS-0.3.6-windows.zip
```

## update.index.json

نمونه:

```json
{
  "format": "azsos.update.v1",
  "version": "0.3.6",
  "files": [
    {
      "name": "AZSOS-0.3.6-windows.exe",
      "url": "AZSOS-0.3.6-windows.exe",
      "sha256": "..."
    }
  ]
}
```

## رفتار برنامه

برنامه فایل‌های آپدیت را اینجا دانلود می‌کند:

```text
~/AZSOS/updates/
```

برنامه installer دانلودشده را خودکار اجرا نمی‌کند. کاربر خودش تصمیم می‌گیرد چه زمانی آن را اجرا کند.
