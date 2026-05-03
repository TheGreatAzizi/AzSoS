# انتشار بسته‌ها

> زبان: **فارسی** | [English](../en/PUBLISHING_PACKAGES.md)


## ساختار پیشنهادی انتشار

یک branch با نام `IR-packages` بساز و از این ساختار استفاده کن:

```text
packages.index.json
packages/
  first-aid.azsos
  digital-safety.azsos
```

## ساخت بسته

کلید ناشر را یک بار بساز و کلید خصوصی را امن نگه دار:

```powershell
python azsos.py keygen --out-dir keys
```

ساخت بسته:

```powershell
python azsos.py pack `
  --content .\content `
  --id first-aid.fa.basic `
  --title "First Aid Basic" `
  --version 0.1.0 `
  --publisher-name "AZSOS Publisher" `
  --key keys\publisher_private.pem `
  --out packagesirst-aid.azsos
```

قبل از انتشار verify کن:

```powershell
python azsos.py verify packagesirst-aid.azsos
```

## ساخت registry

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-ir-packages
```

## انتشار

فایل registry و بسته‌ها را داخل branch `IR-packages` commit کن. کاربران از این لینک fetch می‌کنند:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

## نکات خوب برای بسته‌ها

- بسته‌ها را کوچک و متمرکز نگه دار.
- عنوان و نسخه واضح بنویس.
- منبع محتوا را داخل خود محتوا ذکر کن.
- محتوای پزشکی یا اضطراری را قبل از انتشار دقیق review کن.
- هرگز کلید خصوصی امضا را منتشر نکن.
