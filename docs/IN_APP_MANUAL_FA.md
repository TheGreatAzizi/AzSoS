# راهنمای کامل AZSOS

## شروع سریع

AZSOS برای این ساخته شده که محتوای ضروری را قبل از قطعی اینترنت بگیری، روی سیستم نگه داری، داخلش جستجو کنی، و در زمان قطعی با بقیه به‌صورت محلی به اشتراک بگذاری.

مسیر سریع استفاده:

1. وارد تب Get content شو.
2. روی Fetch selected بزن تا برنامه از منبع پیش‌فرض دنبال فایل‌های .azsos بگردد.
3. یک یا چند بسته را انتخاب کن و Install selected را بزن.
4. برو به تب Installed، بسته نصب‌شده را انتخاب کن.
5. با Open package محتوا را باز کن یا با Search all / Search selected داخل بسته‌ها جستجو کن.
6. برای پخش آفلاین، برو به تب Share و Start را بزن.

اگر اینترنت نداری ولی یک فایل .azsos داری، از تب Installed دکمه Import .azsos را بزن.

## AZSOS چیست؟

AZSOS یک ابزار آفلاین‌اول برای بسته‌های محتوای ضروری است. هر بسته یک فایل با پسوند .azsos است که می‌تواند شامل راهنما، HTML، Markdown، عکس‌های سبک، ایندکس جستجو، manifest، hash و امضای دیجیتال باشد.

هدف پروژه:

- کاربر قبل از بحران محتوا را دانلود کند.
- در زمان قطعی اینترنت بتواند محتوا را بدون اینترنت بخواند.
- بتواند داخل بسته‌ها جستجو کند.
- بتواند بسته‌ها را با Wi-Fi، hotspot، LAN، فلش، تلگرام، گیت، یا هر مسیر فایل دیگری منتقل کند.
- قبل از نصب، سالم بودن فایل و امضای ناشر بررسی شود.

AZSOS جایگزین پیام‌رسان یا VPN نیست؛ یک کش آفلاین قابل‌اعتماد برای اطلاعات ضروری است.

## فایل .azsos چیست؟

فایل .azsos از نظر فنی یک ZIP کنترل‌شده است، اما داخل آن ساختار و قوانین مشخصی وجود دارد.

ساختار معمول:

first-aid.azsos
  manifest.json
  hashes.json
  signature.ed25519
  search.sqlite
  content/
    index.html
    pages/
    assets/

فایل‌های مهم:

manifest.json
  اطلاعات بسته: عنوان، نسخه، زبان، ناشر، مسیر صفحه شروع، و فرمت.

hashes.json
  SHA-256 فایل‌های داخل بسته برای تشخیص دستکاری یا خرابی.

signature.ed25519
  امضای دیجیتال ناشر برای manifest و hashes.

search.sqlite
  ایندکس جستجوی آفلاین.

content/
  محتوای واقعی که کاربر می‌خواند.

برنامه هنگام نصب، مسیرهای خطرناک داخل ZIP را رد می‌کند تا بسته نتواند فایل‌های بیرون از library را overwrite کند.

## تب Installed

تب Installed برای مدیریت بسته‌هایی است که روی سیستم نصب شده‌اند.

دکمه‌ها:

Import .azsos
  یک فایل .azsos از روی کامپیوتر انتخاب می‌کنی. برنامه آن را verify و نصب می‌کند.

Verify file
  فقط بررسی می‌کند فایل سالم و معتبر است یا نه، بدون اینکه آن را نصب کند.

Open package
  صفحه شروع بسته انتخاب‌شده را در مرورگر پیش‌فرض باز می‌کند.

Export selected
  فایل .azsos بسته نصب‌شده را دوباره خروجی می‌گیرد تا بتوانی آن را برای دیگران بفرستی.

Delete package
  بسته نصب‌شده را از library حذف می‌کند. فایل اصلی بیرون از library حذف نمی‌شود.

Trust publisher
  fingerprint ناشر بسته را روی همین دستگاه به لیست trusted اضافه می‌کند. این یعنی بسته‌های بعدی با همان fingerprint به‌عنوان ناشر قابل‌اعتماد نشان داده می‌شوند.

Refresh
  لیست بسته‌های نصب‌شده را دوباره می‌خواند.

Open library folder
  فولدر نصب بسته‌ها را باز می‌کند.

## جستجوی آفلاین

در تب Installed می‌توانی داخل بسته‌ها جستجو کنی.

Search selected
  فقط داخل بسته انتخاب‌شده جستجو می‌کند.

Search all
  داخل همه بسته‌های نصب‌شده جستجو می‌کند.

Open result
  نتیجه انتخاب‌شده را باز می‌کند.

نکته‌های جستجو برای فارسی:

- بهتر است کلمات ساده‌تر را جستجو کنی؛ مثلاً به‌جای «آبرسانی اضطراری» اول «آب» را امتحان کن.
- اگر با نیم‌فاصله نتیجه نگرفتی، با فاصله معمولی هم تست کن.
- بسته‌ها هنگام ساخت، متن‌ها را وارد search.sqlite می‌کنند؛ اگر یک بسته search.sqlite نداشته باشد، جستجو ممکن است نتیجه کامل ندهد.

## تب Get content

تب Get content برای گرفتن بسته از اینترنت، گیت‌هاب، ریلیزها، لینک مستقیم، فولدر محلی، یا registry است.

منبع پیش‌فرض برنامه:

https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

دکمه‌ها:

Fetch selected
  فقط source فعلی را بررسی می‌کند.

Fetch all
  همه sourceهای ذخیره‌شده را بررسی می‌کند.

Open source
  صفحه source فعلی را در مرورگر باز می‌کند.

Reset default
  source پیش‌فرض AZSOS IR packages را برمی‌گرداند.

Save current
  تغییرات name و URL source فعلی را ذخیره می‌کند.

Add as new
  source فعلی را به‌عنوان یک منبع جدید اضافه می‌کند.

Remove
  source انتخاب‌شده را حذف می‌کند.

Install selected
  فایل‌های انتخاب‌شده در Remote packages را دانلود، verify، و نصب می‌کند.

Inspect selected
  قبل از نصب، فایل ریموت را دانلود موقت می‌کند و اطلاعات manifest، ناشر، fingerprint و SHA-256 را نشان می‌دهد.

Copy download URL
  لینک دانلود بسته انتخاب‌شده را کپی می‌کند.

## Sourceها و Registry

AZSOS چند نوع source را می‌فهمد:

1. GitHub branch/tree
   مثل:
   https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

2. GitHub Releases
   اگر در release asset فایل .azsos بگذاری، برنامه می‌تواند آن را پیدا کند.

3. لینک مستقیم .azsos
   مثل:
   https://example.com/packs/first-aid.azsos

4. فولدر محلی
   مثلاً:
   C:\AZSOS-Packs

5. فایل packages.index.json
   این بهترین روش انتشار منظم است، چون برنامه لازم نیست کل صفحه GitHub را بگردد.

نمونه ساده packages.index.json:

{
  "format": "azsos.registry.v1",
  "source_name": "azsos-ir-packages",
  "packages": [
    {
      "name": "first-aid.azsos",
      "title": "کمک‌های اولیه",
      "version": "0.1.0",
      "download_url": "https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages/first-aid.azsos",
      "sha256": "..."
    }
  ]
}

پیشنهاد: در branch محتوا یک packages.index.json بگذار تا Fetch سریع‌تر، پایدارتر، و بدون rate limit انجام شود.

## دریافت محتوا در زمان عادی و قطعی

در زمان عادی:

- بسته‌ها را روی GitHub branch یا Release قرار بده.
- کاربر از Get content آن‌ها را Fetch و Install می‌کند.
- بسته‌ها روی کامپیوتر کاربر باقی می‌مانند و بعداً بدون اینترنت قابل استفاده‌اند.

در زمان قطعی یا اینترنت ضعیف:

- اگر یک نفر قبلاً بسته‌ها را نصب کرده باشد، از تب Share می‌تواند آن‌ها را روی شبکه محلی پخش کند.
- دیگران به همان Wi-Fi یا hotspot وصل می‌شوند و لینک Local Share را باز می‌کنند.
- اگر شبکه محلی هم در دسترس نیست، Export selected بزن و فایل .azsos را با فلش، هارد، کابل، بلوتوث، یا هر مسیر انتقال فایل دیگری بده.

اصل طراحی AZSOS این است: یک بار محتوا را بگیر، بارها آفلاین استفاده و پخش کن.

## تب Share

تب Share برای پخش بسته‌های نصب‌شده روی شبکه محلی است.

Start
  یک HTTP server کوچک روی همین سیستم اجرا می‌کند.

Stop
  سرور محلی را خاموش می‌کند.

Copy URL
  لینک Share را کپی می‌کند.

QR
  از لینک Share یک QR می‌سازد تا موبایل‌ها راحت‌تر وارد شوند.

نحوه استفاده:

1. لپ‌تاپ یا کامپیوتر را به Wi-Fi یا hotspot وصل کن.
2. در AZSOS دکمه Start را بزن.
3. لینک نشان‌داده‌شده را برای بقیه بفرست یا QR را نشان بده.
4. دستگاه‌های دیگر باید روی همان شبکه باشند.
5. آن‌ها لینک را در مرورگر باز می‌کنند و فایل‌های .azsos را دانلود می‌کنند.

نکته امنیتی: وقتی کار تمام شد Stop را بزن، مخصوصاً اگر روی شبکه عمومی هستی.

## ساخت بسته .azsos با CLI

برای ناشرها و سازنده‌های محتوا، ابزار CLI وجود دارد.

ساخت کلید ناشر:

python azsos.py keygen --out-dir keys

ساخت بسته:

python azsos.py pack ^
  --content examples/first-aid/content ^
  --id first-aid.fa ^
  --title "کمک‌های اولیه" ^
  --version 0.1.0 ^
  --publisher-name "AZSOS Publisher" ^
  --key keys/publisher_private.pem ^
  --out dist/first-aid.azsos

بررسی بسته:

python azsos.py verify dist/first-aid.azsos

نصب از CLI:

python azsos.py install dist/first-aid.azsos

جستجو از CLI:

python azsos.py search آب

اجرای share server از CLI:

python azsos.py serve

کلید خصوصی ناشر را هیچ‌وقت داخل repo عمومی نگذار. فقط public key یا fingerprint را منتشر کن.

## ساخت packages.index.json

برای اینکه کاربران راحت‌تر محتوا بگیرند، کنار بسته‌ها یک registry بساز.

ساختار پیشنهادی branch IR-packages:

IR-packages/
  packages.index.json
  packages/
    first-aid.azsos
    digital-safety.azsos
    offline-business-kit.azsos

ساخت registry با CLI:

python azsos.py registry build ^
  --packages-dir ./packages ^
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages ^
  --out packages.index.json ^
  --source-name azsos-ir-packages

بعد این فایل‌ها را push کن روی branch:

https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

مزیت registry:

- Fetch سریع‌تر می‌شود.
- کمتر به GitHub API نیاز دارد.
- SHA-256 فایل‌ها از قبل داخل index است.
- title/version/publisher بهتر نمایش داده می‌شود.

## آپدیت خود نرم‌افزار

بالای برنامه دکمه Check updates وجود دارد.

منبع پیش‌فرض آپدیت:

https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE

برنامه در branch UPDATE دنبال این‌ها می‌گردد:

- update.index.json
- فایل .exe
- فایل .msi
- فایل .zip
- GitHub Releases به‌عنوان fallback

رفتار برنامه:

1. لیست فایل‌های آپدیت را پیدا می‌کند.
2. کاربر یک مورد را انتخاب می‌کند.
3. فایل در مسیر زیر دانلود می‌شود:

~/AZSOS/updates/

4. برنامه فایل را خودکار اجرا نمی‌کند؛ کاربر باید دستی installer یا zip را باز کند.

این کار امن‌تر است، چون نصب خودکار برنامه ناشناس انجام نمی‌شود.

## امنیت و اعتماد

AZSOS چند لایه بررسی دارد:

1. بررسی ساختار ZIP
   مسیرهای خطرناک مثل ../evil.txt رد می‌شوند.

2. بررسی hash
   هر فایل داخل بسته با hashes.json چک می‌شود.

3. بررسی امضای Ed25519
   manifest و hashes باید با امضای ناشر بخوانند.

4. fingerprint ناشر
   ناشر با fingerprint شناخته می‌شود، نه فقط اسم.

5. Trust publisher
   اگر fingerprint را از یک مسیر قابل‌اعتماد تأیید کردی، می‌توانی آن ناشر را trusted کنی.

معنی وضعیت‌ها:

Valid package
  فایل سالم است و امضا درست است.

Unknown publisher
  فایل سالم است، اما ناشر هنوز روی دستگاه تو trusted نشده.

Trusted publisher
  fingerprint این ناشر قبلاً روی همین دستگاه trusted شده.

Invalid package
  فایل خراب، ناقص، دستکاری‌شده، یا با ساختار خطرناک است.

قاعده مهم: فقط به ناشری trust بده که fingerprint آن را از مسیر قابل اعتماد گرفته‌ای؛ مثلاً سایت رسمی، کانال رسمی، یا حضوری.

## خطاهای رایج

No .azsos packages found
  یعنی در source انتخاب‌شده فایل .azsos پیدا نشده. مطمئن شو branch درست است، فایل‌ها واقعاً push شده‌اند، یا packages.index.json درست است.

HTTP Error 403: rate limit exceeded
  گیت‌هاب درخواست زیاد یا بدون توکن را محدود کرده. راه‌حل بهتر: packages.index.json بساز. راه‌حل موقت: توکن بگذار.

در PowerShell:

$env:AZSOS_GITHUB_TOKEN="ghp_xxx"
python run_app.py

Not found / 404
  لینک branch، repo، مسیر فایل، یا نام فایل اشتباه است.

Invalid package
  فایل .azsos ناقص یا دستکاری‌شده است، یا با نسخه فرمت AZSOS سازگار نیست.

Missing entry
  manifest به صفحه شروعی اشاره کرده که داخل بسته وجود ندارد.

Search gives no results
  بسته شاید search.sqlite ندارد، یا باید عبارت ساده‌تر جستجو شود.

Local Share باز نمی‌شود
  دستگاه‌ها باید روی یک شبکه باشند. فایروال ویندوز ممکن است نیاز به Allow داشته باشد.

## مسیرهای مهم روی سیستم

AZSOS داده‌های کاربر را معمولاً زیر فولدر home ذخیره می‌کند:

Library بسته‌ها:
~/AZSOS/library/

تنظیمات و sourceها:
~/AZSOS/config.json

دانلود آپدیت‌ها:
~/AZSOS/updates/

کش دانلودهای موقت ممکن است در temp سیستم قرار بگیرد.

برای باز کردن library از داخل برنامه:

Installed -> Open library folder

اگر می‌خواهی کل نصب محلی را پاک کنی، برنامه را ببند و فولدر ~/AZSOS را حذف کن. اگر بسته‌های مهم داری، قبلش Export selected بگیر.

## راهنمای ناشر محتوا

برای اینکه بسته‌های خوب و قابل‌اعتماد بسازی:

- محتوا را کوتاه، دقیق و آفلاین‌خوان نگه دار.
- عکس‌ها را کم‌حجم کن.
- از منابع معتبر استفاده کن و منبع را داخل محتوا بنویس.
- برای محتوای پزشکی، هشدار و تاریخ بازبینی بگذار.
- نسخه‌گذاری واضح داشته باش: 0.1.0، 0.2.0، 1.0.0.
- package id را ثابت نگه دار؛ مثلاً first-aid.fa.basic.
- کلید خصوصی ناشر را امن نگه دار.
- fingerprint عمومی را در کانال رسمی منتشر کن.
- packages.index.json بساز.
- قبل از انتشار، بسته را با verify و install تست کن.

چک‌لیست قبل از انتشار:

[ ] فایل .azsos ساخته شد
[ ] verify موفق بود
[ ] install موفق بود
[ ] search کار می‌کند
[ ] Open package صفحه درست را باز می‌کند
[ ] محتوا منبع و تاریخ دارد
[ ] registry ساخته شد
[ ] لینک raw در registry درست است

## دستورات CLI پرکاربرد

نمایش راهنما:

python azsos.py --help

ساخت کلید:

python azsos.py keygen --out-dir keys

ساخت بسته:

python azsos.py pack --content ./content --id my.pack.fa --title "عنوان" --version 0.1.0 --publisher-name "ناشر" --key keys/publisher_private.pem --out my-pack.azsos

بررسی بسته:

python azsos.py verify my-pack.azsos

نصب بسته:

python azsos.py install my-pack.azsos

حذف بسته نصب‌شده:

python azsos.py delete <package-id-or-installed-path>

جستجو:

python azsos.py search کمک

گرفتن catalog:

python azsos.py catalog fetch

inspect یک بسته ریموت:

python azsos.py catalog inspect <url-or-index>

نصب از catalog:

python azsos.py catalog install <url-or-index>

ساخت registry:

python azsos.py registry build --packages-dir ./packages --base-url <raw-base-url> --out packages.index.json

## لینک‌ها و ارتباطات پروژه

Repository اصلی:
https://github.com/TheGreatAzizi/AzSoS

Branch بسته‌های محتوا:
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages

Branch آپدیت نرم‌افزار:
https://github.com/TheGreatAzizi/AzSoS/tree/UPDATE

X / Twitter:
https://x.com/the_azzi

GitHub profile:
https://github.com/TheGreatAzizi

Self-hosted Git:
https://git.theazizi.ir/TheAzizi

Telegram:
https://t.me/luluch_code
