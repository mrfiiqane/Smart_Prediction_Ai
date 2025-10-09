import json
import joblib
import pandas as pd
import numpy as np

# Load once at import
TRAIN_COLUMNS = json.load(open("models/train_columns.json"))
SCALER = joblib.load("models/Student_scaler.pkl") 

#aan la scale garen
DONT_SCALE = ["Total", "Gender", "Result"]

def prepare_features_from_raw(Data) -> tuple[np.ndarray, pd.Series]: 
    """
    Diyaarinta features-ka.
    Data waxay noqon kartaa dict (hal arday) ama pandas DataFrame (arday badan).
    """
    
    # KALA SOOCIDDA: DICT (HAL ARDAY) VS DATAFRAME (ARDAY BADAN)
    
    if isinstance(Data, dict):
        # QAABKA 1: HAL ARDAY (JSON/DICT) - Wuxuu u baahan yahay 6 features
        
        # 1: data user ka ceyrin(Age, Midterm, Gender) into the engineered and scaled to training
        Age = int(Data.get("Age", 0.0))
        Gender = str(Data.get("Gender", "Male")).lower().strip()
        Attendance = float(Data.get("Attendance", 0.0))
        Assignments = float(Data.get("Assignments", 0.0))
        Quiz = float(Data.get("Quiz", 0.0))
        Midterm = float(Data.get("Midterm", 0.0))
        
        # 2. Feature Engineering & Xisaabinta Total-ka
        Total = Attendance + Assignments + Quiz + Midterm
        # Waxaan ka soo qaadanayaa in 'Gender_encoded' la isticmaalo
        Gender_encoded = 1 if Gender == "male" else 0 
        
        # Build a full row with zeros for all training columns
        row = {col: 0.0 for col in TRAIN_COLUMNS}

        # Ku dar qiimaha xogta loo soo diray
        feature_values = [
             ("Age", Age),
             ("Attendance", Attendance),
             ("Assignments", Assignments),
             ("Quiz", Quiz),
             ("Midterm", Midterm),
             ("Gender", Gender_encoded), # Waxaan ka soo qaadanayaa in TRAIN_COLUMNS ay ku jirto 'Gender' ama 'Gender_encoded'
        ]
        
        for name, Value in feature_values:
             # Hubi in name-ka uu ku jiro TRAIN_COLUMNS
            if name in row:
                row[name] = float(Value)
            # Tani waa haddii TRAIN_COLUMNS ay isticmaalayso magac kale sida 'Gender_Male'
            elif f"{name}_Male" in row:
                 row[f"{name}_Male"] = float(Value)


        # 1-row DataFrame with correct column order
        df_one = pd.DataFrame([row], columns=TRAIN_COLUMNS)
    
        # Scale only the columns the scaler was fitted on
        if hasattr(SCALER, "feature_names_in_"):
            cols_to_scale = list(SCALER.feature_names_in_)
            df_one[cols_to_scale] = SCALER.transform(df_one[cols_to_scale])
            
        # Natiijada ugu dambeysa
        x_new = df_one.values
        Total_Scores = pd.Series([Total]) # U beddel series si ay isku qaab u noqdaan

        return x_new, Total_Scores
    
    elif isinstance(Data, pd.DataFrame):
        # QAABKA 2: ARDAY BADAN (XLSX/DATAFRAME) - U baahan kaliya 4 features sidaad rabto
        
        df = Data.copy() # Isticmaal copy si aad u ilaaliso asalka

        # 1. Soo qaado 4-ta tiir ee dhibcaha
        required_cols = ["Attendance", "Assignments", "Quiz", "Midterm"]
        
        # Hubi in tiirarku ay yihiin tirooyin
        for col in required_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Xisaabinta wadarta dhibcaha
        Total_Scores = df[required_cols].sum(axis=1)

        # 2. Xisaabi labada features ee dheeraadka ah (Age iyo Gender) si moodeelka loogu buuxiyo 6 features
        
        # Tani waa qaybta ay tahay inaad hubiso sida moodeelkaaga loo tababaray
        # Haddii moodeelku u baahan yahay 6 features, waa inaan buuxinaa labadii maqnaa
        
        # Buuxi Age iyo Gender qiimo default ah 
        # (Tani waxay ka dhigi kartaa saadaalinta mid aan sax ahayn haddii Age/Gender muhiim yihiin!)
        
        df['Age'] = df.get('Age', df['Attendance'].apply(lambda x: 20)) # Qiimo default ah: 20
        df['Gender'] = df.get('Gender', df['Attendance'].apply(lambda x: 'Male')) # Qiimo default ah: Male
        df['Gender_encoded'] = (df['Gender'].str.lower().str.strip() == 'male').astype(int)

        # 3. Samee 6-da Tiir ee Saxda ah (Waa inaad la mid dhigtaa TRAIN_COLUMNS)
        
        # Kani wuxuu hubinayaa in tiirarku ay yihiin 6-da tiir ee moodeelku u baahan yahay
        feature_map = {
             "Attendance": df["Attendance"],
             "Assignments": df["Assignments"],
             "Quiz": df["Quiz"],
             "Midterm": df["Midterm"],
             "Age": df["Age"],
             # Waxaan ka soo qaadanayaa in tiirka labaad ee gender uu yahay 'Gender'
             "Gender": df["Gender_encoded"], 
        }
       
        # Soo qaado tiirarka saxda ah ee moodeelka
        df_features = pd.DataFrame(feature_map)
        df_features = df_features[[col for col in TRAIN_COLUMNS if col in df_features.columns]]

        # 4. Scale
        if hasattr(SCALER, "feature_names_in_"):
            cols_to_scale = list(SCALER.feature_names_in_)
            df_features[cols_to_scale] = SCALER.transform(df_features[cols_to_scale])
        
        # Natiijada ugu dambeysa
        x_new = df_features.values 

        return x_new, Total_Scores
        
    else:
        raise TypeError("Qaabka xogta lama aqbali karo. Waa inay ahaataa dict ama DataFrame.")