import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os

print("🧠 Sentetik Eğitim Verisi Hazırlanıyor...")
np.random.seed(42)
n_samples = 5000

normal_data = pd.DataFrame({
    'sicaklik_c': np.random.uniform(35, 45, n_samples),
    'nem_yuzde': np.random.uniform(40, 50, n_samples),
    'akim_a': np.random.uniform(120, 400, n_samples),
    'pd_seviyesi_pc': np.random.uniform(0, 10, n_samples),
    'label': 0 # 0: Normal
})

anomaly_data = pd.DataFrame({
    'sicaklik_c': np.random.uniform(60, 95, n_samples // 4),
    'nem_yuzde': np.random.uniform(30, 60, n_samples // 4),
    'akim_a': np.random.uniform(700, 1200, n_samples // 4),
    'pd_seviyesi_pc': np.random.uniform(30, 150, n_samples // 4),
    'label': 1 # 1: Anomali
})


df = pd.concat([normal_data, anomaly_data], ignore_index=True)
df = df.sample(frac=1).reset_index(drop=True) # Shuffle

X = df.drop('label', axis=1)
y = df['label']

print("🚀 XGBoost Modeli Eğitiliyor...")
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)

model.fit(X, y)

os.makedirs('ai_research/models', exist_ok=True)
model_path = 'ai_research/models/xgb_anomaly_model.pkl'
joblib.dump(model, model_path)

print(f"✅ Model başarıyla eğitildi ve kaydedildi: {model_path}")
