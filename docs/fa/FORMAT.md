# فرمت بسته AZSOS

> زبان: **فارسی** | [English](../en/FORMAT.md)


## خلاصه

فایل `.azsos` یک آرشیو ZIP با ساختار داخلی مشخص است. شناسه فرمت فعلی:

```text
azsos.v1
```

## فایل‌های الزامی

```text
manifest.json
hashes.json
signature.ed25519
content/
```

فایل اختیاری:

```text
search.sqlite
```

## ساختار نمونه

```text
first-aid.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
    index.html
    pages/
      burns.html
```

## manifest.json

مانیفست اطلاعات بسته را توضیح می‌دهد.

```json
{
  "format": "azsos.v1",
  "id": "first-aid.fa.demo",
  "title": "First Aid Demo",
  "version": "0.1.0",
  "language": "fa",
  "publisher": {
    "name": "AZSOS Demo Publisher",
    "public_key": "base64-ed25519-public-key"
  },
  "entry": "content/index.html"
}
```

## hashes.json

این فایل هش SHA-256 فایل‌های بسته را نگه می‌دارد.

```json
{
  "content/index.html": "sha256-...",
  "search.sqlite": "sha256-..."
}
```

## signature.ed25519

امضا ثابت می‌کند که manifest و لیست hashها با کلید ناشر امضا شده‌اند.

## قوانین ایمنی

- هیچ فایلی نباید خارج از فولدر نصب extract شود.
- JavaScript داخل محتوای بسته نباید اجرا شود.
- محتوای بسته نباید درخواست شبکه بزند.
- هر بسته تا قبل از verify شدن باید untrusted فرض شود.
