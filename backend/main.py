from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import redis.asyncio as redis
import json
import joblib
import pandas as pd
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GridSentinel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = []

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

try:
    xgb_model = joblib.load("ai_research/models/xgb_anomaly_model.pkl")
    print("🧠 XGBoost Modeli Başarıyla Yüklendi!")
except Exception as e:
    print("❌ Model yükleme hatası:", e)
    xgb_model = None


async def send_telegram_alert(msg_text):
    """Anomali anında teknisyene Telegram'dan acil durum mesajı atar."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg_text}
    print(f"📱 TELEGRAM MESAJI TETİKLENDİ:\n{msg_text}")


    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload)
        except Exception as e:
            print(f"❌ Telegram Hatası: {e}")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_listener())


async def redis_listener():
    try:
        r = redis.Redis(host='localhost', port=6380, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe('sensor_data_stream')
        print("🚀 FastAPI Backend Redis'i dinlemeye başladı...")

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is not None:
                raw_data = message['data']
                data_dict = json.loads(raw_data)

                if xgb_model is not None:
                    features = pd.DataFrame([{
                        'sicaklik_c': data_dict.get('sicaklik_c', 0),
                        'nem_yuzde': data_dict.get('nem_yuzde', 0),
                        'akim_a': data_dict.get('akim_a', 0),
                        'pd_seviyesi_pc': data_dict.get('pd_seviyesi_pc', 0)
                    }])


                    probabilities = xgb_model.predict_proba(features)[0]
                    risk_score = float(probabilities[1] * 100)
                    prediction = 1 if risk_score > 50 else 0

                    data_dict['ai_risk_score'] = round(risk_score, 2)
                    data_dict['is_synthetic_anomaly'] = bool(prediction)

                    if prediction == 1:
                        ai_karari = "🚨 ANOMALİ (AI)"
                        # Yeni ve çok daha şık mesaj formatı
                        alert_msg = (
                            f"🚨 GridSentinel Kritik Alarm!\n"
                            f"📍 Pano: {data_dict.get('pano_id')}\n"
                            f"🌡 Sıcaklık: {round(data_dict.get('sicaklik_c'), 1)}°C\n"
                            f"⚡ Akım: {round(data_dict.get('akim_a'), 1)}A\n"
                            f"🔋 Kısmi Deşarj: {round(data_dict.get('pd_seviyesi_pc'), 1)} pC\n"
                            f"🤖 AI Ark Riski: %{round(risk_score, 1)}"
                        )
                        await send_telegram_alert(alert_msg)
                    else:
                        ai_karari = "✅ NORMAL"
                else:
                    ai_karari = "Model Yok"

                final_data = json.dumps(data_dict)

                dead_clients = []
                for client in connected_clients:
                    try:
                        await client.send_text(final_data)
                    except Exception:
                        dead_clients.append(client)

                for client in dead_clients:
                    if client in connected_clients:
                        connected_clients.remove(client)

            await asyncio.sleep(0.05)
    except Exception as e:
        print(f"❌ Redis Listener Hatası: {e}")


@app.websocket("/ws/monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        if websocket in connected_clients:
            connected_clients.remove(websocket)