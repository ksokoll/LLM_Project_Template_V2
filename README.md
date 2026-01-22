# LLM Project Template V2

This repository provides a minimal, production-oriented template for building LLM-based APIs.  
The goal of version 2 is clarity, with fewer moving parts, predictable execution flow, and patters that hold up in real deployments.

## What Changed Compared to V1

1. Added Error handling: Be it API-Errors from LLM calls or parsing errors, this is catched by several executions. Principle: Fail Fast & Chain of responsibility.
2. Added Logging: Of course Errors are logged, but also other occurances like if a worker finalizes it's steps successfully. This helps to find out what the tool is doing once in production.
3. Prompt is separated from code: I added a prompt library based on the proposal of Chip Huyen in her Book "AI Engineering" Chapter 7. She recommends to separate Prompts and also add a specific pydantic object to track changes, authorship etc.
4. I intentionally left out: ".env" , ".requirements.txt" and the dockerfiles. It proved not to make sense, as this framework serves as basis and gets enhanced over time, changing the requirements constantly. It's better to create them from scratch after finalizing the project.
5. Summarized the worker units: Instead of multiple workers, left is only 1 "processor" which can copy-pasted when needed. This serves that the framework is easier to understand, and can be evolved afterwards. The overall codebase is smaller, flatter, and easier to reason about, especially under operational pressure.

---

## The Current Project Structure

The application is organized along a single request pipeline. Each file maps to a clear responsibility and a single processing step. Also, the business logic is strongly separated from the program logic by separating models/config from the pipeline.

```
config.py                 # Central configuration and environment handling
models.py                 # Pydantic request and response models
prompts.py                # Versioned prompt definitions with metadata
validator.py              # Input validation and ULID generation
processor.py              # Unified LLM processing with optional retrieval
prompt_templates.py       # Here the pydantic models for the prompt are stored
pipeline.py               # Three-step orchestration
main.py                   # FastAPI entry point
```

Every request flows through validation & processing.
There are no hidden branches anymore,no background tasks, or implicit side effects.

---

## How to Run the Framework

The service is designed to run either locally or inside a container with only small code adjustments.

Start by installing dependencies and configuring your environment.

```bash
pip install -r requirements.txt
```

Create a `.env` file and provide at least an OpenAI API key.

```bash
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4o-mini
ENABLE_RETRIEVAL=false
```

Once configured, start the API server using FastAPI.

```bash
uvicorn main:app --reload
```

The service will be available on port 8000.  
Interactive API documentation is exposed at `/docs`.

To process a request, send a POST call to the `/process` endpoint with a JSON payload containing a query.

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset my password?"}'
```

---

## Design Intent

This template is not meant to cover every possible LLM architecture.  
It is meant to be a stable starting point that works out of the box, scales down well, and can be extended deliberately when real requirements emerge.

Have fun adding modules and experiencing how easy it is to integrate into this backbone structure :)
