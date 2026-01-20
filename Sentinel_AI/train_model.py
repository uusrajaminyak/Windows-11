import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

print("[+] Creating malware and benign simulation datasets...")

malware_data = {
    'SectionMaxEntropy': np.random.uniform(7.0, 8.0, 1000),
    'Subsystem': np.random.randint(2, 3, 1000),
    'ImportNB': np.random.randint(1, 5, 1000),
    'is_malware': 1
}

benign_data = {
    'SectionMaxEntropy': np.random.uniform(3.0, 7.0, 1000),
    'Subsystem': np.random.randint(2, 3, 1000),
    'ImportNB': np.random.randint(50, 500, 1000),
    'is_malware': 0
}

df_malware = pd.DataFrame(malware_data)
df_benign = pd.DataFrame(benign_data)
data = pd.concat([df_malware, df_benign]).sample(frac=1).reset_index(drop=True)

print(f"[+] Dataset ready with total sample: {len(data)}\n")
print(data.head())

print("\n[+] Training AI...")
x = data.drop('is_malware', axis=1)
y = data['is_malware']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(x_train, y_train)

y_pred = clf.predict(x_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"[+] Model accuracy: {accuracy * 100:.2f}%")

joblib.dump(clf, 'malware_detection_model.pkl')
print("[+] Model saved as malware_detection_model.pkl")