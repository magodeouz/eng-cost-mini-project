# SmartAgroTechnologies CVP & Sensitivity Analysis

Flask tabanlı, Matplotlib ile sunucu tarafında grafik üreten CVP ve hassasiyet analizi aracı.

## Kurulum
```bash
cd /Users/oguzakpinar/python-project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma
```bash
source venv/bin/activate
python app.py
```
Tarayıcı: `http://localhost:5001`

Notlar:
- Formdaki sayısal değerler değiştiğinde ~450 ms içinde otomatik gönderilir, grafikler yeniden üretilir.
- Bilimsel gösterim yok; eksenler binlik ayraçla gösterilir.

## Önemli Kod Blokları

### Metrik hesapları (`app.py`)
```python
def calculate_metrics(*, selling_price, variable_cost, fixed_costs, units_sold, tax_rate):
    cm_per_unit = selling_price - variable_cost
    total_cm = cm_per_unit * units_sold
    operating_income = total_cm - fixed_costs
    net_income = operating_income * (1 - tax_rate / 100.0)
    breakeven_units = fixed_costs / cm_per_unit if cm_per_unit > 0 else 0
    breakeven_revenue = breakeven_units * selling_price
    cm_pct = cm_per_unit / selling_price if selling_price > 0 else 0
    return {...}
```
Katkı payı, faaliyet kârı, net kâr ve başa baş noktası (adet/gelir) hesaplanır; senaryolar bu fonksiyonu kullanır.

### Senaryo OI grafiği (`app.py`)
```python
def plot_scenario_compare(scenarios):
    for key, p in scenarios.items():
        m = calculate_metrics(**strip_label(p))
        oi_line = [(p["selling_price"] - p["variable_cost"]) * u - p["fixed_costs"] for u in units]
        ax.plot(units, oi_line, ...)
        ax.scatter([m["breakeven_units"]], [0], ...)
    ax.axhline(0, linestyle="--")
```
Her senaryo için işletme kârı eğrisi ve başa baş noktası çizilir; eksenler binlik ayraçlıdır.

### Ana görünüm ve senaryolar (`app.py`)
```python
@app.route("/")
def analysis():
    params = {...}  # baseline form değerleri
    scA = {..., "label": "Scenario A (price ↓, volume ↑)"}
    scB = {..., "label": "Scenario B (lower price & VC)"}
    scC = {..., "label": "Scenario C (fixed ↓, price ↓)"}
    scenario_metrics = {k: calculate_metrics(**strip_label(v)) for k, v in scenarios.items()}
    # Matplotlib grafikleri base64 olarak template'e gönderilir
    return render_template("analysis.html", ...)
```
Form girdileri alınır, A/B/C senaryoları oluşturulur, metrikler hesaplanır ve grafik görselleri template’e gömülür.

## Çıkış
```bash
deactivate
```

## Sorun Giderme
- Port 5001 doluysa: `lsof -ti:5001 | xargs kill`
- Değişiklik görmüyorsanız tarayıcıyı yenileyin; debug açıkken yeniden yükleme devrededir.
