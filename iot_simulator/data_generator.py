import time
import json
import random
import redis

try:
    r = redis.Redis(host='localhost', port=6380, decode_responses=True)
except Exception as e:
    print("❌ Redis bağlantı hatası:", e)

def generate_sensor_data(pano_id="PANO_1600kVA_01"):

    sicaklik = random.uniform(35.0, 45.0)  # Santigrat
    nem = random.uniform(40.0, 50.0)  # Yüzde


    sekonder_mA = random.uniform(20.0, 80.0)
    primer_A = sekonder_mA * (6000 / 1000)  # Çarpan mantığı

    pd_seviyesi = random.uniform(0.0, 10.0)


    ark_durumu = 0


    is_anomaly = random.random() < 0.15
    if is_anomaly:
        anomali_tipi = random.choice(["asiri_isinma", "kismi_desarj", "yuksek_akim", "ark_flasi"])

        if anomali_tipi == "asiri_isinma":
            sicaklik = random.uniform(75.0, 95.0)
        elif anomali_tipi == "kismi_desarj":
            pd_seviyesi = random.uniform(50.0, 150.0)
        elif anomali_tipi == "yuksek_akim":
            primer_A = random.uniform(800.0, 1200.0)
        elif anomali_tipi == "ark_flasi":
            ark_durumu = 1
            sicaklik += 20.0

    payload = {
        "pano_id": pano_id,
        "timestamp": time.time(),
        "sicaklik_c": round(sicaklik, 2),
        "nem_yuzde": round(nem, 2),
        "akim_a": round(primer_A, 2),
        "pd_seviyesi_pc": round(pd_seviyesi, 2),
        "ark_durumu": ark_durumu,
        "is_synthetic_anomaly": is_anomaly
    }
    return payload

if __name__ == "__main__":
    print("🚀 Sentetik Veri Üreticisi Başladı. SCADA Ağına Veri Basılıyor...")
    while True:
        data = generate_sensor_data()

        try:
            r.publish('sensor_data_stream', json.dumps(data))
        except Exception as e:
            pass


        if data["is_synthetic_anomaly"]:
            print(f"🚨 KRİZ TETİKLENDİ! Pano: {data['pano_id']} | Yapay Zeka Devrede!")
            print(f"   => Detay: Sıcaklık {data['sicaklik_c']}°C, Akım {data['akim_a']}A, PD {data['pd_seviyesi_pc']}pC\n")
        else:
            print(f"✅ Normal Akış: {data['sicaklik_c']}°C, {data['akim_a']}A, PD: {data['pd_seviyesi_pc']}pC")

        time.sleep(1)