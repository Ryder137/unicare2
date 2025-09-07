// DASS-21 Assessment Questions with categories
const dassQuestions = [
    {
        id: 1,
        text: "I found it hard to wind down",
        category: "Stress"
    },
    {
        id: 2,
        text: "I was aware of dryness of my mouth",
        category: "Anxiety"
    },
    {
        id: 3,
        text: "I couldn't seem to experience any positive feeling at all",
        category: "Depression"
    },
    {
        id: 4,
        text: "I experienced breathing difficulty",
        category: "Anxiety"
    },
    {
        id: 5,
        text: "I found it difficult to work up the initiative to do things",
        category: "Depression"
    },
    {
        id: 6,
        text: "I tended to over-react to situations",
        category: "Stress"
    },
    {
        id: 7,
        text: "I experienced trembling",
        category: "Anxiety"
    },
    {
        id: 8,
        text: "I felt that I was using a lot of nervous energy",
        category: "Anxiety"
    },
    {
        id: 9,
        text: "I was worried about situations in which I might panic",
        category: "Anxiety"
    },
    {
        id: 10,
        text: "I felt that I had nothing to look forward to",
        category: "Depression"
    },
    {
        id: 11,
        text: "I found myself getting agitated",
        category: "Stress"
    },
    {
        id: 12,
        text: "I found it difficult to relax",
        category: "Stress"
    },
    {
        id: 13,
        text: "I felt down-hearted and blue",
        category: "Depression"
    },
    {
        id: 14,
        text: "I was intolerant of anything that kept me from getting on with what I was doing",
        category: "Stress"
    },
    {
        id: 15,
        text: "I felt I was close to panic",
        category: "Anxiety"
    },
    {
        id: 16,
        text: "I was unable to become enthusiastic about anything",
        category: "Depression"
    },
    {
        id: 17,
        text: "I felt I wasn't worth much as a person",
        category: "Depression"
    },
    {
        id: 18,
        text: "I felt that I was rather touchy",
        category: "Stress"
    },
    {
        id: 19,
        text: "I was aware of the action of my heart in the absence of physical exertion",
        category: "Anxiety"
    },
    {
        id: 20,
        text: "I felt scared without any good reason",
        category: "Anxiety"
    },
    {
        id: 21,
        text: "I felt that life was meaningless",
        category: "Depression"
    }
];

// Response options for each question
const responseOptions = [
    { value: 0, label: "Did not apply to me at all" },
    { value: 1, label: "Applied to me to some degree, or some of the time" },
    { value: 2, label: "Applied to me to a considerable degree, or a good part of time" },
    { value: 3, label: "Applied to me very much, or most of the time" }
];

// DASS-21 scoring
function calculateDassScores(responses) {
    // Reverse score items: 2, 4, 6, 7, 8, 10, 12, 13, 14, 16, 17, 19, 20, 21
    const reverseItems = [1, 3, 5, 6, 7, 9, 11, 12, 13, 15, 16, 18, 19, 20]; // 0-indexed
    
    const processedResponses = responses.map((response, index) => {
        return reverseItems.includes(index) ? 3 - response : response;
    });
    
    // Calculate subscale scores (0-21)
    const depression = processedResponses.slice(0, 7).reduce((a, b) => a + b, 0) * 2;
    const anxiety = processedResponses.slice(7, 14).reduce((a, b) => a + b, 0) * 2;
    const stress = processedResponses.slice(14, 21).reduce((a, b) => a + b, 0) * 2;
    
    return { depression, anxiety, stress };
}

// Severity levels
function getSeverity(score, type) {
    const cutoffs = {
        depression: [10, 14, 21, 28],
        anxiety: [8, 10, 15, 20],
        stress: [15, 19, 26, 34]
    };
    
    const [mild, moderate, severe, extreme] = cutoffs[type];
    
    if (score < mild) return { level: 'Normal', color: '#4CAF50' };
    if (score < moderate) return { level: 'Mild', color: '#8BC34A' };
    if (score < severe) return { level: 'Moderate', color: '#FFC107' };
    if (score < extreme) return { level: 'Severe', color: '#FF9800' };
    return { level: 'Extremely Severe', color: '#F44336' };
}

// Recommendations based on DASS-21 results
const recommendations = {
    depression: [
        'Consider talking to a mental health professional',
        'Try to maintain a regular sleep schedule',
        'Engage in physical activity, even just a short walk',
        'Spend time with supportive friends or family',
        'Practice gratitude journaling'
    ],
    anxiety: [
        'Practice deep breathing exercises',
        'Try progressive muscle relaxation',
        'Limit caffeine and alcohol intake',
        'Practice mindfulness meditation',
        'Challenge negative thoughts with evidence'
    ],
    stress: [
        'Take regular breaks throughout the day',
        'Practice time management techniques',
        'Engage in relaxing activities like yoga or reading',
        'Ensure you\'re getting enough sleep',
        'Learn to say no to additional commitments'
    ]
};

// Initialize assessment with one question at a time
let currentQuestionIndex = 0;
let userResponses = new Array(dassQuestions.length).fill(null);

function initAssessment() {
    const container = document.getElementById('dassAssessment');
    if (!container) return;
    
    // Show the first question
    showQuestion(0);
}

function showQuestion(index) {
    const container = document.getElementById('dassAssessment');
    const question = dassQuestions[index];
    
    // Calculate progress
    const progress = ((index) / dassQuestions.length) * 100;
    
    // Create question card
    container.innerHTML = `
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span class="text-muted">Question ${index + 1} of ${dassQuestions.length}</span>
                    </div>
                    <div class="progress" style="width: 100px; height: 8px;">
                        <div class="progress-bar" role="progressbar" style="width: ${progress}%" 
                             aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <h5 class="card-title mb-4">${question.text}</h5>
                
                <div class="response-options">
                    ${responseOptions.map(option => `
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="radio" 
                                   name="response" 
                                   id="option-${option.value}" 
                                   value="${option.value}"
                                   ${userResponses[index] === option.value ? 'checked' : ''}>
                            <label class="form-check-label" for="option-${option.value}">
                                ${option.label}
                            </label>
                        </div>
                    `).join('')}
                </div>
                
                <div class="d-flex justify-content-between mt-4">
                    <button type="button" class="btn btn-outline-secondary" 
                            id="prevBtn" ${index === 0 ? 'disabled' : ''}>
                        <i class="bi bi-chevron-left"></i> Previous
                    </button>
                    
                    ${index < dassQuestions.length - 1 ? `
                        <button type="button" class="btn btn-primary" id="nextBtn">
                            Next <i class="bi bi-chevron-right"></i>
                        </button>
                    ` : `
                        <button type="button" class="btn btn-success" id="submitBtn">
                            <i class="bi bi-check-circle"></i> Submit Assessment
                        </button>
                    `}
                </div>
            </div>
        </div>
    `;
    
    // Add event listeners
    document.getElementById('prevBtn')?.addEventListener('click', () => {
        saveResponse(index);
        showQuestion(index - 1);
    });
    
    const nextBtn = document.getElementById('nextBtn');
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (saveResponse(index)) {
                showQuestion(index + 1);
            } else {
                alert('Please select an option before continuing.');
            }
        });
    }
    
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
            if (saveResponse(index)) {
                submitAssessment();
            } else {
                alert('Please select an option before submitting.');
            }
        });
    }
    
    // Update current question index
    currentQuestionIndex = index;
}

function saveResponse(index) {
    const selectedOption = document.querySelector('input[name="response"]:checked');
    if (selectedOption) {
        userResponses[index] = parseInt(selectedOption.value);
        return true;
    }
    return false;
}

async function submitAssessment() {
    // Check if all questions are answered
    const unanswered = userResponses.findIndex(response => response === null || response === undefined);
    if (unanswered !== -1) {
        alert('Please answer all questions before submitting.');
        showQuestion(unanswered); // Go to first unanswered question
        return;
    }

    // Calculate DASS scores
    const depressionItems = [2, 4, 6, 7, 9, 12, 13, 16, 17, 18, 20];
    const anxietyItems = [0, 1, 6, 8, 10, 11, 12, 14, 16, 17, 19];
    const stressItems = [3, 5, 7, 8, 9, 10, 11, 13, 14, 15, 18];
    
    // Calculate raw scores (sum of responses for each scale)
    let depression = 0;
    let anxiety = 0;
    let stress = 0;
    
    userResponses.forEach((response, index) => {
        // For DASS-21, we multiply by 2 to get comparable scores to DASS-42
        const score = response * 2;
        
        // Check which scale this question belongs to (1-based index)
        const questionNum = index + 1;
        if (depressionItems.includes(questionNum)) depression += score;
        if (anxietyItems.includes(questionNum)) anxiety += score;
        if (stressItems.includes(questionNum)) stress += score;
    });
    
    // Get severity levels
    const depressionSev = getSeverity(depression, 'depression');
    const anxietySev = getSeverity(anxiety, 'anxiety');
    const stressSev = getSeverity(stress, 'stress');
    
    // Display results
    const resultsContainer = document.getElementById('assessmentResults');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Your Assessment Results</h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h5>Depression</h5>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${Math.min(100, (depression / 42) * 100)}%; background-color: ${depressionSev.color}">
                                    ${depression} (${depressionSev.level})
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Anxiety</h5>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${Math.min(100, (anxiety / 42) * 100)}%; background-color: ${anxietySev.color}">
                                    ${anxiety} (${anxietySev.level})
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Stress</h5>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${Math.min(100, (stress / 42) * 100)}%; background-color: ${stressSev.color}">
                                    ${stress} (${stressSev.level})
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <h5>Recommendations</h5>
                        <div class="recommendations">
                            ${getRecommendations(depressionSev, anxietySev, stressSev).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Save results to Supabase
    try {
        const response = await fetch('/api/assessment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                depression_score: depression,
                anxiety_score: anxiety,
                stress_score: stress,
                depression_level: depressionSev.level,
                anxiety_level: anxietySev.level,
                stress_level: stressSev.level,
                responses: userResponses
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save assessment results');
        }
        
        const data = await response.json();
        console.log('Assessment saved successfully:', data);
        
        // Update UI with saved data if needed
        if (data.streak) {
            const streakElement = document.getElementById('streakCount');
            if (streakElement) {
                streakElement.textContent = data.streak;
            }
        }
        
    } catch (error) {
        console.error('Error saving assessment:', error);
        // Show error message to user
        const errorElement = document.createElement('div');
        errorElement.className = 'alert alert-warning';
        errorElement.textContent = 'Assessment completed, but there was an issue saving your results.';
        resultsContainer.prepend(errorElement);
    }
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Handle assessment submission
const assessmentForm = document.getElementById('dassAssessmentForm');
if (assessmentForm) {
    assessmentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get all responses
        const responses = [];
        const selects = assessmentForm.querySelectorAll('select');
        let allAnswered = true;
        
        selects.forEach(select => {
            if (!select.value) {
                allAnswered = false;
                select.classList.add('is-invalid');
            } else {
                responses.push(parseInt(select.value));
                select.classList.remove('is-invalid');
            }
        });
        
        if (!allAnswered) {
            alert('Please answer all questions before submitting.');
            return;
        }
        
        // Calculate DASS scores
        const { depression, anxiety, stress } = calculateDassScores(responses);
        const depressionSev = getSeverity(depression, 'depression');
        const anxietySev = getSeverity(anxiety, 'anxiety');
        const stressSev = getSeverity(stress, 'stress');
        
        // Update UI with results
        const resultsContainer = document.getElementById('assessmentResults');
        resultsContainer.innerHTML = `
            <div class="card mb-3">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">Your Assessment Results</h4>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h5>Depression</h5>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${Math.min(100, (depression / 42) * 100)}%; background-color: ${depressionSev.color}">
                                    ${depression} (${depressionSev.level})
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Anxiety</h5>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${Math.min(100, (anxiety / 42) * 100)}%; background-color: ${anxietySev.color}">
                                    ${anxiety} (${anxietySev.level})
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5>Stress</h5>
                            <div class="progress mb-2" style="height: 25px;">
                                <div class="progress-bar" role="progressbar" 
                                     style="width: ${Math.min(100, (stress / 42) * 100)}%; background-color: ${stressSev.color}">
                                    ${stress} (${stressSev.level})
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <h5>Recommendations</h5>
                        <div class="recommendations">
                            ${getRecommendations(depressionSev, anxietySev, stressSev).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
        
        // Send to server
        try {
            const response = await fetch('/api/assessment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrf_token]').value
                },
                body: JSON.stringify({
                    depression,
                    anxiety,
                    stress,
                    responses
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save assessment');
            }
            
            // Update dashboard stats
            updateDashboardStats(depression, anxiety, stress);
            
        } catch (error) {
            console.error('Error saving assessment:', error);
            alert('There was an error saving your assessment. Please try again.');
        }
    });
}

// Get recommendations based on severity
function getRecommendations(depressionSev, anxietySev, stressSev) {
    const recs = [];
    
    // Add depression recommendations if moderate or higher
    if (depressionSev.level !== 'Normal' && depressionSev.level !== 'Mild') {
        recs.push(`
            <div class="alert alert-info">
                <strong>For ${depressionSev.level} Depression:</strong><br>
                ${recommendations.depression.slice(0, 3).join('<br>')}
            </div>
        `);
    }
    
    // Add anxiety recommendations if moderate or higher
    if (anxietySev.level !== 'Normal' && anxietySev.level !== 'Mild') {
        recs.push(`
            <div class="alert alert-warning">
                <strong>For ${anxietySev.level} Anxiety:</strong><br>
                ${recommendations.anxiety.slice(0, 3).join('<br>')}
            </div>
        `);
    }
    
    // Add stress recommendations if moderate or higher
    if (stressSev.level !== 'Normal' && stressSev.level !== 'Mild') {
        recs.push(`
            <div class="alert alert-danger">
                <strong>For ${stressSev.level} Stress:</strong><br>
                ${recommendations.stress.slice(0, 3).join('<br>')}
            </div>
        `);
    }
    
    // If all are normal/mild, show general wellness tips
    if (recs.length === 0) {
        recs.push(`
            <div class="alert alert-success">
                <strong>You're doing great!</strong><br>
                Your assessment shows normal to mild levels of depression, anxiety, and stress. 
                Keep up with your self-care routine and check back regularly to monitor your mental well-being.
            </div>
        `);
    }
    
    return recs;
}

// Update dashboard stats based on assessment
function updateDashboardStats(depression, anxiety, stress) {
    // Update mood indicator based on highest score
    const scores = { depression, anxiety, stress };
    const highestCategory = Object.keys(scores).reduce((a, b) => scores[a] > scores[b] ? a : b);
    
    const todayMood = document.getElementById('todayMood');
    if (todayMood) {
        const severity = getSeverity(scores[highestCategory], highestCategory);
        todayMood.style.backgroundColor = severity.color;
        todayMood.textContent = severity.level;
        
        // Add tooltip with more info
        todayMood.title = `Depression: ${depression} | Anxiety: ${anxiety} | Stress: ${stress}`;
        todayMood.setAttribute('data-bs-toggle', 'tooltip');
        new bootstrap.Tooltip(todayMood);
    }
    
    // Update streak (this would normally come from the server)
    const streakCount = document.getElementById('streakCount');
    if (streakCount) {
        // In a real app, this would be fetched from the server
        streakCount.textContent = '1';
    }
}

// Encouragement quotes
const encouragementQuotes = [
    {
        text: "You are capable of amazing things.",
        author: ""
    },
    {
        text: "One day at a time, one step at a time. You're doing great!",
        author: ""
    },
    {
        text: "Your mental health is a priority. Your happiness is essential. Your self-care is a necessity.",
        author: ""
    },
    {
        text: "You don't have to be perfect to be amazing.",
        author: ""
    },
    {
        text: "It's okay to not be okay as long as you're not giving up.",
        author: ""
    },
    {
        text: "You are stronger than you think.",
        author: ""
    },
    {
        text: "Every day may not be good, but there's something good in every day.",
        author: "Alice Morse Earle"
    },
    {
        text: "You're braver than you believe, stronger than you seem, and smarter than you think.",
        author: "A.A. Milne"
    },
    {
        text: "The only way to do great work is to love what you do.",
        author: "Steve Jobs"
    },
    {
        text: "You are never too old to set another goal or to dream a new dream.",
        author: "C.S. Lewis"
    }
];

// Function to get a daily quote (same quote for the same day for each user)
function getDailyQuote() {
    // Get today's date string (YYYY-MM-DD)
    const today = new Date().toISOString().split('T')[0];
    
    // Use the date to create a consistent index for the quote
    const dateNum = parseInt(today.replace(/-/g, ''), 10);
    const quoteIndex = dateNum % encouragementQuotes.length;
    
    return encouragementQuotes[quoteIndex];
}

// Function to display the daily quote
function displayDailyQuote() {
    const quoteElement = document.getElementById('dailyQuote');
    const authorElement = document.getElementById('quoteAuthor');
    
    if (quoteElement && authorElement) {
        const quote = getDailyQuote();
        quoteElement.textContent = `"${quote.text}"`;
        authorElement.textContent = quote.author ? `— ${quote.author}` : '';
    }
}

// Initialize the assessment and display quote when the page loads
document.addEventListener('DOMContentLoaded', () => {
    initAssessment();
    displayDailyQuote();
    
    // Update the quote every 24 hours (in case the page stays open)
    setInterval(displayDailyQuote, 24 * 60 * 60 * 1000);
});

// Update streak count (this would normally come from the server)
const streakCount = document.getElementById('streakCount');
if (streakCount) {
    streakCount.textContent = '7'; // Example streak count
}

// Update badge count (this would normally come from the server)
const badgeCount = document.getElementById('badgeCount');
if (badgeCount) {
    badgeCount.textContent = '3'; // Example badge count
}
