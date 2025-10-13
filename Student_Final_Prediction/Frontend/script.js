// API-link
const BASE_URL = 'http://127.0.0.1:8000';

// Waxaan isticmaalayaa 40 dhibcaha ugu badan: 5+10+10+20 = 45
const MAX_TOTAL_SCORE = 40;
const MAX_SCORE = 40;


// --- Function Single Student Prediction ---
document.getElementById('prediction-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = event.target;
    //waxaan ka soo qaadanayaa Select-ka (id="model-choice")
    const modelChoice = document.getElementById('model-choice').value; 
    const resultMessage = document.getElementById('result-message');
    const scoreDetails = document.getElementById('score-details');
    const predictButton = document.getElementById('predict-button');

    // Xogta laga soo qaaday formka
    const studentName = form['Name'].value;
    const courseName = form['Course'].value;

    const data = {
        // "Attendance", "Assignments", "Quiz", "Midterm" API-ga  baahan yahay oo kaliya
        Attendance: parseFloat(form['Attendance'].value),
        Assignments: parseFloat(form['Assignments'].value),
        Quiz: parseFloat(form['Quiz'].value),
        Midterm: parseFloat(form['Midterm'].value)
    };

    // UI in la sugo
    resultMessage.className = 'waiting';
    resultMessage.innerHTML = '<p>Xisaabinta Natiijada...</p>';
    scoreDetails.style.display = 'none';
    predictButton.disabled = true;

    // API Request
    fetch(`${BASE_URL}/predict?model=${modelChoice}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Error the Server.');
            });
        }
        return response.json();
    })
    .then(result => {
        const prediction = result.prediction_result;
        const totalScore = result.Total_Score_Calculated;
        const modelUsed = result.model;

        // Percentage
        const percentage = ((totalScore / MAX_SCORE) * 100).toFixed(2); // Ku wareeji 2 decimal
        
        
        // Feedback
        resultMessage.className = (prediction === 'Pass') ? 'pass' : 'fail';
        resultMessage.innerHTML = `<p>You will:  ${prediction}</p>`;
        
        // Faahfaahinta Dhibcaha
        document.getElementById('student-name').textContent = studentName;
        document.getElementById('course-name').textContent = courseName;  
        document.getElementById('total-score-percentage').textContent = `${percentage}% (${totalScore} / ${MAX_SCORE})`; 
        // Total Score
        document.getElementById('model-used').textContent = modelUsed;
        scoreDetails.style.display = 'block';

    })
    .catch(error => {
        console.error('Error:', error);
        resultMessage.className = 'fail';
        resultMessage.innerHTML = `<p>QALAD: ${error.message}</p>`;
        scoreDetails.style.display = 'none';
    })
    .finally(() => {
        predictButton.disabled = false;
    });
});


// --- Function Excel File Upload and Prediction ---
document.getElementById('excel-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    // Xogta
    const excelFile = document.getElementById('excel-file').files[0];
    const excelMessage = document.getElementById('excel-result-message');
    const excelButton = document.getElementById('excel-predict-button');
    // Isticmaal isla model-ka la doortay
    const modelChoice = document.getElementById('model-choice').value; 

    if (!excelFile) {
        excelMessage.innerHTML = `<p style="color:red; font-weight:bold;">Upload only Excel file (.xlsx).</p>`;
        return;
    }

    excelButton.disabled = true;
    excelMessage.innerHTML = `<p style="color:#007bff; font-weight:bold;">File was uploaded please wait until calculation finished, sug inta la xisaabinayo...</p>`;
    
    // U diyaari xogta qaab 'multipart/form-data' ah
    const formData = new FormData();
    formData.append('file', excelFile);

    // Kani wuxuu isticmaalayaa '/upload_predict' endpoint-ka aan ku darsannay server-ka Flask
    fetch(`${BASE_URL}/upload_predict?model=${modelChoice}`, { 
        method: 'POST',
        body: formData 
    })
    .then(response => {
        if (response.headers.get('content-type') === 'application/json') {
             // Haddii uu server-ku khalad soo celiyo oo uu JSON yahay
            return response.json().then(err => {
                throw new Error(err.error || 'Error Server to calculate in this file.');
            });
        }
        if (!response.ok) {
            throw new Error('Timeout Request. please check the file is correctly.');
        }
        // Wuxuu soo celinayaa fayl (blob)
        return response.blob(); 
    })
    .then(blob => {
        // Samee link si loo dejisto (Download) file-ka
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        // Magaca file-ka la soo dejinayo
        a.download = `Student_Fail_Final_prediction_List_${Date.now()}.xlsx`; 
        document.body.appendChild(a);
        a.click();
        a.remove();
        
        excelMessage.innerHTML = `<p style="color:green; font-weight:bold;">Result was finished successfully! Now you can download fail students Thanks!.</p>`;
    })
    .catch(error => {
        console.error('Batch Error:', error);
        excelMessage.innerHTML = `<p style="color:red; font-weight:bold;">Error the calculation: ${error.message}</p>`;
    })
    .finally(() => {
        excelButton.disabled = false;
    });
});