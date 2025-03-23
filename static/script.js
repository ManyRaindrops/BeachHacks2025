document.addEventListener('DOMContentLoaded', function() {
    // Create references to the DOM elements
    const queryInput = document.getElementById('searchbar');
    const mainDiv = document.querySelector('.main');

    // Send and recieve data to and from the server
    function sendQueryToServer(query) {
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

        // Recieve data from the server, executes after the previous operation is done (receives "response" and turns it into response.json)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        // ".then()" is a function that executes after the previous functions have completed. "data" is the parsed JSON data from the previous ".then" function
        .then(data => {
            // Makes sure that the data is successfully parsed
            if (data.status === 'success') {
                // Create a new paragraph element to display the result
                const botMessage = document.createElement('div');
                botMessage.className = 'bot-message';
                botMessage.textContent = data.result;
                loadingElement.replaceWith(botMessage);
            } else {
                // Display an error message if the data is was not successfully parsed
                const errorMessage = document.createElement('div');
                errorMessage.className = 'error-message';
                errorMessage.textContent = `Error: ${data.message}`;
                loadingElement.replaceWith(errorMessage);            }
        })
        .catch(error => {
            // Handles network errors if the send/receive couldn't connect to the server
            mainDiv.innerHTML = `<p>Network error: ${error}</p>`;
        });
    }

    // Event listener for the search bar (when the user presses Enter)
    queryInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const query = queryInput.value;
            sendQueryToServer(query);
        }
        // HTML - clear main screen and add loading elements. Add user's query as a chat bubble
    });
});
