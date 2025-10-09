// Hubi in API-gaagu ku shaqaynayo http://127.0.0.1:8000 ama isbeddel ku samee URL-kan
const BASE_URL = 'http://127.0.0.1:8000';
const MAX_TOTAL_SCORE = 40; // 5 (Attendance) + 10 (Assignments) + 10 (Quiz) + 20 (Midterm) = 45. 

// Waxaan isticmaalayaa 45 dhibcaha ugu badan: 5+10+10+20 = 45 (waxaan u maleeyay inaad Quiz max 10 ka dhigtay form-ka)
const MAX_SCORE = 40;


// --- Function for Single Student Prediction ---
document.getElementById('prediction-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = event.target;
    // Model Choice waxaan ka soo qaadanayaa Select-ka (id="model-choice") ee form-ka hore ku jira
    const modelChoice = document.getElementById('model-choice').value; 
    const resultMessage = document.getElementById('result-message');
    const scoreDetails = document.getElementById('score-details');
    const predictButton = document.getElementById('predict-button');

    // Xogta laga soo qaaday formka
    const studentName = form['Name'].value;
    const courseName = form['Course'].value;

    const data = {
        // Halkan waxaan ka saarayaa "Age" iyo "Gender" maxaa yeelay API-gaaga wuxuu sheegay inuu u baahan yahay oo kaliya
        // "Attendance", "Assignments", "Quiz", "Midterm"
        Attendance: parseFloat(form['Attendance'].value),
        Assignments: parseFloat(form['Assignments'].value),
        Quiz: parseFloat(form['Quiz'].value),
        Midterm: parseFloat(form['Midterm'].value)
    };

    // U diyaari UI in la sugo
    resultMessage.className = 'waiting';
    resultMessage.innerHTML = '<p>Xisaabinta Natiijada...</p>';
    scoreDetails.style.display = 'none';
    predictButton.disabled = true;

    // Samee API Request (FETCH)
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
                throw new Error(err.error || 'Server-ka wax baa ka qaldamay.');
            });
        }
        return response.json();
    })
    .then(result => {
        const prediction = result.prediction_result;
        const totalScore = result.Total_Score_Calculated;
        const modelUsed = result.model;

        // Xisaabinta Percentage-ka
        const percentage = ((totalScore / MAX_SCORE) * 100).toFixed(2); // Ku wareeji 2 decimal
        
        
        // Visual Feedback (Midabka)
        resultMessage.className = (prediction === 'Pass') ? 'pass' : 'fail';
        resultMessage.innerHTML = `<p>You will:  ${prediction}</p>`;
        
        // Soo bandhig Faahfaahinta Dhibcaha oo ay ku jiraan percentage-ka
        document.getElementById('student-name').textContent = studentName;
        document.getElementById('course-name').textContent = courseName;  
        document.getElementById('total-score-percentage').textContent = `${percentage}% (${totalScore} / ${MAX_SCORE})`; // Ku dar Total Score as well
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


// --- Function for Excel File Upload and Prediction (QAYBTA CUSUB) ---
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
                throw new Error(err.error || 'Server-ka wax baa ka qaldamay xisaabinta file-ka.');
            });
        }
        if (!response.ok) {
            throw new Error('Codsigu wuu dhacay. Hubi in server-ku socdo oo file-ku uu sax yahay.');
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
        
        excelMessage.innerHTML = `<p style="color:green; font-weight:bold;">Result was finished successfully! now you can download fail students Thanks!.</p>`;
    })
    .catch(error => {
        console.error('Batch Error:', error);
        excelMessage.innerHTML = `<p style="color:red; font-weight:bold;">Qalad ka dhacay xisaabinta: ${error.message}</p>`;
    })
    .finally(() => {
        excelButton.disabled = false;
    });
});