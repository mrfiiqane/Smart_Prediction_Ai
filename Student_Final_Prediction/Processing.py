
# soo import liabarrys ka
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

import os
import joblib               # ku fiican yahay joblib waaweyn lagu save gareya  wana fast, pkl yaryar
import json

# 1: so jiido file ka load Dataset
CSV_PATH = "Dataset/Student_Dataset_6k.csv"
df = pd.read_csv(CSV_PATH)

print("Final INITIAL HEAD,INFO,MISSING VALUES")
print(df.head())
print(df.describe())
print(df.info())
print(df.shape) 
print(df.isnull().sum())

# 2: Hagaaji Khaladaadka,  Clean,fix
df["Age"] = df["Age"].replace(r"[.%,]", "", regex=True)
df["Attendance"] = df["Attendance"].replace(r"[% ,]", "", regex=True)
df["Attendance"] = pd.to_numeric(df["Attendance"], errors='coerce') 
df["Age"] = pd.to_numeric(df["Age"], errors='coerce') 


# 3) Fix categorical issues BEFORE imputation
df["Gender"] = df["Gender"].replace({"Females": "Female", "??": pd.NA})
df["Gender"] = df["Gender"].replace({"Man": "Male", "??": pd.NA})

# magaca column ka sax
df.rename(columns={"Midterm Exam Score": "Midterm"}, inplace=True)


# 4: Impute missing values mean average median haddi autliers jiro Impute missing values
df["Age"] = df["Age"].fillna(df["Age"].mode()[0])
df["Attendance"] = df["Attendance"].fillna(df["Attendance"].mean())


# 5: saar 2 jeer so laabta, Remove duplicates ka
before = df.shape
df = df.drop_duplicates()
after = df.shape
print(f"Dropped duplicates: before = {before} after = {after}")

yar = df.min(numeric_only = True)
weyn = df.max(numeric_only= True)
print("Tirada ugu yar waa: \n", yar)
print("Tirada ugu weyn waa: \n", weyn)

#Autlier hubi ila inte ay kala fogtahay data ka
print(df["Age"].skew())  #autliers badan
print(df["Quiz"].skew())  #autliers yar



# 6: IQR capping hagajinta autliers ka 
def iqr_fun(series, k=1.5):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return lower, upper

low_Midterm, high_Midterm = iqr_fun(df["Age"])
print(f"ugu hoseeya: {low_Midterm}, ugu sareeya: {high_Midterm}")


#clip lower & upper
low_Attendance, high_Attendance = iqr_fun(df["Attendance"])
df["Attendance"] = df["Attendance"].clip(lower=low_Attendance, upper=high_Attendance).astype(int)
print(df["Attendance"].head())


# 7 Feature engineering, Abuurista Feature cusub
df["Total"] = df["Attendance"] + df["Assignments"] + df["Quiz"] + df["Midterm"]
print(df["Total"].head())

# cloumn cusub same
df["Result"] = np.where(df["Total"] <= 29, "Fail", "Pass").astype(str)
df["Gender"] = df["Gender"].map({"Female":0, "Male":1}).astype(int)


# # 8: One Hot Encoding ku samee Result
# df = pd.get_dummies(df, columns = ["Result"], drop_first= False, dtype="int")
# print([c for c in df.columns if c.startswith("Result")])
df.loc[df["Result"].str.lower().str.strip() == "Fail", "Result"] = 0
df.loc[df["Result"].str.lower().str.strip() == "Pass",  "Result"] = 1

# 9) ka tag targets & dummies 0/1, Feature scaling X only
dont_scale = ["Total", "Gender"]
numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.to_list()
exclude = [c for c in df.columns if c.startswith("Result")]
num_features_to_scale = [c for c in numeric_cols if c not in dont_scale and c not in exclude]

scaler = StandardScaler()
df[num_features_to_scale] = scaler.fit_transform(df[num_features_to_scale])


#save the scaler and training features
os.makedirs("models", exist_ok=True)  #exist_ok haddi uu jiro in toos ugu shubo
joblib.dump(scaler, "models/Student_scaler.pkl")  #dump save gareyn scaler ka

TRAIN_COLUMNS = df.drop(columns= ["Result", "Total"]).columns.tolist()  #ka reeb target y
json.dump(TRAIN_COLUMNS, open("models/train_columns.json", "w"))  
print("\n save gareyey scaler iyo TRAIN models ka")


print("Final INITIAL HEAD,INFO,MISSING VALUES")
print(df.head())
print(df.describe())
print(df.info())
print(df.shape) 
print(df.isnull().sum())


# 10) Save
OUT_PATH = "Dataset/Clean_Student_Dataset_6k.csv"
df.to_csv(OUT_PATH, index=False)
print(f"Saved Cleaned dataset  name:{OUT_PATH}")


