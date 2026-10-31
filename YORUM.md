# Yorum: bu veriden ne çıkarılabilir, ne çıkarılamaz

Bu dosyadaki her sayı `sql/queries.sql`, `src/figures.py` ya da DEVLOG'da kayıtlı sorguların çıktısından geliyor. Sayılar örneklem içi ilişkiler: veri, Google Play'in %9'u kadar, geliştirici bazlı bir örneklem (ABD mağazası, Haziran 2026, yalnızca Android). "Neden" diye başlayan açıklamalar test edilmemiş hipotezdir.

## 1. Büyük uygulamalar birden fazla gelir kaynağı kullanıyor

Kurulum bandı büyüdükçe reklam ve IAP birlikte kullanılıyor. Reklam+IAP payı 1,000+ bandında %5.6 (n=37,498), 10M+ bandında %56.1 (n=1,017). Reklamsız ve IAP'siz uygulamaların payı aynı aralıkta %64.1'den %12.6'ya iniyor.

Olası açıklamalar:
- Büyüyen uygulamalar sonradan gelir modeli ekliyor olabilir.
- Baştan iki gelir kaynağıyla tasarlanan profesyonel stüdyo uygulamaları daha çok büyüyor olabilir.
- Küçük uygulamaların çoğu hobi projesi ya da bir şirketin vitrin uygulaması olabilir.

Tek tarihli veri bunları ayıramaz; bunun için aynı uygulamaları zaman içinde izlemek gerekir. Kesin olan şu: büyük uygulamalar arasında tek gelir kaynağıyla yetinen az.

## 2. Reklamsız olmak çoğu zaman "para başka yerden geliyor" demek

Finance'ta reklamsız ve IAP'siz payı her büyüklükte yüksek kalıyor: <100K grubunda %80.0, 1M+ grubunda %85.8. Productivity ve Entertainment'ta ise büyüdükçe hızla düşüyor (bkz. 3).

Büyük Finance uygulamaları büyük ihtimalle bankaların ve hizmet şirketlerinin uygulamaları; ürünü satan bir şirket var, uygulama sadece kanal. Veri bunu doğrudan göstermiyor, ama benzer örnekler var: restoran sipariş uygulamaları yapan WABiz'in iki hesabındaki 819 uygulama ve spor salonları için uygulama yapan MINDBODY'nin 273 uygulaması neredeyse tamamen reklamsız ve IAP'siz.

Sonuç: "Finance uygulamalarının %80'i reklamsız" cümlesi, SpendWise gibi bağımsız bir uygulamanın rakip kümesini anlatmıyor.

## 3. Tür ortalaması büyüklüğü gizliyor

| Tür · kurulum (n) | Reklamsız, IAP'siz | Yalnızca reklam | Reklam + IAP | Yalnızca IAP | Ücretli |
|---|---|---|---|---|---|
| Productivity · <100K (4,077) | %68.2 | %17.6 | %6.7 | %6.8 | %0.8 |
| Productivity · 100K-1M (448) | %46.4 | %21.2 | %19.9 | %10.9 | %1.6 |
| Productivity · 1M+ (195)* | %25.1 | %22.1 | %36.4 | %16.4 | %0.0 |
| Finance · <100K (3,747) | %80.0 | %13.9 | %3.2 | %2.5 | %0.3 |
| Finance · 100K-1M (726) | %78.7 | %14.5 | %5.0 | %1.9 | %0.0 |
| Finance · 1M+ (274) | %85.8 | %8.8 | %3.3 | %2.2 | %0.0 |
| Entertainment · <100K (3,808) | %40.7 | %46.0 | %7.2 | %5.6 | %0.5 |
| Entertainment · 100K-1M (911) | %17.3 | %57.5 | %17.5 | %7.7 | %0.0 |
| Entertainment · 1M+ (387) | %15.0 | %44.7 | %27.6 | %12.7 | %0.0 |

Gruplar: <100K = 1,000+ ile 50,000+ arası bantlar, 100K-1M = 100,000+ ve 500,000+, 1M+ = 1,000,000+ ve üstü. \*n < 200, dikkatli okunmalı. Grafik: `figures/05_focus_genres_by_size.png`. Dashboard'da herhangi bir tür için: tür seç, "Kurulum bandı" sekmesinde "3 büyüklük grubu" görünümü.

Productivity'nin "%64'ü reklamsız ve IAP'siz" ortalaması, binlerce küçük uygulamanın ağırlığından geliyor. 1M+ grubunda tablo tersine dönüyor: yalnızca %25'i ikisini de kullanmıyor, %36'sı reklam+IAP, %16'sı yalnızca IAP kullanıyor.

**PomoQuest için:** kıyas grubu "ortalama Productivity uygulaması" değil, hedeflenen büyüklükteki uygulamalar olmalı.

## 4. Entertainment reklamla dönüyor, IAP büyüklerde ekleniyor

"Yalnızca reklam" her büyüklük grubunda en büyük pay (%46.0, %57.5, %44.7). Reklam+IAP %7.2'den %27.6'ya, yalnızca IAP %5.6'dan %12.7'ye çıkıyor.

**Pairplot için:** bu türde reklamsız kalmak, 1M+ uygulamaların %85'inden ayrışmak demek. Bunun avantaj mı dezavantaj mı olduğunu bu veri söyleyemez.

## 5. Oyunlar ayrı bir ekonomi

| | n | Reklamsız, IAP'siz | Reklamlı | IAP'li |
|---|---|---|---|---|
| Oyun | 14,728 | %10.5 | %78.9 | %44.7 |
| Uygulama | 85,285 | %56.1 | %37.3 | %14.0 |

Oyunları ve uygulamaları aynı ortalamaya katmak iki tarafı da bulanıklaştırıyor. Reklamsız ve IAP'siz payın en düşük olduğu 20 türün 15'i oyun. PomoQuest oyunlaştırılmış olsa da Productivity'de listeleniyor ve o türün kurallarıyla kıyaslanıyor.

## 6. Ücretli uygulama modeli neredeyse yok

Tüm verinin %1.48'i ücretli. Ücretli payı 1,000+ bandında %2.2, 10M+ bandında %0.1. Üç odak türünde 1M+ grubunda hiç ücretli uygulama yok. Önden ödeme Google Play'de marjinal kalmış.

Bu verinin ölçemediği bir şey var: abonelikler IAP'nin içinde sayılıyor, ayrı görünmüyor. "Yalnızca IAP" kategorisi hem tek seferlik satın almayı hem aboneliği kapsıyor.

## 7. Rakip sayısı abartılı

Son 12 ayda güncellenmemiş uygulamaların payı 1,000+ bandında %32.3 (n=37,498), 1,000,000+ bandında %15.9, 10M+ bandında %10.9. Bir türdeki "4,700 rakip" sayısının önemli bir kısmı fiilen terk edilmiş uygulamalar. Aktif rekabet, sayının söylediğinden dar.

Sınırlama: `last_updated` tek bir tarih; güncellemenin büyüklüğünü göstermez. 365 günlük eşik bir seçim.

## 8. Uygulama fabrikaları sayımı çarpıtıyor

Üç klavye/tema hesabı (Cool keyboard skin, Delicate theme, Fancy keyboard) 1,053 uygulama yayınlamış, bunların yaklaşık %99'u yalnızca reklamlı. Tek bir saat yüzü geliştiricisi (Samtree), Personalization'daki 488 ücretli uygulamanın 175'ini yapmış. GPSmyCity'nin 380 uygulaması 2013 kohortunun IAP oranını %30.6'dan %43.4'e çekiyor.

Uygulama başına sayım bu hesapları büyütüyor. Daha adil bir ölçü geliştirici başına sayım olurdu (DEVLOG "Sonraki adımlar"da).

## 9. Yeni uygulamalar IAP'ye daha yatkın, ama temkinli oku

IAP oranı yayın yılına göre: 2023'te yayınlananlarda %18.3, 2024'te %22.7, 2025'te %28.3, 2026'da %36.0. Sınırlamalar:
- 2026 yalnızca 1 Ocak-6 Haziran arasını kapsıyor.
- Uygulamaların %17.5'inde yayın tarihi yok.
- Eski uygulamaların bugünkü gelir modeli, yayınlandıkları günkünden farklı olabilir. Veri yalnızca bugünkü durumu gösteriyor.

## Bu veri neyi söyleyemez

- **Kazanç:** gelir verisi yok; hangi modelin daha çok kazandırdığı bilinmiyor.
- **Etki:** reklamın ya da IAP'nin puanı, kurulumu ya da büyümeyi etkileyip etkilemediği. Burada yalnızca birlikte görülme var.
- **iOS:** veri Android. PomoQuest ve SpendWise yalnızca iOS'ta; App Store'da gelir modeli dağılımı farklı olabilir.
- **Tam mağaza:** örneklem geliştirici bazlı. Genel oranlar tam veriyle 0.5 puan içinde tutsa da tür düzeyinde birkaç büyük geliştirici tabloyu kaydırabiliyor.

## Kısaca

Google Play'de para kazanmak tür ve ölçekle değişen bir karar. Ortalama uygulamayı değil, hedeflediğin büyüklükteki ve türdeki uygulamaları kıyas almak gerekiyor. Finance gibi türlerde "reklamsız" norm, ayrı bir iş modeline sahip şirket uygulamalarından gelebilir.
