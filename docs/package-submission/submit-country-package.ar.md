# إرسال حزمة دولة إلى AZSOS

> Language: [English](submit-country-package.en.md) | [فارسی](submit-country-package.fa.md) | [العربية](submit-country-package.ar.md) | [Türkçe](submit-country-package.tr.md)

هذا الدليل مخصص لمن يريد إنشاء ملف `.azsos` لبلده أو منطقته، ثم إرساله عبر Pull Request حتى يراجعه المشرف ويضيفه إلى فهرس AZSOS العام.

## 1. ما هي حزمة الدولة؟

حزمة الدولة هي ملف `.azsos` موقّع يحتوي على معلومات مفيدة، قابلة للبحث، وتعمل بدون إنترنت. يمكن للمستخدم تنزيلها قبل الانقطاع، نسخها عبر USB، مشاركتها عبر شبكة محلية أو نقطة اتصال، أو تثبيتها من كتالوج AZSOS.

أمثلة مناسبة:

- أرقام الطوارئ والجهات العامة
- إرشادات إسعاف أولي أساسية
- قوائم استعداد للعائلة
- إرشادات لاستمرار عمل المتاجر الصغيرة أثناء انقطاع الإنترنت
- أساسيات السلامة الرقمية
- خرائط أو قوائم موارد محلية عندما يسمح الترخيص بإعادة التوزيع

تجنب إضافة:

- بيانات شخصية خاصة
- مفاتيح خاصة أو مفاتيح توقيع
- كتب أو مقالات أو محتوى مدفوع/محمي بدون إذن
- نصائح طبية بدون مصادر واضحة وتنبيه مناسب
- محتوى قد يعرّض المستخدمين لخطر غير ضروري

## 2. المستودع المستهدف

افتح Pull Request على فرع الحزم المستخدم في AZSOS:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

إذا أنشأ المشرف فرعاً خاصاً بدول معينة لاحقاً، اتبع التعليمات الأحدث في المستودع.

## 3. تنظيم الملفات المقترح

استخدم مجلداً برمز الدولة:

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

استخدم رموز الدول الشائعة مثل `IR`، `TR`، `IQ`، `AF`، `DE`، `FR`، `US`.

## 4. إنشاء مجلد المحتوى

جهّز المحتوى أولاً كملفات Markdown أو HTML:

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

اجعل المحتوى صغيراً، واضحاً، ومسنوداً بمصادر. يجب أن تشرح الصفحة الأولى ما تحتويه الحزمة، من الناشر، وتاريخ آخر مراجعة.

## 5. إنشاء مفتاح الناشر

نفذ الأمر محلياً فقط. لا ترفع المفتاح الخاص إلى GitHub.

```powershell
python azsos.py keygen --out-dir keys
```

يُستخدم المفتاح الخاص لتوقيع الحزم. تساعد بصمة المفتاح العام المستخدمين على التحقق من الناشر.

## 6. بناء ملف `.azsos`

مثال:

```powershell
python azsos.py pack `
  --content .\my-country-pack `
  --id iq.family-preparedness.ar `
  --title "Family Preparedness - Iraq" `
  --version 1.0.0 `
  --publisher-name "Your Team or Name" `
  --key .\keys\publisher_private.pem `
  --out .\packages\IQamily-preparedness-ar.azsos
```

صيغة package id المقترحة:

```text
<country-code>.<topic>.<language>
```

أمثلة:

```text
ir.first-aid-basic.fa
tr.emergency-contacts.tr
iq.family-preparedness.ar
```

## 7. التحقق قبل الإرسال

```powershell
python azsos.py verify .\packages\IQamily-preparedness-ar.azsos
```

ثم ثبّت الحزمة واختبرها محلياً:

```powershell
python azsos.py install .\packages\IQamily-preparedness-ar.azsos
python azsos.py search emergency
```

افتحها في تطبيق سطح المكتب وتأكد من:

- صحة العنوان
- فتح المحتوى بدون إنترنت
- عمل البحث بشكل مفيد
- عدم اعتماد الصفحات الأساسية على روابط خارجية
- ظهور حالة الحزمة كصالحة

## 8. بناء أو تحديث registry

قد يعيد المشرف بناء registry بعد الدمج. إذا طُلب منك ذلك:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-community-packages
```

الـ registry يساعد على اكتشاف الحزم فقط. الثقة تأتي من توقيع الحزمة نفسها.

## 9. فتح Pull Request

يجب أن يتضمن PR:

- ملف `.azsos`
- ملاحظات المصادر والتراخيص
- الدولة واللغة
- بصمة الناشر
- ملاحظة قصيرة عن الاختبار

عناوين PR جيدة:

```text
Add IQ family preparedness package (ar)
Add TR emergency contacts package (tr)
Add IR first-aid basic package (fa)
```

## 10. قالب وصف PR

انسخ هذا في وصف PR:

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

## 11. أسباب محتملة للرفض أو التأخير

- فشل التحقق من الحزمة
- مصادر غير واضحة
- محتوى خاص أو غير آمن
- حجم كبير بدون سبب واضح
- ادعاءات مضللة
- وجود مفتاح خاص أو سر داخل PR
- اعتماد المحتوى الأساسي على الإنترنت

## 12. تذكيرات أمنية

- لا ترفع `publisher_private.pem`.
- لا تنشر أسراراً أو tokens أو ملفات خاصة.
- وقّع كل حزمة.
- احتفظ بنسخة آمنة وغير متصلة من المفتاح الخاص.
- إذا تسرّب المفتاح، توقف عن استخدامه وأخبر المستخدمين.
