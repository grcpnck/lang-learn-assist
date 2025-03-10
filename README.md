## Language Learning Assistant

This is a language learning app tailored to the languages that I want to learn, with the goal of using AI to correct written text since I practice that frequently. The app provides corrections for written text and shows previous grammar mistakes, as well as sugggests chinese characters to learn next.

### Notes on the frontend

**IMPORTANT PLEASE READ**

I did not code the frontend - it was generated using v0.dev AI.

It was primarily an experiment to use AI for frontend generation, see how it works, and how to efficiently use it to rapidly build a full application for prototyping. (Spoiler alert - it's pretty cool! I'm a big fan)

As a consequence, some elements of the frontend are there for display and do not have a function (yet!).

### Document Ingestion

The app uses ChromaDB to locally store embedding information in order to RAG. Two types of documents are ingested:

1. A text file about grammar mistakes that were previously made (this is mostly mocked data).
2. A pdf about Chinese characters and easy ways to memorize them.

The first time running the application, it will take a long time to load due to the volume of data in the pdf about Chinese characters.

## Running FastAPI

### Prerequisites

1. Install Python 3.8 or higher.
2. Install Node.js and npm.
3. Install the required Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Install frontend dependencies
   ```sh
   npm install
   ```

### Starting the Backend

1. Navigate to the project directory:

   ```sh
   cd /c:/Insert-Your-Path/language-learning-chatbot
   ```

2. Create a .env file and copy variables from .envexample

   You will need an OpenAI key to run this application

   Paste your API key into the .env file

3. Start the FastAPI application:

   ```sh
   python main.py
   ```

4. Open your browser and navigate to the Swagger page to test the API:
   ```
   http://127.0.0.1:8000/docs
   ```

### Starting the Frontend Application

1. Navigate to the frontend directory (if applicable):

   ```sh
   cd /c:/Insert-Your-Path/language-learning-chatbot
   ```

2. Install the required Node.js dependencies (if not already done):

   ```sh
   npm install
   ```

3. Start the frontend application:

   ```sh
   npm run dev
   ```

4. Open your browser and navigate to the frontend application:
   ```
   http://localhost:3000
   ```

### Additional Information

- The FastAPI application will run on `http://127.0.0.1:8000` by default.
- The frontend application will run on `http://localhost:3000` by default.
- You can use the Swagger UI to interact with the API and test the endpoints: http://127.0.0.1:8000/docs.
