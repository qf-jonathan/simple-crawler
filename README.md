# Simple Crawler Project

This repository contains a simple crawler project that uses FastAPI and asyncio.

## Project Structure

- api: A FastAPI-based module that provides API endpoints.
- crawler: An asyncio-based service that performs the url crawling.
- storage: Shared SQLite database accessed by both modules.

## Requirements

- Python 3.8+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)

## Installation

```bash
uv sync
```

## Running the Project

```bash
sh run_api.sh
```

In another terminal:

```bash
sh run_crawler.sh
```
