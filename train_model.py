import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os

print("📊 1. GridSentinel Sentetik Veri Seti Üretiliyor...")
np.random.seed(42)

# 1. NORMAL VERİLER (5000 Adet)
df_normal = pd.DataFrame({
    'sicaklik_c': np.random.uniform(35.0, 45.0, 5000),
    'nem_yuzde': np.random.uniform(40.0, 50.0, 5000),
    'akim_a': np.random.uniform(200.0, 450.0, 5000),
    'pd_seviyesi_pc': np.random.uniform(0.0, 10.0, 5000),
    'is_anomaly': 0
})

# 2. SADECE AŞIRI ISINMA ANOMALİSİ (1000 Adet - Sadece ısı yüksek, diğerleri normal)
df_isinma = pd.DataFrame({
    'sicaklik_c': np.random.uniform(75.0, 95.0, 1000),
    'nem_yuzde': np.random.uniform(40.0, 50.0, 1000),
    'akim_a': np.random.uniform(200.0, 450.0, 1000), # Normal
    'pd_seviyesi_pc': np.random.uniform(0.0, 10.0, 1000), # Normal
    'is_anomaly': 1
})

# 3. SADECE YÜKSEK AKIM ANOMALİSİ (1000 Adet - Sadece akım yüksek, diğerleri normal)
df_akim = pd.DataFrame({
    'sicaklik_c': np.random.uniform(35.0, 45.0, 1000), # Normal
    'nem_yuzde': np.random.uniform(40.0, 50.0, 1000),
    'akim_a': np.random.uniform(800.0, 1200.0, 1000), # Yüksek
    'pd_seviyesi_pc': np.random.uniform(0.0, 10.0, 1000), # Normal
    'is_anomaly': 1
})

# 4. SADECE KISMİ DEŞARJ ANOMALİSİ (1000 Adet - Sadece PD yüksek, diğerleri normal)
df_pd = pd.DataFrame({
    'sicaklik_c': np.random.uniform(35.0, 45.0, 1000), # Normal
    'nem_yuzde': np.random.uniform(40.0, 50.0, 1000),
    'akim_a': np.random.uniform(200.0, 450.0, 1000), # Normal
    'pd_seviyesi_pc': np.random.uniform(50.0, 150.0, 1000), # Yüksek
    'is_anomaly': 1
})

# 5. ARK FLAŞI ANOMALİSİ (1000 Adet - Ani ısı sıçraması)
df_ark = pd.DataFrame({
    'sicaklik_c': np.random.uniform(55.0, 65.0, 1000),
    'nem_yuzde': np.random.uniform(40.0, 50.0, 1000),
    'akim_a': np.random.uniform(200.0, 450.0, 1000),
    'pd_seviyesi_pc': np.random.uniform(0.0, 10.0, 1000),
    'is_anomaly': 1
})

# Bütün verileri birleştir ve karıştır
df = pd.concat([df_normal, df_isinma, df_akim, df_pd, df_ark]).sample(frac=1).reset_index(drop=True)
X = df[['sicaklik_c', 'nem_yuzde', 'akim_a', 'pd_seviyesi_pc']]
y = df['is_anomaly']

print("🧠 2. XGBoost Modeli Yeni ve Akıllı Mantıkla Eğitiliyor...")
model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
model.fit(X, y)

# Yeni Modeli Kaydet
os.makedirs("ai_research/models", exist_ok=True)
model_path = "ai_research/models/xgb_anomaly_model.pkl"
joblib.dump(model, model_path)
print(f"✅ Model başarıyla eğitildi ve {model_path} konumuna kaydedildi!")