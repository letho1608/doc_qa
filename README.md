# DocQA - Intelligent Document Question Answering 🤖

> Upload documents, ask questions, get AI-powered answers

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 Introduction

**DocQA** is a web application that enables intelligent interaction with your documents. Simply upload files, ask questions, and the AI will search through your documents to provide accurate answers.

### Key Features

- 📄 Support for multiple document formats (PDF, DOCX, TXT, MD)
- 💬 Chat with documents naturally
- 🔍 Intelligent semantic search
- 💾 Conversation history
- 🌐 Beautiful, user-friendly web interface

## 🚀 Quick Start

### 1. Install Python packages

```bash
pip install -r requirements.txt
```

### 2. Configure API key

Create a `.env` file and add your Google API key:

```env
GOOGLE_API_KEY=your-api-key-here
```

> 💡 **Get a free API key at**: https://aistudio.google.com/api-keys

### 3. Run the application

```bash
python main.py
```

Open your browser and navigate to: **http://localhost:8000**

## 💡 How to Use

1. **Upload documents**: Click on the "Documents" tab → Drag and drop or select files
2. **Ask questions**: Return to the "Chat" tab → Type your question → Press Enter
3. **Get answers**: The AI will read your documents and answer your questions

## 🛠️ Tech Stack

- **Backend**: FastAPI + LangChain
- **AI**: Google Gemini (LLM) + Sentence Transformers (Embedding)
- **Vector DB**: FAISS
- **Frontend**: HTML + CSS + JavaScript

## ⚙️ Advanced Configuration

### Switch to GPU (if available)

Edit the `.env` file:
```env
EMBEDDING_DEVICE=cuda
```

### Customize model

Edit the `.env` file:
```env
SENTENCE_TRANSFORMER_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

## 📝 Notes

- Documents are stored in the `storage/uploads/` directory
- Vector data is stored in `storage/vector_store/`
- Chat history is stored in `storage/conversations/`

---
