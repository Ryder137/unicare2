// Available avatar options (add more as needed)
const AVATARS = [
    { id: 'cat', name: 'Cat', path: '/static/img/avatars/cat.png' },
    { id: 'dog', name: 'Dog', path: '/static/img/avatars/dog.png' },
    { id: 'panda', name: 'Panda', path: '/static/img/avatars/panda.png' },
    { id: 'fox', name: 'Fox', path: '/static/img/avatars/fox.png' },
    { id: 'rabbit', name: 'Rabbit', path: '/static/img/avatars/rabbit.png' },
    { id: 'sunflower', name: 'Sunflower', path: '/static/img/avatars/sunflower.png' },
    { id: 'rose', name: 'Rose', path: '/static/img/avatars/rose.png' },
    { id: 'tulip', name: 'Tulip', path: '/static/img/avatars/tulip.png' },
    { id: 'daisy', name: 'Daisy', path: '/static/img/avatars/daisy.png' },
];

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('avatarModal');
    const avatarGrid = document.getElementById('avatarGrid');
    const currentAvatar = document.getElementById('currentAvatar');
    const saveBtn = document.getElementById('saveAvatarBtn');
    
    let selectedAvatar = null;

    // Populate avatar grid
    AVATARS.forEach(avatar => {
        const col = document.createElement('div');
        col.className = 'col-4 col-md-3 text-center mb-3';
        
        const avatarEl = document.createElement('img');
        avatarEl.src = avatar.path;
        avatarEl.className = 'img-thumbnail rounded-circle avatar-option';
        avatarEl.style.width = '80px';
        avatarEl.style.height = '80px';
        avatarEl.style.cursor = 'pointer';
        avatarEl.style.objectFit = 'cover';
        avatarEl.alt = avatar.name;
        avatarEl.title = avatar.name;
        
        avatarEl.addEventListener('click', () => {
            // Remove selected class from all options
            document.querySelectorAll('.avatar-option').forEach(el => {
                el.classList.remove('border-primary');
                el.style.borderWidth = '1px';
            });
            
            // Add selected class to clicked option
            avatarEl.classList.add('border-primary');
            avatarEl.style.borderWidth = '3px';
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
