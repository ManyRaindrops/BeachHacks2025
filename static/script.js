document.addEventListener('DOMContentLoaded', function() {
    // Create references to the DOM elements
    const queryInput = document.getElementById('searchbar');
    const searchButton = document.getElementById('searchbutton');
    const mainDiv = document.querySelector('main');


    // Send and recieve data to and from the server
    function sendQueryToServer(query, loadingElement) {
        console.log('sendQueryToServer function called with query:', query);
        // Send data to the server URL (sends the input data as a JSON with string data)
        fetch('/get_data', {
            // Tells the server what kind of request this is. POST requests are usually for sending data that is to be processed
            method: 'POST',

            // Defines what kind of information is being sent to the server
            headers: {
                'Content-Type': 'application/json'
            },
            // Converts input data into a string and turns it into a query type with the value "query," the function parameter
            body: JSON.stringify({ query: query })
        })
        .then(response => {
            console.log('Response received from server:', response);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        // ".then()" is a function that executes after the previous functions have completed. "data" is the parsed JSON data from the previous ".then" function
        .then(data => {
            console.log('Data parsed from response:', data);
            // Makes sure that the data is successfully parsed
            if (data.status === 'success') {
                // Create a new paragraph element to display the result
                const botMessage = document.createElement('div');
                botMessage.className = 'bot-message';
                botMessage.innerHTML = marked.parse(data.result); // Convert Markdown to HTML and set innerHTML
                loadingElement.replaceWith(botMessage);
                mainDiv.scrollTop = botMessage.offsetTop;
        } else {
                // Display an error message if the data is was not successfully parsed
                const errorMessage = document.createElement('div');
                errorMessage.className = 'error-message';
                errorMessage.textContent = `Error: ${data.message}`;
                loadingElement.replaceWith(errorMessage);
                mainDiv.scrollTop = errorMessage.offsetTop;
            }
        })
        .catch(error => {
            // Handles network errors if the send/receive couldn't connect to the server
            console.error('Network error:', error);
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.textContent = `Network error: ${error.message}`;
            loadingElement.replaceWith(errorMessage);
            mainDiv.scrollTop = mainDiv.scrollHeight;
        });
    }

    // Event listener for the search bar (when the user presses Enter)
    queryInput.addEventListener('keypress', function(event) {
        console.log('Keypress event on queryInput:', event.key);
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSearch();
        }
    });

    // Event listener for the search button
    searchButton.addEventListener('click', function() {
        console.log('Click event on searchButton');
        handleSearch();
    });

    // Function to handle search logic
    function handleSearch() {
        console.log('handleSearch function called');
        const query = queryInput.value.trim();

        if (!query) {
            console.log('Query is empty, returning from handleSearch');
            return;
        }

        // Add user message
        const userMessage = document.createElement('div');
        userMessage.className = 'user-message';
        userMessage.innerHTML = marked.parse(query);
        mainDiv.appendChild(userMessage);

        // Add loading indicator
        const loadingMessage = document.createElement('div');
        loadingMessage.className = 'loading-message';
        loadingMessage.textContent = 'Loading...';
        mainDiv.appendChild(loadingMessage);

        // Clear input and scroll to bottom
        queryInput.value = '';
        mainDiv.scrollTop = mainDiv.scrollHeight;

        sendQueryToServer(query, loadingMessage);
    }
    // Fetch conversations from the server
    fetch('/get_conversations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const historyDiv = document.getElementById('conversation_history');
            // Create a button for each conversation
            data.forEach(convo => {
                const button = document.createElement('button');
                button.textContent = convo.title;
                button.addEventListener('click', () => {
                    loadConversation(convo.conversation);
                });
                historyDiv.appendChild(button);
            });
        })
        .catch(error => {
            console.error('Error loading conversations:', error);
        });

    // Function to load a conversation into the main area
    function loadConversation(conversation) {
        const mainDiv = document.querySelector('main');
        // Clear the main area
        mainDiv.innerHTML = '';
        // Append each prompt-response pair
        conversation.forEach(pair => {
            const [prompt, response] = pair;
            // User message
            const userMessage = document.createElement('div');
            userMessage.className = 'user-message';
            userMessage.textContent = prompt;
            mainDiv.appendChild(userMessage);
            // Bot message
            const botMessage = document.createElement('div');
            botMessage.className = 'bot-message';
            botMessage.textContent = response;
            mainDiv.appendChild(botMessage);
        });
        // Scroll to the bottom of the main area
        mainDiv.scrollTop = mainDiv.scrollHeight;
    }
    //Toggle between day and night mode//
    const themeBtn = document.getElementById("theme");

function updateThemeIcon() {
  themeBtn.textContent = document.body.classList.contains("light-mode") ? "🌙" : "☀️";
}

// Toggle light/dark mode on button click
themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("light-mode");

  // Save preference
  const mode = document.body.classList.contains("light-mode") ? "light" : "dark";
  localStorage.setItem("theme", mode);

  updateThemeIcon();
});

// Apply saved theme on page load
window.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "light") {
    document.body.classList.add("light-mode");
  }
  updateThemeIcon();
});

});