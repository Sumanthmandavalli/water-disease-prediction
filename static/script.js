// Add water drop animation to cards
function createWaterDrop(card) {
    const drop = card.querySelector('.water-drop');
    const startAnimation = () => {
        drop.style.left = Math.random() * 100 + '%';
        drop.style.opacity = '0';
        drop.style.animation = 'none';
        drop.offsetHeight; // Trigger reflow
        drop.style.animation = 'dropFall 2s ease-in infinite';
    };
    setInterval(startAnimation, 2000);
}

// Initialize water drops for all cards
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    cards.forEach(createWaterDrop);
    
    // Add input animation handlers
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('focused');
            }
        });
    });
});

// Add ripple effect to predict button
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('predict-btn') || e.target.closest('.predict-btn')) {
        const button = e.target.classList.contains('predict-btn') ? e.target : e.target.closest('.predict-btn');
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        button.appendChild(ripple);

        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + 'px';
        
        const x = e.clientX - rect.left - size/2;
        const y = e.clientY - rect.top - size/2;
        
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        ripple.addEventListener('animationend', () => {
            ripple.remove();
        });
    }
});

// Disease prediction function with enhanced UI feedback
function predictDisease() {
    let patientName = document.getElementById("patient_name").value;
    let age = document.getElementById("age").value;
    let gender = document.getElementById("gender").value;
    let waterSource = document.getElementById("water_source").value;
    let specificContaminant = document.getElementById("specific_contaminant").value;
    let minChemical = document.getElementById("min_chemical").value;
    let maxChemical = document.getElementById("max_chemical").value;

    // Form validation with visual feedback
    const inputs = [
        { id: "patient_name", value: patientName },
        { id: "age", value: age },
        { id: "specific_contaminant", value: specificContaminant },
        { id: "min_chemical", value: minChemical },
        { id: "max_chemical", value: maxChemical }
    ];

    let isValid = true;
    inputs.forEach(input => {
        const element = document.getElementById(input.id);
        if (!input.value) {
            element.classList.add('error');
            isValid = false;
            // Add shake animation
            element.style.animation = 'shake 0.5s ease-in-out';
            element.addEventListener('animationend', () => {
                element.style.animation = '';
            });
        } else {
            element.classList.remove('error');
        }
    });

    if (!isValid) {
        return;
    }

    let inputData = {
        patient_name: patientName,
        age: age,
        gender: gender,
        water_source: waterSource,
        specific_contaminant: specificContaminant,
        min_chemical: minChemical,
        max_chemical: maxChemical
    };

    // Show loading state with animation
    const predictBtn = document.querySelector('.predict-btn');
    const btnSpan = predictBtn.querySelector('span');
    const originalText = btnSpan.textContent;
    predictBtn.disabled = true;
    btnSpan.innerHTML = '<div class="loader"></div> Analyzing...';

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(inputData)
    })
    .then(response => response.json())
    .then(data => {
        // Show results with fade-in animation
        const results = document.getElementById("results");
        results.style.display = 'block';
        results.style.opacity = '0';
        
        document.getElementById("result_name").innerText = data.patient_name;
        document.getElementById("result_age").innerText = data.age;
        document.getElementById("result_gender").innerText = data.gender;
        document.getElementById("result_source").innerText = data.water_source;
        document.getElementById("result_disease").innerText = data.predicted_disease;
        
        // Animate results appearance
        setTimeout(() => {
            results.style.opacity = '1';
            results.style.transform = 'translateY(0)';
        }, 100);
        
        // Smooth scroll to results
        results.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    })
    .catch(error => {
        console.error("Error:", error);
        // Show error message with animation
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        errorMsg.textContent = "An error occurred while processing your request.";
        document.querySelector('.analysis-form').appendChild(errorMsg);
        
        setTimeout(() => errorMsg.remove(), 5000);
    })
    .finally(() => {
        // Reset button state
        predictBtn.disabled = false;
        btnSpan.textContent = originalText;
    });
}

// Add some parallax effect to the background
document.addEventListener('mousemove', (e) => {
    const bubbles = document.querySelectorAll('.bubble');
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    
    bubbles.forEach(bubble => {
        const speed = parseFloat(bubble.getAttribute('data-speed') || 1);
        const moveX = (x * 20 * speed);
        const moveY = (y * 20 * speed);
        bubble.style.transform = `translate(${moveX}px, ${moveY}px)`;
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Retrieve last patient ID from localStorage or start from 1
    let lastPatientId = localStorage.getItem("lastPatientId") || 0;
    let newPatientId = parseInt(lastPatientId) + 1;

    // Set the new Patient ID
    document.getElementById("patient_id").value = "Patient " + newPatientId;

    // Store the new Patient ID for the next entry
    localStorage.setItem("lastPatientId", newPatientId);
});
document.addEventListener("DOMContentLoaded", function() {
    const tableRows = document.querySelectorAll("#predictionsTable tr");
    
    // Add fade-in effect for table rows
    tableRows.forEach((row, index) => {
        row.style.opacity = "0";
        setTimeout(() => {
            row.style.transition = "opacity 0.5s ease-in-out";
            row.style.opacity = "1";
        }, index * 200);
    });
});
document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_predictions")
        .then(response => {
            console.log("🔍 Fetching data... Status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("✅ Data received:", data);
            const tableBody = document.getElementById("predictionsTable");
            if (!tableBody) {
                console.error("❌ Table body element not found!");
                return;
            }

            tableBody.innerHTML = ""; // Clear old data

            if (data.length === 0) {
                tableBody.innerHTML = "<tr><td colspan='10' class='text-center'>No records found.</td></tr>";
                return;
            }

            data.forEach(prediction => {
                const row = `<tr>
                    <td>${prediction.id}</td>
                    <td>${prediction.patient_name}</td>
                    <td>${prediction.age}</td>
                    <td>${prediction.gender}</td>
                    <td>${prediction.water_source}</td>
                    <td>${prediction.specific_contaminant}</td>
                    <td>${prediction.min_chem}</td>
                    <td>${prediction.max_chem}</td>
                    <td>${prediction.chemical_diff}</td>
                    <td>${prediction.predicted_disease}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        })
        .catch(error => {
            console.error("❌ Error fetching predictions:", error);
            alert("Error loading data. Check the console for details.");
        });
});
