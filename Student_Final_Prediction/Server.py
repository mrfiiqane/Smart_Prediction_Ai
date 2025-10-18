
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib

import pandas as pd 
from io import BytesIO

from Utilities import prepare_features_from_raw

# Initialize server
App = Flask(__name__)
CORS(App)

# models
MODELS = {
  "lr": joblib.load("models/lr_model.joblib"),
  "rf": joblib.load("models/rf_model.joblib"),
  "dt": joblib.load("models/dt_model.joblib"),
  "xgb": joblib.load("models/xgb_model.joblib")
}

@App.route("/", methods=["GET"])
def home():
  return jsonify({
    "message": "Welcome to Student Performance Final Prediction API",
    "endpoints": {
      "POST /predict?model=lr|rf|dt|xgb": {
        "expects_json": {
            # "Age": "int",
            # "Gender": "Male/Female",
            "Attendance": "float",
            "Assignments": "float",
            "Quiz": "float",
            "Midterm": "float",
            # "Final": "float"
        }
      }
    }
  })

@App.route("/predict", methods=["POST"])
def predict():
    
    # 1) choose model
    choice = (request.args.get("model") or "xgb").lower()        #haddi model la waayo rf qaado
    if choice not in MODELS:
        return jsonify({"error": "Unknown model Use model=lr, model=rf, model=dt or model=xgb"}), 400
    # return jsonify({"Choice": choice})
    model = MODELS[choice]
    
    
    # 2) read payload
    Data = request.get_json(silent=True) or {}
    Required = ["Attendance", "Assignments", "Quiz", "Midterm"]
    Missing = [k for k in Required if k not in Data]
    if Missing:
        return jsonify({"error": f"Please Fill Missing Fields {Missing}"}), 400    #qofka wuxu ka tagay u sheeg
    
    try:
       x_new, Total = prepare_features_from_raw(Data) 
       pred_label = float(model.predict(x_new)[0])           #so celiyaa Pass ama Fail
       prediction = "Pass" if pred_label == 1 else "Fail"

    except Exception as e:
        return jsonify({"error": f" failed to predict: {e}"}), 500
    return jsonify({
            "model": (
                "Logistic Regression" if choice == "lr"
                else "Random Forest" if choice == "rf"
                else "decision tree" if choice == "dt"
                else "XGBoost"
              ),
            "input":{
                # "Age": int(Data["Age"]),
                # "Gender": Data["Gender"], 
                "Attendance": float(Data["Attendance"]),
                "Assignments": float(Data["Assignments"]),
                "Quiz": float(Data["Quiz"]),
                "Midterm": float(Data["Midterm"]),
                

        },
        "Total_Score_Calculated": round(Total.iloc[0], 2),
        "prediction_result": prediction
      
        })

@App.route("/upload_predict", methods=["POST"])
def upload_predict():
    # 1) Hubi in fayl la soo galiyay
    if 'file' not in request.files:
        return jsonify({"error": "Fayl lama helin, fadlan soo geli fayl 'file' lagu magacaabay"}), 400
    
    file = request.files['file']
    
    # Hubi magaca faylka
    if file.filename == '':
        return jsonify({"error": "Fayl aan la dooran"}), 400
    
    # Hubi nooca faylka
    if not file.filename.endswith('.xlsx'):
        return jsonify({"error": "Fadlan soo geli fayl nooca XLSX (Excel) ah"}), 400

    # 2) Dooro model
    choice = (request.args.get("model") or "xgb").lower()
    if choice not in MODELS:
        return jsonify({"error": "Unknown model. Use model=lr, model=rf, model=dt or model=xgb"}), 400
    model = MODELS[choice]

    try:
        # 3) Akhriso faylka XLSX
        df_original = pd.read_excel(file)
        
        # Hubi tiirarka loo baahan yahay (columns)
        Required = ["Attendance", "Assignments", "Quiz", "Midterm"]
        Missing = [k for k in Required if k not in df_original.columns]
        if Missing:
            return jsonify({"error": f"Faylka wuxuu ka maqan yahay tiirarka (columns): {Missing}"}), 400
      
        X_new, Total_Scores = prepare_features_from_raw(df_original.copy()) 
        pred_labels = model.predict(X_new)
        
        # Ku dar natiijooyinka DataFrame-ka
        df_original['Total_Score'] = Total_Scores
        df_original['Label'] = pred_labels
        df_original['Result_predict'] = df_original['Label'].apply(
            lambda x: "Pass" if x == 1 else "Fail"
        )
     
        df_failed = df_original[df_original['Result_predict'] == 'Fail'].copy()
        df_failed = df_failed.drop(columns=['Label'], errors='ignore')
        

       
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df_failed.to_excel(writer, sheet_name='Student_Fail', index=False)
        writer.close()
        output.seek(0) # dib ugu noqo bilawga buffer-ka

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='Student_Fail_Predict.xlsx', # magaca faylka la soo dejinayo
            as_attachment=True
        )

    except Exception as e:
        return jsonify({"error": f"Waxaa dhacay khalad intii lagu jiray hawlgalka: {e}"}), 500

if __name__ == "__main__":
    App.run(host="0.0.0.0", port=8000, debug=True)  