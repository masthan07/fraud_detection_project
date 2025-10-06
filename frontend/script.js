const API_URL = window.location.origin;

const form = document.getElementById('fraudForm');
const submitBtn = document.querySelector('.submit-btn');
const resultContainer = document.getElementById('result');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    submitBtn.classList.add('loading');
    resultContainer.classList.remove('show');
    
    await analyzeFraud();
});

async function analyzeFraud() {
    const formData = new FormData(form);
    
    const data = {
        amount: formData.get('amount'),
        cardType: formData.get('cardType'),
        cardLast4: formData.get('cardLast4'),
        deviceType: formData.get('deviceType'),
        country: formData.get('country'),
        zipCode: formData.get('zipCode'),
        email: formData.get('email')
    };
    
    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Prediction failed');
        }
        
        const result = await response.json();
        displayResult(result, data.amount);
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Failed to analyze transaction: ${error.message}`);
        submitBtn.classList.remove('loading');
    }
}

function displayResult(result, amount) {
    submitBtn.classList.remove('loading');
    
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const transactionId = document.getElementById('transactionId');
    const displayAmount = document.getElementById('displayAmount');
    const riskScore = document.getElementById('riskScore');
    const confidence = document.getElementById('confidence');
    const confidenceFill = document.getElementById('confidenceFill');
    
    transactionId.textContent = result.transaction_id;
    displayAmount.textContent = `$${parseFloat(amount).toFixed(2)}`;
    riskScore.textContent = result.risk_score.toFixed(1) + '%';
    confidence.textContent = result.confidence.toFixed(1) + '%';
    
    if (result.is_fraud) {
        resultContainer.className = 'result-container fraud show';
        resultIcon.textContent = '⚠️';
        resultTitle.textContent = 'FRAUD DETECTED';
        resultMessage.textContent = 'This transaction has been flagged as potentially fraudulent. Please verify the details carefully.';
    } else {
        resultContainer.className = 'result-container legitimate show';
        resultIcon.textContent = '✅';
        resultTitle.textContent = 'TRANSACTION APPROVED';
        resultMessage.textContent = 'This transaction appears legitimate and safe to proceed.';
    }
    
    setTimeout(() => {
        confidenceFill.style.width = result.confidence.toFixed(1) + '%';
        confidenceFill.textContent = result.confidence.toFixed(1) + '%';
    }, 100);
}

// Real-time validation
document.getElementById('cardLast4').addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '');
});

document.getElementById('amount').addEventListener('input', (e) => {
    if (e.target.value < 0) e.target.value = 0;
});