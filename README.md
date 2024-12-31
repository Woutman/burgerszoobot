# Burgers' Zoo Chatbot Project

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documents](#documents)

## Introduction
The **Burgers' Zoo Chatbot** is a Django-based web application that helps visitors interactively find information about the zoo during their visit. The chatbot is enhanced with a Retrieval-Augmented Generation (RAG) system, consisting of query classification, query rephrasing, document retrieval, retrieval reranking, and summarization. Users can enable or disable the optional steps of this system and also choose whether they want the chatbot to remember the conversation history for comparison of results.

## Features
- **Interactive Chat UI** for providing zoo-related information.
- **Customizable RAG pipeline**: Users can enable or disable different steps in the RAG pipeline.
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
- Enter your question in the input field and press "Enter" or click "Verstuur".
- Enable or disable **steps in the RAG pipeline** or **chat history**  using the provided checkbox.

## Project Structure

```
burgerszoobot/
├── burgerszoobot/
│   ├── __init__.py
│   ├── asgi.py 
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL configuration
│   └── wsgi.py
├── chatbot/
│   ├── migrations/
│   ├── templates/
│   │   └── chatbot/
│   │       └── chat.html        # Frontend HTML template
│   ├── static/
│   │   └── chatbot/
│   │       ├── script.js        # Custom JavaScript scripts
│   │       └── styles.css       # Custom CSS styles
│   ├── management/
│   │   └── commands/
│   │       └── ingest_docs.py   # Command to ingest documents
│   ├── services/
│   │   ├── chromadb/
│   │   │   └── chroma.sqlite3   # Persistent ChromaDB database
│   │   ├── chatbot_service.py   # Main chatbot service logic
│   │   ├── llm_instructions.py  # Instructions for LLM components
│   │   ├── llm_interface.py     # LLM interaction (e.g., OpenAI API)
│   │   └── rag.py               # RAG pipeline
│   ├── views.py                 # Handles user interactions
│   ├── urls.py                  # Chatbot app URL configuration
│   ├── util.py                  # Utility functions
│   └── models.py                # (Optional) Database models for chat history or document metadata
├── manage.py                    # Django's command-line utility
└── README.md                    # Project documentation
```

## Documents
A JSON file with a list of all documents that have been ingested can be found at `util/docs.json`.
