# Burgers' Zoo Chatbot Project

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Technologies Used](#technologies-used)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)

## Introduction
The **Burgers' Zoo Chatbot** is a Django-based web application that helps visitors interactively find information about the zoo during their visit. The chatbot is enhanced with a Retrieval-Augmented Generation (RAG) system, utilizing different retrieval methods: **basic cosine similarity**, **retrievel with example answer**, and **retrieval with generated subqueries**. Users can also choose whether they want the chatbot to remember the conversation history.

## Features
- **Interactive Chat UI** for providing zoo-related information.
- **Multiple Retrieval Methods**: Users can choose between different IR methods for relevant responses.
- **Enable Chat History**: Users can enable or disable conversation history.
- **Customizable**: Easy to adapt to other use cases beyond zoo information.

## Installation

### Steps

1. **Clone the Repository**
   ```sh
   git clone https://github.com/woutman/burgerszoobot.git
   cd burgerszoobot
   ```

2. **Create a Virtual Environment and Activate It**
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   - Create a `api_keys.env` file in burgerszoobot/ (same directory as manage.py) and add the necessary environment variables:

   ```env
   OPENAI_API_KEY='your_openai_api_key'
   ```

5. **Run Database Migrations**
   ```sh
   cd burgerszoobot
   python manage.py migrate
   ```

6. **Run the Development Server**
   ```sh
   python manage.py runserver
   ```

## Usage

- Once the server is running, open a browser and navigate to `http://127.0.0.1:8000/chat/`.
- Enter your question in the input field and click "Send".
- Select different **retrieval methods** by choosing the radio buttons.
- Enable or disable **chat history** using the provided checkbox.

## Project Structure

```
burgerszoobot/
├── burgerszoobot/
│   ├── __init__.py
│   ├── asgi.py 
│   ├── settings.py           # Django settings
│   ├── urls.py               # URL configuration
│   └── wsgi.py
├── chatbot/
│   ├── migrations/
│   ├── templates/
│   │   └── chatbot/
│   │       └── chat.html      # Frontend HTML template
│   ├── static/
│   │   └── chatbot/
│   │       └── styles.css     # Custom CSS styles
│   ├── management/
│   │   └── commands/
│   │       └── ingest_docs.py # Command to ingest documents
│   ├── services/
│   │   ├── chromadb/
│   │   │   └── chroma.sqlite3 # Persistent ChromaDB database
│   │   ├── chatbot_service.py # Main chatbot service logic
│   │   ├── retrieval.py       # Logic for document retrieval
│   │   └── llm_interface.py   # LLM interaction (e.g., OpenAI API)
│   ├── views.py               # Handles user interactions
│   ├── urls.py                # Chatbot app URL configuration
│   └── models.py              # (Optional) Database models for chat history or document metadata
├── manage.py                  # Django's command-line utility
└── README.md                  # Project documentation
```

## Documents
A JSON file with a list of all documents that have been ingested can be found at `util/docs.json`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
