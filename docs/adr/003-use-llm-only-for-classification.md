# ADR 003: Use LLM strictly for Classification and Summary generation

## Context
LLMs are powerful but prone to hallucinations, non-deterministic outputs, and high latency/cost. 

## Decision
We isolated the LLM. It is strictly used *only* for categorical classification of unknown merchants, and generating a high-level narrative summary. All data cleaning, deduplication, and numerical anomaly detection are handled by deterministic Python code.

## Rationale
- **Accuracy**: Math operations (like finding a 3x median anomaly) or date parsing must be 100% accurate. LLMs fail at basic arithmetic. Deterministic code guarantees accuracy.
- **Cost Efficiency**: Passing 10,000 rows to an LLM to find duplicates is prohibitively expensive. Hashing rows in Python is virtually free.
- **Speed**: Python services process thousands of rows per second. LLMs take seconds per batch.
- **Resilience**: By isolating the LLM, if the API key fails or OpenAI goes down, the core deterministic engine still successfully persists the cleaned transactions.
