# انتشار بسته‌های AZSOS

English version: [PUBLISHING_PACKAGES_EN.md](PUBLISHING_PACKAGES_EN.md)

## روش سریع

1. فایل‌های `.azsos` را بسازید.
2. آن‌ها را روی branch زیر آپلود کنید:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

3. کاربران در برنامه روی **Fetch selected** می‌زنند و پکیج‌ها را می‌بینند.

## روش پیشنهادی با registry

اگر می‌خواهید عنوان، نسخه، ناشر، SHA-256 و اطلاعات دقیق‌تر نمایش داده شود، یک registry بسازید:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

بعد فایل `packages.index.json` را هم کنار بسته‌ها آپلود کنید.

## ساخت بسته

```powershell
python azsos.py keygen --out-dir keys

python azsos.py pack `
  --content .\my-content `
  --id first-aid.fa.basic `
  --title "کمک‌های اولیه پایه" `
  --version 0.1.0 `
  --publisher-name "AZSOS Publisher" `
  --key .\keys\publisher_private.pem `
  --out .\packages\first-aid-basic-fa.azsos
```

کلید خصوصی را هیچ‌وقت داخل گیت آپلود نکنید.
