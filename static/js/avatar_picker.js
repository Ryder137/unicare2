// Available avatar options (add more as needed)
const AVATARS = [
    { id: 'default', name: 'Default', path: '/static/img/avatars/default.png' }
];

// Function to handle image loading errors
function handleImageError(img) {
    // Set a fallback image or hide the broken image
    img.onerror = null; // Prevent infinite loop if fallback also fails
    img.src = '/static/img/avatars/default.png';
}

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('avatarModal');
    const avatarGrid = document.getElementById('avatarGrid');
    const currentAvatar = document.getElementById('currentAvatar');
    const saveBtn = document.getElementById('saveAvatarBtn');
    
    // Check if required elements exist
    if (!avatarGrid) {
        console.warn('Avatar grid element not found');
        return;
    }
    
    let selectedAvatar = null;

    // Populate avatar grid
    AVATARS.forEach(avatar => {
        const col = document.createElement('div');
        col.className = 'col-4 col-md-3 text-center mb-3';
        
        const avatarEl = document.createElement('div');
        avatarEl.className = 'avatar-option d-inline-flex align-items-center justify-content-center';
        avatarEl.style.width = '80px';
        avatarEl.style.height = '80px';
        avatarEl.style.cursor = 'pointer';
        avatarEl.style.borderRadius = '50%';
        avatarEl.style.border = '1px solid #dee2e6';
        avatarEl.style.overflow = 'hidden';
        avatarEl.title = avatar.name;
        
        const img = document.createElement('img');
        img.src = avatar.path;
        img.alt = avatar.name;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.onerror = function() {
            // If image fails to load, show initials
            this.style.display = 'none';
            const initials = document.createElement('div');
            initials.textContent = avatar.name.charAt(0).toUpperCase() || 'U';
            initials.style.fontSize = '24px';
            initials.style.color = '#6c757d';
            avatarEl.appendChild(initials);
        };
        
        avatarEl.appendChild(img);
        
        avatarEl.addEventListener('click', () => {
            // Remove selected class from all options
            document.querySelectorAll('.avatar-option').forEach(el => {
                el.style.border = '1px solid #dee2e6';
                el.style.boxShadow = 'none';
            });
            
            // Add selected style to clicked option
            avatarEl.style.border = '3px solid #0d6efd';
            avatarEl.style.boxShadow = '0 0 0 0.25rem rgba(13, 110, 253, 0.25)';
            selectedAvatar = avatar.path;
        });
        
        col.appendChild(avatarEl);
        avatarGrid.appendChild(col);
    });

    // Save selected avatar
    saveBtn.addEventListener('click', async () => {
        if (!selectedAvatar) {
            alert('Please select an avatar');
            return;
        }

        try {
            const response = await fetch('/update_avatar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ avatar_url: selectedAvatar })
            });

            if (response.ok) {
                // Update the displayed avatar
                currentAvatar.src = selectedAvatar;
                // Close the modal
                const modalInstance = bootstrap.Modal.getInstance(modal);
                modalInstance.hide();
                
                // Show success message
                alert('Avatar updated successfully!');
            } else {
                throw new Error('Failed to update avatar');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to update avatar. Please try again.');
        }
    });

    // Reset selection when modal is closed
    modal.addEventListener('hidden.bs.modal', function () {
        selectedAvatar = null;
        document.querySelectorAll('.avatar-option').forEach(el => {
            el.classList.remove('border-primary');
            el.style.borderWidth = '1px';
        });
    });
});
