# چک‌لیست انتشار

> زبان: **فارسی** | [English](../en/RELEASE.md)


## قبل از انتشار

- مقدار `azsos_core.__version__` را به‌روزرسانی کن.
- نسخه `pyproject.toml` را به‌روزرسانی کن.
- `CHANGELOG.md` را آپدیت کن.
- تست‌ها را اجرا کن.
- بسته نمونه را verify کن.
- فایل اجرایی ویندوز را بساز.
- فایل‌های انتشار را در branch `UPDATE` یا GitHub Releases آپلود کن.

## دستورات تست

```powershell
pytest
python azsos.py verify sample-packages/first-aid-demo.azsos
python run_app.py
```

## بعد از انتشار

- بررسی کن **Check updates** نسخه جدید را پیدا کند.
- بررسی کن **Fetch selected** بسته‌های `IR-packages` را پیدا کند.
- اگر کاربران ممکن است rollback بخواهند، فایل‌های نسخه قبلی را نگه دار.
