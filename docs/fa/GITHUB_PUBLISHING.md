# انتشار روی GitHub

> زبان: **فارسی** | [English](../en/GITHUB_PUBLISHING.md)


## Branchها

AZSOS به صورت پیش‌فرض از دو branch عمومی استفاده می‌کند:

```text
IR-packages  کاتالوگ بسته‌ها و فایل‌های .azsos
UPDATE       فایل‌های آپدیت نرم‌افزار
```

## Branch بسته‌ها

branch بسته‌ها بهتر است این ساختار را داشته باشد:

```text
packages.index.json
packages/
  first-aid.azsos
```

AZSOS از این لینک fetch می‌کند:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

## چرا registry JSON مهم است؟

registry باعث می‌شود برنامه کمتر به GitHub API وابسته شود و به rate limit نخورد. برنامه اول سعی می‌کند `packages.index.json` را بخواند و فقط بعداً سراغ روش‌های سنگین‌تر می‌رود.

## GitHub Releases

GitHub Releases می‌تواند به عنوان مسیر fallback استفاده شود، مخصوصاً برای مجموعه‌های پایدار بسته‌ها. اما برای سورس پیش‌فرض، discovery از registry داخل branch پیشنهاد می‌شود.

## کلید خصوصی

کلید خصوصی امضا را commit نکن. کلیدها را از ریپو و release assetها دور نگه دار.
