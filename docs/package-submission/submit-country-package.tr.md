# AZSOS'a ülke paketi gönderme

> Language: [English](submit-country-package.en.md) | [فارسی](submit-country-package.fa.md) | [العربية](submit-country-package.ar.md) | [Türkçe](submit-country-package.tr.md)

Bu rehber, kendi ülkesi veya bölgesi için bir `.azsos` paketi hazırlayıp Pull Request ile göndermek isteyen katkıcılar içindir. Paket, incelendikten sonra AZSOS genel kataloğuna eklenebilir.

## 1. Ülke paketi nedir?

Ülke paketi; internet olmadan çalışan, aranabilir ve imzalı bir `.azsos` dosyasıdır. Kullanıcı paketi kesinti olmadan önce indirebilir, USB ile kopyalayabilir, yerel ağ/hotspot üzerinden paylaşabilir veya AZSOS kataloğundan kurabilir.

Uygun örnekler:

- acil telefon numaraları ve kamu iletişim bilgileri
- temel ilk yardım sayfaları
- aile hazırlık kontrol listeleri
- küçük işletmeler için internet kesintisi hazırlığı
- temel dijital güvenlik notları
- yeniden dağıtım izni olan harita veya yerel kaynak listeleri

Eklemeyin:

- özel kişisel veriler
- özel anahtarlar veya imzalama anahtarları
- izinsiz telifli veya ücretli içerikler
- kaynaksız tıbbi tavsiyeler
- kullanıcıları gereksiz riske sokabilecek içerikler

## 2. Hedef repository

Pull Request'i AZSOS paket branch'ine açın:

```text
https://github.com/TheGreatAzizi/AzSoS/tree/IR-packages
```

Maintainer daha sonra ülkeye özel branch oluşturursa, repository'deki güncel talimatları takip edin.

## 3. Önerilen klasör yapısı

Paketleri ülke kodu klasöründe tutun:

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

Mümkünse `IR`, `TR`, `IQ`, `AF`, `DE`, `FR`, `US` gibi yaygın ülke kodlarını kullanın.

## 4. İçerik klasörünü hazırlama

İçeriği önce Markdown veya HTML olarak hazırlayın:

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

İçerik küçük, okunabilir ve kaynaklı olmalıdır. İlk sayfa paketin ne içerdiğini, yayıncının kim olduğunu ve son gözden geçirme tarihini açıklamalıdır.

## 5. Yayıncı anahtarı oluşturma

Bu komutu kendi bilgisayarınızda çalıştırın. Özel anahtarı asla commit etmeyin.

```powershell
python azsos.py keygen --out-dir keys
```

Özel anahtar paketleri imzalar. Public fingerprint, kullanıcıların yayıncıyı kontrol etmesine yardımcı olur.

## 6. `.azsos` paketini oluşturma

Örnek:

```powershell
python azsos.py pack `
  --content .\my-country-pack `
  --id tr.emergency-contacts.tr `
  --title "Emergency Contacts - Turkey" `
  --version 1.0.0 `
  --publisher-name "Your Team or Name" `
  --key .\keys\publisher_private.pem `
  --out .\packages\TR\emergency-contacts-tr.azsos
```

Önerilen package id formatı:

```text
<country-code>.<topic>.<language>
```

Örnekler:

```text
ir.first-aid-basic.fa
tr.emergency-contacts.tr
iq.family-preparedness.ar
```

## 7. Göndermeden önce doğrulama

```powershell
python azsos.py verify .\packages\TR\emergency-contacts-tr.azsos
```

Paketi yerel olarak kurup test edin:

```powershell
python azsos.py install .\packages\TR\emergency-contacts-tr.azsos
python azsos.py search emergency
```

Masaüstü uygulamasında kontrol edin:

- paket başlığı doğru
- içerik internet olmadan açılıyor
- arama yararlı sonuç veriyor
- temel bilgiler dış bağlantıya bağımlı değil
- paket durumu valid görünüyor

## 8. Registry oluşturma veya güncelleme

Maintainer genellikle merge sonrasında registry'yi tekrar oluşturur. İstenirse:

```powershell
python azsos.py registry build `
  --packages-dir .\packages `
  --base-url https://raw.githubusercontent.com/TheGreatAzizi/AzSoS/IR-packages/packages `
  --out packages.index.json `
  --source-name azsos-community-packages
```

Registry sadece keşif içindir. Güven, paket imzasından gelir.

## 9. Pull Request açma

PR şunları içermelidir:

- `.azsos` paket dosyası
- içerik kaynakları ve lisans notları
- ülke ve dil bilgisi
- yayıncı fingerprint'i
- kısa test notu

İyi PR başlıkları:

```text
Add TR emergency contacts package (tr)
Add IR first-aid basic package (fa)
Add IQ family preparedness package (ar)
```

## 10. PR açıklama şablonu

Bunu PR açıklamasına kopyalayın:

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

## 11. Reddedilme veya gecikme nedenleri

- paket doğrulamadan geçmiyor
- kaynaklar belirsiz
- özel veya güvensiz içerik var
- paket gereksiz büyük
- yanıltıcı iddialar var
- PR içinde özel anahtar veya secret var
- temel içerik internet erişimine bağlı

## 12. Güvenlik hatırlatmaları

- `publisher_private.pem` dosyasını commit etmeyin.
- secret, token veya özel dosya yayınlamayın.
- her paketi imzalayın.
- özel anahtarınızı güvenli ve offline yedekleyin.
- anahtar sızarsa kullanmayı bırakın ve kullanıcıları bilgilendirin.
