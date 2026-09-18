
# AI Requirement Intelligence System

A GenAI application that analyzes proposal/RFP PDFs and converts their requirements into a structured, traceable dataset.

## Flow
PDF -> Page-wise extraction -> Gemini 2.5 Flash -> Structured requirements -> Validation -> Excel / Word / JSON

## Requirement hierarchy
Business Area -> Requirement Group -> Capability -> Requirement

## Setup
1. Create a virtual environment.
2. Install packages:
   pip install -r requirements.txt
3. Copy `.env.example` to `.env`.
4. Add your Gemini API key.
5. Run:
   streamlit run app.py

## Important
This implementation does not use RAG, vector databases, embeddings, or a retriever. Gemini analyzes the uploaded document directly.
