# FinSight

FinSight is an AI-powered financial insights engine that transforms SEC 10-K and 10-Q filings into structured, searchable, and actionable information. The project emphasizes scalable backend systems and retrieval-augmented generation (RAG) for fast, context-aware financial analysis.

## Overview

Financial filings contain critical information but are lengthy and difficult to analyze efficiently. FinSight automates the ingestion, processing, and querying of SEC EDGAR filings, enabling users to extract insights using natural language queries.

## Features

- Automated ingestion of SEC EDGAR 10-K and 10-Q filings  
- Serverless processing pipeline using AWS Lambda  
- Efficient storage and retrieval with Amazon S3  
- AI-powered semantic search and question answering  
- Sub-second querying across large filing datasets  

## Architecture

- Ingestion layer downloads SEC EDGAR JSON indexes and filings  
- Processing layer cleans, chunks, and embeds filing text  
- Query layer retrieves relevant sections and generates grounded AI responses  

## Tech Stack

- Python  
- AWS Lambda  
- Amazon S3  
- LangChain  
- Vector embeddings and RAG  

## Use Cases

- Analyze risk factors and forward-looking statements  
- Compare financial performance across reporting periods  
- Extract company-specific insights from large filings  

## Status

Actively developed and optimized for scalability and performance.

## License

This project is for educational and portfolio purposes. All SEC EDGAR data is publicly available.
