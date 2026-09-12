# ⚡ GridSentinel - AI-Powered IoT SCADA & Grid Monitoring System

GridSentinel, elektrik panolarındaki (örneğin 1600kVA) ark flaşı, aşırı ısınma ve kısmi deşarj gibi kritik anomalileri tespit etmek için geliştirilmiş **gerçek zamanlı ve yapay zeka destekli bir IoT izleme sistemidir.**

Kaggle standartlarında tasarlanmış MLOps boru hattı sayesinde, sensör verileri milisaniyeler içinde işlenir, risk skoru hesaplanır ve kriz anlarında bakım mühendislerine doğrudan Telegram üzerinden acil durum bildirimleri iletilir.

## 🚀 Temel Özellikler

* **Gerçek Zamanlı SCADA İzleme:** Sensörlerden gelen sıcaklık, nem, akım ve kısmi deşarj (PD) verilerini Next.js arayüzünde canlı (WebSocket) olarak görselleştirir.
* **XGBoost ile Anomali Tespiti:** Sentetik kriz verileriyle eğitilmiş makine öğrenmesi modeli, %99+ doğruluk oranıyla ark riski tahmini yapar.
* **Uçtan Uca İletişim (Telegram FCM):** Kritik bir anomali tespit edildiğinde, sistem saniyeler içinde yetkili personelin telefonuna yapılandırılmış Telegram uyarıları fırlatır.
* **Endüstriyel Protokol Desteği:** Fiziksel donanımlarla iletişim kurabilmek için arka planda aktif bir Modbus TCP Sunucusu barındırır.
* **Event-Driven Mimari:** Redis Pub/Sub üzerinden akan veriler, darboğaz yaratmadan FastAPI'ye ve oradan frontend'e aktarılır.

## 🛠️ Teknoloji Yığını

| Katman | Teknoloji | Görevi |
| :--- | :--- | :--- |
| **Yapay Zeka (AI)** | Python, XGBoost, Pandas, Scikit-Learn | Kaggle-grade MLOps, Anomali risk skoru tahmini. |
| **Backend / API** | FastAPI, Uvicorn, httpx | Asenkron veri işleme, WebSocket yönetimi ve Telegram entegrasyonu. |
| **Frontend** | Next.js, React, Tailwind CSS | Glassmorphism tasarımlı, gerçek zamanlı kullanıcı arayüzü. |
| **Veri & Mesajlaşma** | Redis (Pub/Sub) | IoT simülatörü ile backend arasındaki yüksek hızlı veri akışı. |
| **Endüstriyel Haberleşme** | Modbus TCP, PyModbus | SCADA ve PLC sistemleri ile endüstri standardında entegrasyon. |

## ⚙️ Kurulum ve Çalıştırma

### 1. Ön Koşullar

* **Node.js** (v18+)
* **Python** (3.9+)
* **Redis** (Docker üzerinden veya lokal olarak 6380 portunda çalışır durumda olmalıdır)

### 2. Projeyi Klonlama ve Bağımlılıklar

Backend kütüphanelerini kurmak için (Bağımlılıklar `backend/requirements.txt` dosyasında yer almaktadır):

```bash
git clone https://github.com/KULLANICI_ADIN/gridsentinel.git
cd gridsentinel
pip install -r backend/requirements.txt
```

Frontend kütüphanelerini kurmak için:

```bash
cd frontend
npm install
cd ..
```

### 3. Yapay Zeka Modelini Eğitme (İlk Kurulum)

Sistemin krizleri tanıyabilmesi için XGBoost modelini oluşturmanız gerekir:

```bash
python train_model.py
```

(Bu işlem `ai_research/models/xgb_anomaly_model.pkl` dosyasını üretecektir.)

### 4. Tek Tıkla Sistemi Başlatma

Tüm servisleri (FastAPI, Next.js, Redis Listener, Modbus Server ve IoT Simülatörü) eşzamanlı olarak başlatmak için:

```bash
chmod +x start.sh
./start.sh
```

* **Web Arayüzü:** http://localhost:3000
* **API Dokümantasyonu (Swagger):** http://localhost:8001/docs

## 📱 Bildirim Sistemi (Telegram)

Sistem, risk skoru %50'yi aştığı anda belirlenen `CHAT_ID`'ye aşağıdaki formatta bildirim gönderir:

```
🚨 GridSentinel Kritik Alarm!

📍 Pano: PANO_1600kVA_01
🌡 Sıcaklık: 87.2°C
⚡ Akım: 922.1A
🔋 Kısmi Deşarj: 6.9 pC
🤖 AI Ark Riski: %99.9
```