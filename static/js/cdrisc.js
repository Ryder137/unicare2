// CD-RISC 10 Assessment Questions
const cdriscQuestions = [
    "I am able to adapt to change.",
    "I can deal with whatever comes my way.",
    "I try to see the humorous side of things when I face problems.",
    "I can achieve my goals, despite difficulties.",
    "I can remain focused under pressure.",
    "I don't give up easily when I face challenges.",
    "I believe I can handle unpleasant or painful feelings.",
    "I tend to bounce back after difficult situations.",
    "I can think clearly under stress.",
    "I take control of my life during tough times."
];

// CD-RISC response options
const cdriscOptions = [
    { value: 0, label: 'Not true at all' },
    { value: 1, label: 'Rarely true' },
    { value: 2, label: 'Sometimes true' },
    { value: 3, label: 'Often true' },
    { value: 4, label: 'True nearly all the time' }
];

let cdriscResponses = new Array(cdriscQuestions.length).fill(null);
let currentCdriscQuestion = 0;

// Initialize CD-RISC Assessment
function initCdriscAssessment() {
    const container = document.getElementById('cdriscAssessment');
    if (!container) return;
    
    // Set up payment button click handler
    const payNowBtn = document.getElementById('payNowBtn');
    if (payNowBtn) {
        payNowBtn.addEventListener('click', handlePayment);
    }
    
    // Check if we should show results (for demo purposes)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('showResults') === 'true') {
        showCdriscQuestion(0);
    }
}

// Handle payment button click
function handlePayment() {
    const paymentSection = document.getElementById('paymentRequired');
    const loadingState = document.getElementById('loadingState');
    const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked');
    
    if (!paymentSection || !loadingState || !paymentMethod) return;
    
    // Show loading state
    paymentSection.style.display = 'none';
    loadingState.style.display = 'block';
    
    // Simulate payment processing (2 seconds)
    setTimeout(() => {
        // Hide loading state
        loadingState.style.display = 'none';
        
        // Generate and show receipt
        showReceipt(paymentMethod.value);
    }, 2000);
}

// Show receipt after successful payment
function showReceipt(paymentMethod) {
    const receiptContainer = document.getElementById('receiptContainer');
    const receiptNumber = document.getElementById('receiptNumber');
    const receiptDate = document.getElementById('receiptDate');
    const receiptDateTime = document.getElementById('receiptDateTime');
    const receiptPaymentMethod = document.getElementById('receiptPaymentMethod');
    const printReceiptBtn = document.getElementById('printReceiptBtn');
    const viewResultsBtn = document.getElementById('viewResultsBtn');
    
    if (!receiptContainer || !receiptNumber || !receiptDate || !receiptDateTime || !receiptPaymentMethod || !printReceiptBtn || !viewResultsBtn) return;
    
    // Generate receipt details
    const now = new Date();
    const receiptId = 'RC-' + Math.floor(100000 + Math.random() * 900000);
    const formattedDate = now.toLocaleDateString('en-PH', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    const formattedDateTime = now.toLocaleString('en-PH', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    // Payment method display names
    const paymentMethods = {
        'gcash': 'GCash',
        'paymaya': 'PayMaya',
        'card': 'Credit/Debit Card'
    };
    
    // Update receipt content
    receiptNumber.textContent = receiptId;
    receiptDate.textContent = formattedDate;
    receiptDateTime.textContent = formattedDateTime;
    receiptPaymentMethod.textContent = paymentMethods[paymentMethod] || paymentMethod;
    
    // Set up print receipt button
    printReceiptBtn.addEventListener('click', function() {
        const receipt = document.getElementById('receipt');
        if (!receipt) return;
        
        // Create a new window for printing
        const printWindow = window.open('', '_blank');
        
        // Get the receipt HTML and add print styles
        const receiptHTML = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>UniCare Receipt</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .receipt { max-width: 300px; margin: 0 auto; }
                    .text-center { text-align: center; }
                    .text-muted { color: #6c757d; }
                    .fw-bold { font-weight: bold; }
                    .border-top { border-top: 1px solid #dee2e6; }
                    .mt-4 { margin-top: 1.5rem; }
                    .pt-3 { padding-top: 1rem; }
                    .small { font-size: 0.875em; }
                    .mb-0 { margin-bottom: 0; }
                    .mb-4 { margin-bottom: 1.5rem; }
                    .my-3 { margin-top: 1rem; margin-bottom: 1rem; }
                </style>
            </head>
            <body>
                <div class="receipt">
                    <div class="text-center mb-4">
                        <h4 class="mb-1">UniCare</h4>
                        <p class="text-muted mb-0">Official Receipt</p>
                        <p class="text-muted small">${formattedDate}</p>
                    </div>
                    
                    <div class="mb-2">
                        <div class="d-flex justify-content-between">
                            <span>Receipt #:</span>
                            <span>${receiptId}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Date:</span>
                            <span>${formattedDateTime}</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>Payment Method:</span>
                            <span>${paymentMethods[paymentMethod] || paymentMethod}</span>
                        </div>
                    </div>
                    
                    <hr class="my-3">
                    
                    <div class="mb-2">
                        <div class="d-flex justify-content-between fw-bold">
                            <span>Item</span>
                            <span>Amount</span>
                        </div>
                        <div class="d-flex justify-content-between">
                            <span>CD-RISC 10 Assessment</span>
                            <span>₱5.00</span>
                        </div>
                    </div>
                    
                    <hr class="my-2">
                    
                    <div class="d-flex justify-content-between fw-bold">
                        <span>Total Paid:</span>
                        <span>₱5.00</span>
                    </div>
                    
                    <div class="mt-4 pt-3 border-top text-center">
                        <p class="small text-muted mb-0">This is an official receipt for your records.</p>
                        <p class="small text-muted">Thank you for using UniCare services.</p>
                    </div>
                </div>
                
                <script>
                    // Auto-print when the window loads
                    window.onload = function() {
                        setTimeout(function() {
                            window.print();
                            window.onafterprint = function() {
                                window.close();
                            };
                        }, 500);
                    };
                </script>
            </body>
            </html>
        `;
        
        // Write the receipt HTML to the new window
        printWindow.document.open();
        printWindow.document.write(receiptHTML);
        printWindow.document.close();
    });
    
    // Set up view results button
    viewResultsBtn.addEventListener('click', function() {
        receiptContainer.style.display = 'none';
        showCdriscQuestion(0);
        
        // Update URL to show results (for demo purposes)
        window.history.pushState({}, '', `${window.location.pathname}?showResults=true`);
    });
    
    // Show the receipt container
    receiptContainer.style.display = 'block';
    
    // Scroll to the receipt
    receiptContainer.scrollIntoView({ behavior: 'smooth' });
}

// Show CD-RISC question
function showCdriscQuestion(index) {
    const container = document.getElementById('cdriscAssessment');
    if (!container) return;
    
    // Calculate progress
    const progress = Math.round(((index) / cdriscQuestions.length) * 100);
    
    // Create question HTML
    container.innerHTML = `
        <div class="assessment-progress mb-3">
            <div class="progress" style="height: 6px;">
                <div class="progress-bar" role="progressbar" 
                     style="width: ${progress}%" 
                     aria-valuenow="${progress}" 
                     aria-valuemin="0" 
                     aria-valuemax="100"></div>
            </div>
            <div class="text-end small text-muted">
                Question ${index + 1} of ${cdriscQuestions.length}
            </div>
        </div>
        
        <div class="question-container">
            <h5 class="mb-4">${cdriscQuestions[index]}</h5>
            <div class="response-options">
                ${cdriscOptions.map(option => `
                    <div class="form-check py-2">
                        <input class="form-check-input" 
                               type="radio" 
                               name="cdriscResponse" 
                               id="cdriscOption${option.value}" 
                               value="${option.value}"
                               ${cdriscResponses[index] === option.value ? 'checked' : ''}
                               onchange="saveCdriscResponse(${index}, ${option.value})">
                        <label class="form-check-label ms-2" for="cdriscOption${option.value}">
                            ${option.label}
                        </label>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="d-flex justify-content-between mt-4">
            <button type="button" 
                    class="btn btn-outline-secondary" 
                    ${index === 0 ? 'disabled' : ''}
                    onclick="showCdriscQuestion(${index - 1})">
                Previous
            </button>
            ${index < cdriscQuestions.length - 1 ? `
                <button type="button" 
                        class="btn btn-primary" 
                        ${cdriscResponses[index] === null ? 'disabled' : ''}
                        onclick="showCdriscQuestion(${index + 1})">
                    Next
                </button>
            ` : `
                <button type="button" 
                        class="btn btn-success" 
                        ${cdriscResponses[index] === null ? 'disabled' : ''}
                        onclick="submitCdriscAssessment()">
                    Submit Assessment
                </button>
            `}
        </div>
    `;
}

// Save CD-RISC response
function saveCdriscResponse(questionIndex, value) {
    cdriscResponses[questionIndex] = parseInt(value);
    
    // Enable next/submit button
    const nextButton = document.querySelector('button.btn-primary, button.btn-success');
    if (nextButton) {
        nextButton.disabled = false;
    }
}

// Submit CD-RISC assessment
async function submitCdriscAssessment() {
    try {
        // Check if all questions are answered
        if (cdriscResponses.some(response => response === null)) {
            alert('Please answer all questions before submitting.');
            return;
        }
        
        // Calculate total score
        const totalScore = cdriscResponses.reduce((sum, response) => sum + response, 0);
        
        // Send data to server
        const response = await fetch('/assessments/submit_cdrisc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
            },
            body: JSON.stringify({
                responses: cdriscResponses,
                total_score: totalScore
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit assessment');
        }
        
        const result = await response.json();
        
        // Show results
        showCdriscResults(result);
        
    } catch (error) {
        console.error('Error submitting assessment:', error);
        alert('An error occurred while submitting your assessment. Please try again.');
    }
}

// Show CD-RISC results
function showCdriscResults(data) {
    const container = document.getElementById('cdriscAssessment');
    if (!container) return;
    
    // Calculate total score
    const totalScore = data.total_score;
    
    // Detailed score interpretation
    const scoreInterpretation = {
        range: [0, 40],
        levels: [
            {
                min: 0,
                max: 19,
                level: 'Very Low Resilience',
                class: 'danger',
                description: 'You may find it very challenging to cope with stress and recover from adversity. Consider seeking support to build your resilience.',
                recommendations: [
                    'Seek support from mental health professionals',
                    'Develop a strong support system',
                    'Practice self-care and stress reduction techniques',
                    'Start with small, manageable challenges',
                    'Learn and practice emotional regulation skills'
                ]
            },
            {
                min: 20,
                max: 24,
                level: 'Low Resilience',
                class: 'warning',
                description: 'You may find some challenges in coping with stress and bouncing back from difficulties.',
                recommendations: [
                    'Practice mindfulness and relaxation techniques',
                    'Break problems into smaller, manageable parts',
                    'Build a strong support network',
                    'Develop problem-solving skills',
                    'Consider professional counseling if needed'
                ]
            },
            {
                min: 25,
                max: 28,
                level: 'Moderate Resilience',
                class: 'info',
                description: 'You have a fair level of resilience but may benefit from strengthening your coping strategies.',
                recommendations: [
                    'Practice stress management techniques',
                    'Focus on building positive relationships',
                    'Set realistic goals and celebrate small wins',
                    'Develop a growth mindset',
                    'Practice gratitude and positive thinking'
                ]
            },
            {
                min: 29,
                max: 31,
                level: 'High Resilience',
                class: 'success',
                description: 'You demonstrate good resilience and generally cope well with life\'s challenges.',
                recommendations: [
                    'Continue practicing your coping strategies',
                    'Share your resilience skills with others',
                    'Maintain healthy habits and routines',
                    'Keep building your support network',
                    'Challenge yourself with new experiences'
                ]
            },
            {
                min: 32,
                max: 40,
                level: 'Very High Resilience',
                class: 'success',
                description: 'You have excellent resilience skills and adapt well to change and adversity.',
                recommendations: [
                    'Mentor others in developing resilience',
                    'Continue practicing self-care',
                    'Stay connected with your support network',
                    'Keep challenging yourself with new goals',
                    'Consider volunteering to help others build resilience'
                ]
            }
        ]
    };

    // Find the appropriate level based on score
    const level = scoreInterpretation.levels.find(l => 
        totalScore >= l.min && totalScore <= l.max
    ) || scoreInterpretation.levels[0];

    // Calculate score percentage for visualization
    const scorePercentage = Math.round((totalScore / scoreInterpretation.range[1]) * 100);
    const scoreWidth = Math.min(100, Math.max(5, scorePercentage));

    // Create HTML for results
    container.innerHTML = `
        <div class="cdrisc-results">
            <!-- Score Summary -->
            <div class="card mb-4 border-0 shadow-sm">
                <div class="card-body text-center p-4">
                    <h2 class="mb-3">Your Resilience Score</h2>
                    <div class="score-display display-1 fw-bold text-${level.class} mb-3">
                        ${totalScore}<small class="text-muted">/40</small>
                    </div>
                    
                    <div class="progress mb-4" style="height: 24px; border-radius: 12px; overflow: hidden;">
                        <div class="progress-bar bg-${level.class} progress-bar-striped progress-bar-animated" 
                             role="progressbar" 
                             style="width: ${scoreWidth}%" 
                             aria-valuenow="${totalScore}" 
                             aria-valuemin="${scoreInterpretation.range[0]}" 
                             aria-valuemax="${scoreInterpretation.range[1]}">
                            ${scorePercentage}%
                        </div>
                    </div>
                    
                    <div class="alert alert-${level.class} text-start">
                        <h4 class="alert-heading">${level.level}</h4>
                        <p class="mb-0">${level.description}</p>
                    </div>
                </div>
            </div>
            
            <!-- Detailed Breakdown -->
            <div class="row g-4 mb-4">
                <!-- Score Distribution -->
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <h5 class="mb-0">Score Distribution</h5>
                        </div>
                        <div class="card-body">
                            <div class="score-distribution">
                                ${scoreInterpretation.levels.map(l => {
                                    const isCurrent = level === l;
                                    const range = l.min === l.max ? l.min : `${l.min}-${l.max}`;
                                    const isInRange = totalScore >= l.min && totalScore <= l.max;
                                    return `
                                        <div class="d-flex align-items-center mb-2">
                                            <div class="me-2 text-nowrap" style="width: 80px;">
                                                <span class="badge bg-${l.class} w-100">${range}</span>
                                            </div>
                                            <div class="progress flex-grow-1" style="height: 24px;">
                                                <div class="progress-bar bg-${l.class} ${isInRange ? 'progress-bar-striped progress-bar-animated' : ''}" 
                                                     style="width: ${(l.max / scoreInterpretation.range[1]) * 100}%;">
                                                    ${l.level}
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Recommendations -->
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header bg-light">
                            <h5 class="mb-0">Recommendations</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-group list-group-flush">
                                ${level.recommendations.map(rec => `
                                    <li class="list-group-item d-flex align-items-center">
                                        <i class="bi bi-check-circle-fill text-${level.class} me-2"></i>
                                        <span>${rec}</span>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Detailed Responses -->
            <div class="card mb-4">
                <div class="card-header bg-light d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Your Responses</h5>
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#responseDetails">
                        Toggle Details
                    </button>
                </div>
                <div class="collapse show" id="responseDetails">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>#</th>
                                    <th>Question</th>
                                    <th>Your Response</th>
                                    <th>Score</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${cdriscQuestions.map((q, i) => {
                                    const qNum = i + 1;
                                    const response = data[`q${qNum}`];
                                    const option = cdriscOptions.find(opt => opt.value === response);
                                    const scoreClass = response >= 3 ? 'table-success' : response <= 1 ? 'table-warning' : '';
                                    return `
                                        <tr class="${scoreClass}">
                                            <td>${qNum}</td>
                                            <td>${q}</td>
                                            <td>${option ? option.label : 'Not answered'}</td>
                                            <td class="text-end fw-bold">${response !== null ? response : 'N/A'}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                            <tfoot class="table-light">
                                <tr>
                                    <th colspan="3" class="text-end">Total Score:</th>
                                    <th class="text-end">${totalScore}/40</th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="d-grid gap-3 d-md-flex justify-content-md-center">
                <button class="btn btn-outline-primary btn-lg px-4 me-md-2" onclick="startCdriscAssessment()">
                    <i class="bi bi-arrow-repeat me-2"></i>Retake Assessment
                </button>
                <a href="/dashboard" class="btn btn-primary btn-lg px-4">
                    <i class="bi bi-house-door me-2"></i>Return to Dashboard
                </a>
            </div>
            
            <!-- Score Interpretation Guide -->
            <div class="card mt-4">
                <div class="card-header bg-light">
                    <h5 class="mb-0">Understanding Your Score</h5>
                </div>
                <div class="card-body">
                    <p>The CD-RISC-10 measures your ability to cope with stress and adversity. Higher scores indicate greater resilience.</p>
                    <div class="table-responsive">
                        <table class="table table-bordered">
                            <thead class="table-light">
                                <tr>
                                    <th>Score Range</th>
                                    <th>Resilience Level</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${scoreInterpretation.levels.map(l => `
                                    <tr class="${level === l ? 'table-' + l.class + ' fw-bold' : ''}">
                                        <td>${l.min === l.max ? l.min : `${l.min}-${l.max}`}</td>
                                        <td>${l.level}</td>
                                        <td>${l.description}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            .cdrisc-results .score-display {
                font-size: 4.5rem;
                line-height: 1;
            }
            .cdrisc-results .progress {
                border-radius: 10px;
                overflow: hidden;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
            }
            .cdrisc-results .progress-bar {
                font-weight: 600;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.85rem;
            }
            .cdrisc-results .score-distribution .progress {
                height: 24px;
                border-radius: 12px;
                overflow: hidden;
            }
            .cdrisc-results .table th {
                white-space: nowrap;
            }
            .cdrisc-results .table td, 
            .cdrisc-results .table th {
                vertical-align: middle;
            }
        </style>
    `;
}

// Track if CD-RISC assessment is initialized
let cdriscInitialized = false;

// Initialize when the tab is shown
document.addEventListener('DOMContentLoaded', () => {
    // Initialize when the CD-RISC tab is shown
    const cdriscTab = document.getElementById('cdrisc-tab');
    if (cdriscTab) {
        cdriscTab.addEventListener('shown.bs.tab', function (e) {
            if (!cdriscInitialized) {
                loadCdriscResults();
                cdriscInitialized = true;
            }
        });
    }
    
    // Load DASS results if that tab is active by default
    if (document.querySelector('#cdrisc-tab-pane.show.active')) {
        loadCdriscResults();
        cdriscInitialized = true;
    }
});

// Function to load CD-RISC results
function loadCdriscResults() {
    fetch("/assessments/latest_cdrisc")
        .then(response => {
            if (!response.ok) {
                throw new Error('No assessment data');
            }
            return response.json();
        })
        .then(data => {
            updateCdriscResultsUI(data);
        })
        .catch(error => {
            showCdriscStartScreen();
        });
}

// Show start screen for CD-RISC assessment
function showCdriscStartScreen() {
    const container = document.getElementById('cdriscResults');
    if (!container) return;
    
    container.innerHTML = `
        <div class="text-center py-4">
            <div class="mb-4">
                <i class="bi bi-clipboard2-pulse text-primary" style="font-size: 3rem;"></i>
            </div>
            <h4>Resilience Assessment (CD-RISC 10)</h4>
            <p class="text-muted mb-4">This assessment measures your ability to cope with stress and bounce back from adversity.</p>
            <button class="btn btn-primary" onclick="startCdriscAssessment()">
                Start Assessment
            </button>
        </div>
    `;
}

// Start the CD-RISC assessment
function startCdriscAssessment() {
    const container = document.getElementById('cdriscAssessment');
    const resultsContainer = document.getElementById('cdriscResults');
    
    if (container && resultsContainer) {
        resultsContainer.style.display = 'none';
        container.style.display = 'block';
        initCdriscAssessment();
    }
}

// Update the UI with CD-RISC results
function updateCdriscResultsUI(data) {
    const container = document.getElementById('cdriscResults');
    if (!container) return;
    
    // Format the assessment date
    const assessmentDate = new Date(data.assessment_date);
    const formattedDate = assessmentDate.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
    
    // Interpret the score
    let interpretation = '';
    if (data.total_score >= 32) {
        interpretation = 'Very High Resilience';
    } else if (data.total_score >= 29) {
        interpretation = 'High Resilience';
    } else if (data.total_score >= 25) {
        interpretation = 'Average Resilience';
    } else if (data.total_score >= 20) {
        interpretation = 'Low Resilience';
    } else {
        interpretation = 'Very Low Resilience';
    }
    
    container.innerHTML = `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="card-title mb-0">Your Latest Assessment</h5>
                    <span class="badge bg-primary rounded-pill">${data.total_score}/40</span>
                </div>
                
                <div class="progress mb-3" style="height: 10px;">
                    <div class="progress-bar bg-primary" 
                         role="progressbar" 
                         style="width: ${(data.total_score / 40) * 100}%" 
                         aria-valuenow="${data.total_score}" 
                         aria-valuemin="0" 
                         aria-valuemax="40">
                    </div>
                </div>
                
                <div class="d-flex justify-content-between mb-3">
                    <div>
                        <h6 class="mb-1">Resilience Level</h6>
                        <p class="mb-0 text-muted">${interpretation}</p>
                    </div>
                    <div class="text-end">
                        <h6 class="mb-1">Date Taken</h6>
                        <p class="mb-0 text-muted">${formattedDate}</p>
                    </div>
                </div>
                
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-primary" onclick="startCdriscAssessment()">
                        <i class="bi bi-arrow-repeat me-2"></i>Retake Assessment
                    </button>
                </div>
            </div>
        </div>
    `;
}
