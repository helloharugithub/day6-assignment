Supply Chain Status API

This is my Day 6 project for the FDE Academy (Palantir COE) — a FastAPI service that pulls shipment status from three different vendor systems, aggregates them into one response, and normalizes the mess of field names each vendor uses into a single schema. It's the FDE pattern for quickly validating a client's source data before designing a real Foundry pipeline — build a small API, hit it with Postman/Swagger, see what the data actually looks like.

Everything runs off an in-memory dict for now, no real database or live vendor calls — this was built as a lab exercise, not a production service.

What it does
Basic shipment CRUD — list, get by ID, create, with status/carrier filtering
Lists available carriers
Aggregates tracking data from 3 mock vendors concurrently (asyncio.gather) and normalizes their different response shapes into one VendorStatus model
If a vendor call fails, that vendor just gets dropped from the response instead of blowing up the whole request — only errors out (503) if all three fail
Every endpoint is locked behind an X-API-Key header
Pydantic validates everything going in and out
Test suite with pytest, currently sitting above 90% coverage
Project structure
day6_supply_chain_api/
├── main.py          # the API itself — models, routes, vendor aggregation, auth
├── test_main.py     # pytest suite
└── README.md

Requirements & Dependencies
Python: 3.11+

Core Packages: fastapi, uvicorn, pydantic, httpx

Testing & Quality: pytest, pytest-cov, black, mypy

Local Setup & Installation
Navigate to the directory:

PowerShell
cd day6_supply_chain_api
Install required dependencies:

PowerShell
python -m pip install fastapi uvicorn pydantic pytest pytest-cov httpx black mypy
Running the API Server
Start the local development server using uvicorn:

PowerShell
uvicorn main:app --reload

Once running, you can access:

Interactive OpenAPI Documentation (Swagger UI): http://127.0.0.1:8000/docs

Alternative Documentation (ReDoc): http://127.0.0.1:8000/redoc

Endpoints

Method	Endpoint	What it does
GET	/shipments	list shipments, optional ?status= and ?carrier= filters
GET	/shipments/{id}	get one shipment, 404 if it doesn't exist
POST	/shipments	create a shipment, 409 if the ID already exists
GET	/carriers	list known carriers
GET	/supply-chain-status/{id}	pulls and normalizes status from all 3 vendors


Code Quality & Testing
1. Run Unit Tests & Coverage Report
Execute pytest with code coverage tracking:

PowerShell

pytest test_main.py -v --cov=main --cov-report=term-missing

2. Run Code Formatter
Ensure code adheres to PEP 8 standard formatting:

PowerShell

black main.py test_main.py

3. Run Static Type Checker
Verify typing definitions:

PowerShell
mypy main.py

---


EXECUTION COMMANDS SUMMARY (VS CODE TERMINAL)
Navigate to directory:
cd day6_supply_chain_api

Install dependencies:
python -m pip install fastapi uvicorn pydantic pytest pytest-cov httpx black mypy

Run test suite & coverage (13/13 passed, 93% coverage):
pytest test_main.py -v --cov=main --cov-report=term-missing

Format & check typing:
black main.py test_main.py
mypy main.py

Push to GitHub:
git add .
git commit -m "feat: complete Day 6 lab API with auth, type checks, and 93% test coverage"
git push origin main

```powershell
git add README.md
git commit -m "docs: add comprehensive README for Day 6 Supply Chain API"
git push origin main

