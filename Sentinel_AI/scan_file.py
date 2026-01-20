import joblib
import pandas as pd
import sys
import pefile
import math
from collections import Counter

def load_model():
    print("[*] Loading the trained AI model...")
    try:
        model = joblib.load('malware_detection_model.pkl')
        return model
    except:
        print("[-] Error: Model file not found. Please train the model first.")
        sys.exit()
        
def calculate_entropy(data):
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        p_x = count/length
        entropy -= p_x * math.log(p_x, 2)
    return entropy

def extract_features(filepath):
    print(f"[*] Extracting features from {filepath}...")
    try:
        pe = pefile.PE(filepath)
    except OSError as e:
        print(f"[-] Error: Could not open file. {e}")
        return None
    except pefile.PEFormatError as e:
        print(f"[-] Error: Not a valid .exe file. {e}")
        return None
    subsystem = pe.OPTIONAL_HEADER.Subsystem
    try:
        import_nb = 0
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                import_nb += len(entry.imports)
    except AttributeError:
        import_nb = 0
    section_entropies = []
    for section in pe.sections:
        section_data = section.get_data()
        entropy = calculate_entropy(section_data)
        section_entropies.append(entropy)
    section_max_entropy = 0
    if len(section_entropies) > 0:
        section_max_entropy = max(section_entropies)
    else:
        max_entropy = 0
        
    print(f"Real data found:")
    print(f" - SectionMaxEntropy: {section_max_entropy}")
    print(f" - Subsystem: {subsystem}")
    print(f" - ImportNB: {import_nb}")
    features = {
        'SectionMaxEntropy': section_max_entropy,
        'Subsystem': subsystem,
        'ImportNB': import_nb
    }
    df = pd.DataFrame([features])
    df = df[['SectionMaxEntropy', 'Subsystem', 'ImportNB']]
    return df

if __name__ == "__main__":
    model = load_model()
    target_file = input("Enter the path of the file to scan: ").strip().strip('""')
    data_file = extract_features(target_file)
    if data_file is not None:
        prediction = model.predict(data_file)[0]
        probability = model.predict_proba(data_file)[0][1]*100
        print("=" * 30)
        print(f"File Scanned: {target_file}")
        print("=" * 30)
    if prediction == 1:
        print("Result: MALWARE DETECTED")
        print(f"Malware Probability: ({probability:.1f}%)")
        if data_file['ImportNB'][0] < 5:
            print("[-] Warning: Low number of imports detected, which is common in packed malware.")
        if data_file['SectionMaxEntropy'][0] > 7.0:
            print("[-] Warning: High section entropy detected, which may indicate packed or obfuscated code.")
    else:
        print("Result: File is Clean")
        print(f"Benign Probability: ({100-probability:.1f}%)")