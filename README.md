# Personal Document AI Assistant

An AI-powered document assistant that allows users to upload their documents and ask questions based on their content.

## Project Goals

- Upload PDF, TXT, and DOCX documents
- Extract and process document content
- Split documents into chunks
- Generate embeddings
- Store embeddings in a vector database
- Retrieve relevant information
- Generate context-aware answers using an LLM
- Provide source references for answers

## Technology Stack

- Python
- FastAPI
- Sentence Transformers
- ChromaDB
- LLM API
- Docker

## Project Structure

- `app/ingestion`: Document loading and processing
- `app/retrieval`: Information retrieval
- `app/generation`: LLM and answer generation
- `app/api`: Backend API
- `data/uploads`: Uploaded documents
- `data/processed`: Processed data
- `tests`: Project tests

## Project Status

Currently in the initial setup phase.