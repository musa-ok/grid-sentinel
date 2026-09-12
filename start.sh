#!/bin/bash

echo "🚀 GridSentinel Uçtan Uca Başlatılıyor..."

# 1. FastAPI Backend'i Başlat
echo "📡 Backend (AI & API) ayağa kalkıyor..."
uvicorn backend.main:app --port 8001 &
BACKEND_PID=$!
sleep 2

# 2. Modbus TCP Server'ı Başlat
echo "🔌 Modbus TCP Server (SCADA) 5020 portunda dinliyor..."
python iot_simulator/modbus_server.py &
MODBUS_PID=$!
sleep 1

# 3. Veri Simülatörünü Başlat
echo "🔥 Sentetik Veri (Sensör) Üreticisi başlatıldı..."
python iot_simulator/data_generator.py &
SIMULATOR_PID=$!
sleep 1

# 4. Next.js Frontend'i Başlat
echo "💻 Frontend (Next.js) localhost:3000 üzerinde başlatılıyor..."
cd frontend && npm run dev &
FRONTEND_PID=$!

# Terminal kapatıldığında arkada asılı işlem kalmaması için temizleme kancası (trap)
trap "echo '🛑 GridSentinel kapatılıyor...'; kill $BACKEND_PID $MODBUS_PID $SIMULATOR_PID $FRONTEND_PID; exit" SIGINT SIGTERM

echo ""
echo "✅ BÜTÜN SİSTEM AKTİF!"
echo "👉 Tarayıcıda http://localhost:3000 adresine gidebilirsin."
echo "👉 Sistemi tamamen durdurmak için bu ekranda CTRL+C yapman yeterli."
echo ""

# Scriptin kapanmasını engellemek için arka plandaki işlemleri bekle
wait