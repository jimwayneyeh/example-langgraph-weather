# LangGraph Weather Application

This project demonstrates a simple, stateful weather application using LangGraph. It can remember the context of the conversation.

## Project Setup

Follow these steps to set up the project environment:

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd example-langgraph-weather
    ```
    (Note: If you already have the folder, you can skip this step.)

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Environment Variables

This application requires API keys to function. You must set the following environment variables in your terminal before running the application:

- `GOOGLE_API_KEY`: Your API key for Google Generative AI.
- `OPENWEATHERMAP_API_KEY`: Your API key for OpenWeatherMap.

**Example (Windows CMD):**
```bash
set GOOGLE_API_KEY="your_google_api_key_here"
set OPENWEATHERMAP_API_KEY="your_openweathermap_api_key_here"
```

**Example (Windows PowerShell):**
```bash
$env:GOOGLE_API_KEY="your_google_api_key_here"
$env:OPENWEATHERMAP_API_KEY="your_openweathermap_api_key_here"
```

**Example (Linux/macOS):**
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export OPENWEATHERMAP_API_KEY="your_openweathermap_api_key_here"
```

Replace the placeholder values with your actual API keys.

## Running the Application

To start the application, run the following command:

```bash
.\venv\Scripts\activate
uvicorn main:app --reload
```

This will start the FastAPI application with auto-reloading enabled. You can then interact with the API endpoints, for example, by visiting the `/docs` page for the Swagger UI.

## How to Interact with the API

The `/agent-invoke` endpoint now manages conversation state.

*   **Starting a new conversation:**
    Send a POST request without a `conversation_id`. The API will create a new one for you.
    ```json
    {
      "message": "Hi, what's the weather like in Taipei?"
    }
    ```
    The response will include the `conversation_id`.

*   **Continuing a conversation:**
    Include the `conversation_id` from the previous response in your next request.
    ```json
    {
      "message": "What about in Kaohsiung?",
      "conversation_id": "the_id_you_received_from_the_server"
    }
    ```

The conversation will be stored on the server for 30 minutes of inactivity before being automatically cleared.
