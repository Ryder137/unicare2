// Wrap in IIFE to prevent variable hoisting issues
(function() {
    // DOM Elements
    const moodOptions = document.querySelectorAll('.mood-option');
    const moodInput = document.getElementById('mood-rating');
    const journalForm = document.getElementById('journal-form');
    const saveDraftBtn = document.getElementById('save-draft');
    const journalTextarea = document.getElementById('journal-entry');
    const entriesList = document.getElementById('entries-list');
    const gratitudeInputs = Array.from(document.querySelectorAll('input[name="gratitude[]"]'));
    
    // Initialize data from localStorage
    let journalEntries = JSON.parse(localStorage.getItem('gratitudeJournalEntries')) || [];
    
    // Initialize the page
    function init() {
        // Set up mood selection
        moodOptions.forEach(option => {
            option.addEventListener('click', () => {
                const value = parseInt(option.dataset.value);
                setMood(value);
            });
        });
        
        // Set up form submission
        if (journalForm) {
            journalForm.addEventListener('submit', (e) => {
                e.preventDefault();
                saveEntry(false);
            });
        }
        
        // Set up save draft button
        if (saveDraftBtn) {
            saveDraftBtn.addEventListener('click', (e) => {
                e.preventDefault();
                saveEntry(true);
            });
        }
        
        // Load any saved entries
        renderEntries();
        
        // Load any draft
        loadDraft();
    }
    
    // Set mood selection
    function setMood(value) {
        if (!moodInput) return;
        
        moodInput.value = value;
        moodOptions.forEach(option => {
            if (parseInt(option.dataset.value) === value) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }
    
    // Save entry to localStorage
    function saveEntry(isDraft = false) {
        const entry = {
            id: Date.now(),
            date: new Date().toISOString(),
            mood: parseInt(moodInput.value) || 3,
            gratitude: gratitudeInputs.map(input => input.value.trim()).filter(Boolean),
            entry: journalTextarea ? journalTextarea.value.trim() : '',
            isDraft: isDraft
        };
        
        if (isDraft) {
            // Remove any existing draft
            journalEntries = journalEntries.filter(e => !e.isDraft);
            journalEntries.unshift(entry);
            showNotification('Draft saved!', 'info');
        } else {
            // Save as final entry
            journalEntries.unshift(entry);
            showNotification('Entry saved!', 'success');
            
            // Clear form
            if (journalForm) journalForm.reset();
            setMood(3); // Reset to neutral
        }
        
        saveEntries();
        renderEntries();
    }
    
    // Save entries to localStorage
    function saveEntries() {
        localStorage.setItem('gratitudeJournalEntries', JSON.stringify(journalEntries));
    }
    
    // Load draft
    function loadDraft() {
        const draft = journalEntries.find(entry => entry.isDraft);
        if (!draft) return;
        
        // Set form values from draft
        setMood(draft.mood);
        if (draft.gratitude) {
            draft.gratitude.forEach((item, i) => {
                if (gratitudeInputs[i]) {
                    gratitudeInputs[i].value = item;
                }
            });
        }
        if (journalTextarea) {
            journalTextarea.value = draft.entry || '';
        }
        
        showNotification('Draft loaded', 'info');
    }
    
    // Show notification
    function showNotification(message, type = 'success') {
        // Create notification element if it doesn't exist
        let notification = document.querySelector('.toast-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.className = 'toast-notification';
            document.body.appendChild(notification);
        }
        
        notification.textContent = message;
        notification.className = `toast-notification alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '1100';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (notification) {
                const bsAlert = new bootstrap.Alert(notification);
                bsAlert.close();
            }
        }, 3000);
    }
    
    // Initialize the app
    document.addEventListener('DOMContentLoaded', init);
})();
