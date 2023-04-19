const playButtons = document.querySelectorAll('.play-button');
const spotifyPlayer = document.getElementById('spotify-player');

playButtons.forEach(button => {
    button.addEventListener('click', () => {
        const trackId = button.getAttribute('data-track-id');
        spotifyPlayer.src = `https://open.spotify.com/embed/track/${trackId}`;
        spotifyPlayer.style.display = 'block';
    });
});

// Add track to playlist 
const addToPlaylistButtons = document.querySelectorAll('.add-to-playlist');

addToPlaylistButtons.forEach(button => {
    button.addEventListener('click', async() => {
        const trackId = button.getAttribute('data-track-id');
        const playlistId = document.getElementById('playlist-select').value;
        if (playlistId === 'Select a playlist') {
            alert('Please select a playlist.');
            return;
        }
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        console.log("CSRF Token:", csrfToken);

        const trackData = JSON.parse(button.getAttribute('data-track-data'));
        const response = await fetch(`/add_to_playlist/${playlistId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
            },
            body: JSON.stringify(trackData),
        });

        if (response.ok) {
            alert('Track added to playlist.');
        } else {
            alert('Error adding track to playlist.');
        }
    });
});