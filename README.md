# LangGraph Weather Application

This project demonstrates a simple weather application using LangGraph.

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

This application requires a `GOOGLE_API_KEY` to function. Create a `.env` file in the root directory of the project and add your API key:

```
GOOGLE_API_KEY="your_google_api_key_here"
```

Replace `"your_google_api_key_here"` with your actual Google API Key.

## Running the Application

To start the application, run the following command:

```bash
.\venv\Scripts\activate
uvicorn main:app --reload
```

This will start the FastAPI application with auto-reloading enabled. You can then interact with the API endpoints defined in `main.py` (e.g., `/docs` for Swagger UI).
