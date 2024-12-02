# FMP API Integration Project

This project provides a script to fetch, filter, and store financial data from the Financial Modeling Prep (FMP) API. The project includes functionality to save the data into a CSV file and a PostgreSQL database, along with Docker support for setting up PostgreSQL and pgAdmin.
## Features

- Fetch data from the Financial Modeling Prep API.
- Filter companies based on Indian exchanges (NSE and BSE).
- Save the filtered data into a CSV file.
- Push the data to a PostgreSQL database.
- Docker Compose setup for PostgreSQL and pgAdmin.
- Secure API key handling using `.env` files.

## Prerequisites

- Python 3.6 or later
- PostgreSQL (local or via Docker)
- Docker and Docker Compose (for PostgreSQL setup)
- A valid [Financial Modeling Prep API Key](https://site.financialmodelingprep.com/developer/docs)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/fmp_api.git
   cd fmp_api
2. **Set up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
3. **Set up .env file**
   ```plaintext	
   API_key=your_fmp_api_key
4. **Run the script**
   ```bash
   python fetch_companies.py
5. **Set up PostgreSQL**
   ```bash
   docker compose up -d
6. **Access pgAdmin**
   Open http://localhost:8081 in your browser and configure PostgreSQL.


