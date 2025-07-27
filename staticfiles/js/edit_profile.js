document.addEventListener('DOMContentLoaded', function() {
    // Any future JavaScript functionality can be added here
    console.log('Edit profile page loaded');
});
    selectedGenres.innerHTML = '';
    
    checkboxes.forEach(checkbox => {
        const genre = checkbox.value;
        const label = checkbox.parentNode.textContent.trim();
        const icon = checkbox.parentNode.querySelector('.genre-icon').textContent;
        
        const tag = document.createElement('span');
        tag.className = 'selected-genre-tag';
        tag.innerHTML = `<span class="genre-icon">${icon}</span>${label}`;
        selectedGenres.appendChild(tag);
    });


// Initialize selected genres on page load
document.addEventListener('DOMContentLoaded', function() {
    updateSelectedGenres();
});
    closeGenrePopup();


function updateSelectedGenres() {
    const selectedGenres = document.getElementById('selectedGenres');
    const checkboxes = document.querySelectorAll('input[name="photo_genres"]:checked');
    
    selectedGenres.innerHTML = '';
    
    checkboxes.forEach(checkbox => {
        const genre = checkbox.value;
        const label = checkbox.parentNode.textContent.trim();
        const icon = checkbox.parentNode.querySelector('.genre-icon').textContent;
        
        const tag = document.createElement('span');
        tag.className = 'selected-genre-tag';
        tag.innerHTML = `<span class="genre-icon">${icon}</span>${label}`;
        selectedGenres.appendChild(tag);
    });
}

// Close popup when clicking outside
document.addEventListener('click', function(e) {
    const popup = document.getElementById('genrePopup');
    const btn = document.querySelector('.genre-selector-btn');
    
    if (!e.target.closest('.genre-selector') && popup.style.display === 'block') {
        popup.style.display = 'none';
        btn.classList.remove('active');
    }
});

// Initialize selected genres on page load
document.addEventListener('DOMContentLoaded', function() {
    updateSelectedGenres();
});
