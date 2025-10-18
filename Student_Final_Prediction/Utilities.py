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
    

    # DICT 1 ARDAY, DATAFRAME ARDAY BADAN
    
    if isinstance(Data, dict):
     
        Age = int(Data.get("Age", 0.0))
        Gender = str(Data.get("Gender", "Male")).lower().strip()
        Attendance = float(Data.get("Attendance", 0.0))
        Assignments = float(Data.get("Assignments", 0.0))
        Quiz = float(Data.get("Quiz", 0.0))
        Midterm = float(Data.get("Midterm", 0.0))
       
        Total = Attendance + Assignments + Quiz + Midterm
    
        Gender_encoded = 1 if Gender == "male" else 0 
  
        row = {col: 0.0 for col in TRAIN_COLUMNS}
    
        feature_values = [
             ("Age", Age),
             ("Attendance", Attendance),
             ("Assignments", Assignments),
             ("Quiz", Quiz),
             ("Midterm", Midterm),
             ("Gender", Gender_encoded), 
        ]
        
        for name, Value in feature_values:
            if name in row:
                row[name] = float(Value)
            elif f"{name}_Male" in row:
                 row[f"{name}_Male"] = float(Value)


        df_one = pd.DataFrame([row], columns=TRAIN_COLUMNS)
    
        if hasattr(SCALER, "feature_names_in_"):
            cols_to_scale = list(SCALER.feature_names_in_)
            df_one[cols_to_scale] = SCALER.transform(df_one[cols_to_scale])
            
        # Natiijada ugu dambeysa
        x_new = df_one.values
        Total_Scores = pd.Series([Total]) # U beddel series si ay isku qaab u noqdaan

        return x_new, Total_Scores
    
    elif isinstance(Data, pd.DataFrame):
        
        df = Data.copy() 
      
        required_cols = ["Attendance", "Assignments", "Quiz", "Midterm"]
       
        for col in required_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
        Total_Scores = df[required_cols].sum(axis=1)
        
        df['Age'] = df.get('Age', df['Attendance'].apply(lambda x: 20)) # Qiimo default ah: 20
        df['Gender'] = df.get('Gender', df['Attendance'].apply(lambda x: 'Male')) # Qiimo default ah: Male
        df['Gender_encoded'] = (df['Gender'].str.lower().str.strip() == 'male').astype(int)
      
        feature_map = {
             "Attendance": df["Attendance"],
             "Assignments": df["Assignments"],
             "Quiz": df["Quiz"],
             "Midterm": df["Midterm"],
             "Age": df["Age"],
             # Waxaan ka soo qaadanayaa in tiirka labaad ee gender uu yahay 'Gender'
             "Gender": df["Gender_encoded"], 
        }

        df_features = pd.DataFrame(feature_map)
        df_features = df_features[[col for col in TRAIN_COLUMNS if col in df_features.columns]]

        if hasattr(SCALER, "feature_names_in_"):
            cols_to_scale = list(SCALER.feature_names_in_)
            df_features[cols_to_scale] = SCALER.transform(df_features[cols_to_scale])
        
        x_new = df_features.values 

        return x_new, Total_Scores
        
    else:
        raise TypeError("Qaabka xogta lama aqbali karo. Waa inay ahaataa dict ama DataFrame.")