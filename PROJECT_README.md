# SmartAgroTechnologies CVP & Sensitivity Analysis

## Amaç (Türkçe)
Bu uygulama, küçük tarım ekipmanlarında kullanılan dizel motorlar için maliyet-hacim-kâr (CVP) ve hassasiyet analizini görselleştirir. Kullanıcı, satış fiyatı, değişken/sabit maliyetler, vergi oranı ve satış adedi gibi parametreleri girer; sistem katkı payı, faaliyet kârı, net kâr ve başa baş noktalarını hesaplayıp grafiklerle gösterir. Üç senaryo (A/B/C) için fiyat, maliyet ve hacim varsayımlarını değiştirerek etkileri anında karşılaştırabilirsiniz.

## Purpose (English)
This app visualizes cost-volume-profit (CVP) and sensitivity analysis for diesel engines in small farm equipment. Users enter parameters (selling price, variable/fixed costs, tax rate, units sold); the system computes contribution margin, operating income, net income, and break-even points, then renders server-side charts. Three scenarios (A/B/C) let you adjust price, cost, and volume assumptions and compare their impact immediately.

## Özellikler / Features
- Form girdileri değiştiğinde otomatik yenileme (sunucu tarafı Matplotlib grafikleri).
- Katkı payı ve başa baş analizi; işletme kârı eğrileri ve B/E noktaları.
- Senaryolar: fiyat düşürüp hacim artırma (A), maliyet ve fiyat düşürme (B), sabit gider ve fiyat düşürüp hacmi değiştirme (C).
- Eksenlerde bilimsel gösterim yok; rakamlar binlik ayraçlı.

## Çalıştırma / Run
```bash
cd /Users/oguzakpinar/python-project
source venv/bin/activate
python app.py
# open http://localhost:5001
```

## Girdi / Input
- Satış fiyatı, değişken maliyet, sabit maliyet, vergi oranı, satış adedi.
- Senaryo parametreleri: fiyat indirimleri, satış artışı, değişken maliyet indirimi, sabit gider indirimi, hedef hacim.

## Çıktı / Output
- Kartlar: toplam katkı payı, birim katkı, katkı yüzdesi, faaliyet kârı, net kâr, başa baş (adet/gelir).
- Grafikler: maliyet yapısı, toplam katkı payı, senaryo bazlı işletme kârı vs. hacim, senaryo maliyet vs. gelir.

## Tavsiye / Recommendation
- Kârlılık önceliği için genelde Senaryo B (maliyet ve fiyat indirimi).
- Daha düşük başa baş eşiği için Senaryo C (sabit gider düşüşü) düşünülebilir.

