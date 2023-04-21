// Play track on search results page
const playButtons = document.querySelectorAll('.play-button');
const spotifyPlayer = document.getElementById('spotify-player');

playButtons.forEach(button => {
    button.addEventListener('click', () => {
        const trackId = button.getAttribute('data-track-id');
        spotifyPlayer.src = `https://open.spotify.com/embed/track/${trackId}`;
        spotifyPlayer.style.display = 'block';
    });
});

// Play track on playlist page

const tracks = document.querySelectorAll('.track');

tracks.forEach(track => {
    track.addEventListener('click', () => {
        const trackId = track.dataset.trackId;
        spotifyPlayer.src = `https://open.spotify.com/embed/track/${trackId}`;
        spotifyPlayer.style.display = 'block';
    });
});

// choose playlist first
document.addEventListener('DOMContentLoaded', function() {
    const playlistSelect = document.getElementById('playlist-select');
    const addToPlaylistButton = document.getElementById('add-to-playlist');

    playlistSelect.addEventListener('change', function() {
        if (playlistSelect.value === 'Choose playlist') {
            addToPlaylistButton.disabled = true;
        } else {
            addToPlaylistButton.disabled = false;
        }
    });
});

// Add track to playlist 
const addToPlaylistButtons = document.querySelectorAll('.add-to-playlist');

addToPlaylistButtons.forEach(button => {
    const selectElement = button.closest('.options').querySelector('.playlist-select');

    selectElement.addEventListener('change', () => {
        button.disabled = selectElement.value === 'select playlist';
    });

    button.addEventListener('click', async() => {
        const trackId = button.getAttribute('data-track-id');
        const playlistId = selectElement.value;
        if (playlistId === 'select playlist') {
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
            body: JSON.stringify({ track_data: trackData }),
        });

        const data = await response.json();

        if (data.status === 'error' || data.status === 'warning' || data.status === 'success') {
            alert(data.message);
        } else {
            alert(data.message);
        }
    });
});