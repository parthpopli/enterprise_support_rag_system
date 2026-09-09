# Enterprise Support RAG Assistant

An AI-powered enterprise support assistant that answers questions using internal company documentation such as troubleshooting guides, SOPs, FAQs, and technical documentation.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information before generating an answer, helping keep responses grounded in the available documentation.

## 🚀 Live Demo

**Frontend:**  
https://main.d1gczdp00l1ai0.amplifyapp.com/

**Backend API:**  
https://enterprise-support-rag-system.onrender.com/

## ✨ Features

- Upload PDF, DOCX, and TXT documents
- Automatic document processing and chunking
- Semantic search using embeddings
- Keyword search using BM25
- Hybrid retrieval with Reciprocal Rank Fusion (RRF)
- AI-generated answers using Groq
- Source citations for retrieved information
- Admin document management
- REST API built with FastAPI
- React-based web interface

## 🏗️ Architecture

```text
User
 │
 ▼
React Frontend
 │
 ▼
FastAPI Backend
 │
 ├── Document Ingestion
 │      ├── Text Extraction
 │      ├── Chunking
 │      └── Embeddings
 │
 ├── Hybrid Retrieval
 │      ├── ChromaDB
 │      └── BM25
 │
 ▼
Relevant Documents
 │
 ▼
Groq LLM
 │
 ▼
Grounded Answer + Sources


```

<img width="1862" height="961" alt="rag" src="https://github.com/user-attachments/assets/eb8f07c7-e247-4011-8f1c-dca64d238a2b" />


