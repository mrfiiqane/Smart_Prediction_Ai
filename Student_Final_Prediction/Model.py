
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

#algorithms ka 
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier, XGBRegressor

from sklearn.preprocessing import LabelEncoder                   #kan ka fudud kan positive label intan isticmali laha
from sklearn.preprocessing import StandardScaler                   #kan ka fudud kan positive label intan isticmali laha
#matreics ka
from sklearn.metrics import ( accuracy_score, precision_score, recall_score, f1_score, confusion_matrix )

import joblib    #keydinta scaler
import os
from Utilities import prepare_features_from_raw


# 1: Load the cleaned dataset
CSV_PATH = "Dataset/Clean_Student_Dataset_6k.csv"
df = pd.read_csv(CSV_PATH)

RANDOM_STATE = 42

# 2: kala saar Features x iyo Target y 
x = df.drop(columns=["Total", "Result"])
y = df["Result"]

# LabelEncoder
le = LabelEncoder()
y = le.fit_transform(y) 


# 3) Train/test split (stratified)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)
print("Train:", x_train.shape[0],  "Test:", x_test.shape[0])

# scaler
scalar = StandardScaler()
X_train = scalar.fit_transform(x_train)   # fit,transform train data
X_test = scalar.transform(x_test)          #only transform test data


# Train Logistic Regression 
lr = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
lr.fit(x_train, y_train)
lr_pred = lr.predict(x_test)


# Train Random Forest
rf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE)
rf.fit(x_train, y_train)
rf_pred = rf.predict(x_test)

# Train DECISION TREE
dt = DecisionTreeClassifier(random_state=RANDOM_STATE)
dt.fit(x_train, y_train)
dt_pred = dt.predict(x_test)

# Train XGBOOST
xgb = XGBClassifier(random_state=RANDOM_STATE)
xgb.fit(x_train, y_train)
xgb_pred = xgb.predict(x_test)



# 7  metrics + confusion matrix, pos_label=0 means 'fail' is positive.
def print_metrics(name, y_true, y_pred):
    
    acc = accuracy_score(y_true, y_pred)
    pre = precision_score(y_true, y_pred, pos_label=1)
    rec = recall_score(y_true, y_pred, pos_label=1)
    f1 = f1_score(y_true, y_pred, pos_label=1)
    print(f"\n{name} Performance:")
    print(f"  Accuracy : {acc:.3f}")
    print(f"  Precision: {pre:.3f}") 
    print(f"  Recall   : {rec:.3f}") 
    print(f"  F1-Score : {f1:.3f}")


print_metrics("logistic Regression", y_test, lr_pred)
print_metrics("Random Forest",   y_test, rf_pred)    
print_metrics("DECISION TREE",   y_test, dt_pred)    
print_metrics("XGBOOST",   y_test, xgb_pred)    

# 9 Single-row sanity check
i = 3     #qofka 3aad xogtiisa
x_one_df = x_test.iloc[[i]]     # 1-row DataFrame (keeps feature names)
y_true = y_test[i]  # scalar 
p_lr_one = (lr.predict(x_one_df)[0])
p_rf_one = (rf.predict(x_one_df)[0])
p_dt_one = (dt.predict(x_one_df)[0])
p_xgb_one = (xgb.predict(x_one_df)[0])

print("\nSingle-row sanity check:")
print(f"  Actual Result: {y_true}")
print(" LR Pred:", p_lr_one)
print(" RF Pred:", p_rf_one)
print(" dt Pred:", p_dt_one)
print(" xgb Pred:", p_xgb_one)


# 9) Optional: local custom input test using the shared helper
custom = {
    "Age": 21, "Gender": "Male", "Attendance": "5", "Assignments": 15, "Quiz": 10, "Midterm": 19
}
x_new_df, Total = prepare_features_from_raw(custom)
print("\n Custom Input Prediction {custom}")
print("logistic Regression:", lr.predict(x_new_df)[0])
print("Random Forest    :", rf.predict(x_new_df)[0])
print("decision tree", dt.predict(x_new_df)[0])
print("XGBOOST   :", xgb.predict(x_new_df)[0])



# 8) SAVE MODELS
joblib.dump(lr, "models/lr_model.joblib")
joblib.dump(rf, "models/rf_model.joblib")
joblib.dump(dt, "models/dt_model.joblib")
joblib.dump(xgb, "models/xgb_model.joblib")
print("\nSaved  models lr,fr,dt,xgb")

