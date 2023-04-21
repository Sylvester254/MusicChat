// Import the functions from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.20.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/9.20.0/firebase-analytics.js";
import { getAuth, signInWithCustomToken } from "https://www.gstatic.com/firebasejs/9.20.0/firebase-auth.js";
import { getDatabase, ref, onChildAdded, push, set } from "https://www.gstatic.com/firebasejs/9.20.0/firebase-database.js";
import { serverTimestamp } from "https://www.gstatic.com/firebasejs/9.20.0/firebase-database.js";


// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyAwSv3sZDBlj5GkbOEEdpDP2OlkPKbLPp0",
    authDomain: "musicchat-485c3.firebaseapp.com",
    databaseURL: "https://musicchat-485c3-default-rtdb.firebaseio.com",
    projectId: "musicchat-485c3",
    storageBucket: "musicchat-485c3.appspot.com",
    messagingSenderId: "342433137765",
    appId: "1:342433137765:web:b5b03d9219285a8ba6b28c",
    measurementId: "G-6BWXNRZ62G"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const database = getDatabase(app);


// Access the custom token from the data attribute
const customTokenElement = document.getElementById('custom-token-container');
const customToken = customTokenElement ? customTokenElement.getAttribute('data-custom-token') : undefined;

console.log("Client-side Custom Token:", customToken);


// Check if 'customToken' variable is available from the template
if (typeof customToken !== 'undefined') {
    signInWithCustomToken(auth, customToken)
        .then((userCredential) => {
            console.log('Signed in with custom token:', userCredential);

            // Get a reference to the messages node in the Realtime Database
            const messagesRef = ref(database, 'messages');


            // Listen for new messages and update the UI
            onChildAdded(messagesRef, (snapshot) => {
                const message = snapshot.val();
                const messageTimestamp = new Date(message.timestamp);
                const formattedTimestamp = messageTimestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });

                const formattedDate = messageTimestamp.toLocaleDateString('en-US', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                });

                const messagesContainer = document.getElementById('messages');
                const lastMessageDate = messagesContainer.getAttribute('data-last-message-date');

                let dateSeparator = '';
                if (lastMessageDate !== formattedDate) {
                    dateSeparator = `
                      <div class="date-separator">
                        <hr class="date-separator-line">
                        <span class="date-separator-text">${formattedDate}</span>
                        <hr class="date-separator-line">
                      </div>`;
                    messagesContainer.setAttribute('data-last-message-date', formattedDate);
                }

                const messageElement = document.createElement('div');
                messageElement.classList.add('message');
                messageElement.innerHTML = `
                  ${dateSeparator}
                  <div class="message-header">
                    <strong>${message.username}</strong>
                    <span class="message-time">${formattedTimestamp}</span>
                  </div>
                  <div class="message-text">${message.text}</div>`;
                messagesContainer.appendChild(messageElement);
            });


            // Send new messages to the Realtime Database
            const messageForm = document.getElementById('message-form');
            messageForm.addEventListener('submit', (event) => {
                event.preventDefault();

                const messageInput = document.getElementById('message-input');
                const messageText = messageInput.value.trim();
                if (messageText.length === 0) return;

                const newMessageRef = push(messagesRef);
                set(newMessageRef, {
                    username: displayName,
                    timestamp: serverTimestamp(),
                    text: messageText
                });

                messageInput.value = '';
            });

        })
        .catch((error) => {
            console.error('Error signing in with custom token:', error);
        });
}