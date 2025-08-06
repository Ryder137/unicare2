// Mood indicator colors
const moodColors = {
    happy: '#4CAF50',
    okay: '#FFC107',
    sad: '#FF9800',
    stressed: '#F44336',
    anxious: '#9C27B0'
};

// Recommendations based on mood and stress level
const recommendations = {
    happy: [
        'Keep up the good work!',
        'Try something new today!',
        'Share your happiness with someone!'
    ],
    okay: [
        'Take a short walk outside',
        'Listen to some music',
        'Do something creative'
    ],
    sad: [
        'Try some deep breathing exercises',
        'Talk to someone you trust',
        'Write down your thoughts'
    ],
    stressed: [
        'Take a 5-minute break',
        'Try progressive muscle relaxation',
        'Make a to-do list to organize your tasks'
    ],
    anxious: [
        'Practice mindfulness meditation',
        'Take slow, deep breaths',
        'Focus on the present moment'
    ]
};

// Update stress level display
const stressLevel = document.getElementById('stressLevel');
const stressLevelValue = document.getElementById('stressLevelValue');
stressLevel.addEventListener('input', () => {
    stressLevelValue.textContent = stressLevel.value;
});

// Handle assessment submission
const assessmentForm = document.getElementById('assessmentForm');
assessmentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const mood = document.getElementById('mood').value;
    const stressLevelValue = stressLevel.value;
    
    // Update today's mood indicator
    const todayMood = document.getElementById('todayMood');
    todayMood.style.backgroundColor = moodColors[mood];
    todayMood.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
    
    // Get recommendations based on mood
    const moodRecs = recommendations[mood];
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = '';
    
    // Show 3 random recommendations
    const shownRecs = [];
    for (let i = 0; i < 3; i++) {
        const randomRec = moodRecs[Math.floor(Math.random() * moodRecs.length)];
        if (!shownRecs.includes(randomRec)) {
            shownRecs.push(randomRec);
            const recDiv = document.createElement('div');
            recDiv.className = 'recommendation-card';
            recDiv.textContent = randomRec;
            recommendationsDiv.appendChild(recDiv);
        }
    }
    
    // Send assessment to server
    const response = await fetch('/api/assessment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mood: mood,
            stress_level: stressLevelValue
        })
    });
    
    if (response.ok) {
        alert('Assessment submitted successfully!');
    }
});

// Update streak count (this would normally come from the server)
const streakCount = document.getElementById('streakCount');
streakCount.textContent = '7'; // Example streak count

// Update badge count (this would normally come from the server)
const badgeCount = document.getElementById('badgeCount');
badgeCount.textContent = '3'; // Example badge count
