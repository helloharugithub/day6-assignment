# Supply Chain Status API

This is my Day 6 project for the FDE Academy (Palantir COE) — a FastAPI service that pulls shipment status from three different vendor systems, aggregates them into one response, and normalizes the mess of field names each vendor uses into a single schema. It's the FDE pattern for quickly validating a client's source data before designing a real Foundry pipeline — build a small API, hit it with Postman/Swagger, see what the data actually looks like.

Everything runs off an in-memory dict for now, no real database or live vendor calls — this was built as a lab exercise, not a production service.

## What it does

- Basic shipment CRUD — list, get by ID, create, with status/carrier filtering
- Lists available carriers
- Aggregates tracking data from 3 mock vendors concurrently (`asyncio.gather`) and normalizes their different response shapes into one `VendorStatus` model
- If a vendor call fails, that vendor just gets dropped from the response instead of blowing up the whole request — only errors out (503) if all three fail
- Every endpoint is locked behind an `X-API-Key` header
- Pydantic validates everything going in and out
- Test suite with pytest — 13/13 passing, 93% coverage

## Project structure

```
day6_supply_chain_api/
├── main.py          # the API itself — models, routes, vendor aggregation, auth
├── test_main.py     # pytest suite
└── README.md
```

## Requirements

- Python 3.11+
- Core: `fastapi`, `uvicorn`, `pydantic`, `httpx`
- Testing & quality: `pytest`, `pytest-cov`, `black`, `mypy`

## Setup

```powershell
cd day6_supply_chain_api
python -m pip install fastapi uvicorn pydantic pytest pytest-cov httpx black mypy
```

## Running it

```powershell
uvicorn main:app --reload
```

## Auth

Every route needs an `X-API-Key` header.

Valid keys: `techstar-fde-key-001`, `techstar-fde-key-002`

- No header → 401
- Wrong key → 403

## Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/shipments` | list shipments, optional `?status=` and `?carrier=` filters |
| GET | `/shipments/{id}` | get one shipment, 404 if it doesn't exist |
| POST | `/shipments` | create a shipment, 409 if the ID already exists |
| GET | `/carriers` | list known carriers |
| GET | `/supply-chain-status/{id}` | pulls and normalizes status from all 3 vendors |

## Testing, formatting, type checks

```powershell
pytest test_main.py -v --cov=main --cov-report=term-missing
black main.py test_main.py
mypy main.py
```

Current run: 13/13 tests passing, 93% coverage.

## Quick command reference

Everything above, back to back, from the project folder:

```powershell
cd day6_supply_chain_api
python -m pip install fastapi uvicorn pydantic pytest pytest-cov httpx black mypy
pytest test_main.py -v --cov=main --cov-report=term-missing
black main.py test_main.py
mypy main.py
git add .
git commit -m "feat: complete Day 6 lab API with auth, type checks, and 93% test coverage"
git push origin main
```

## Notes to self

- The vendor aggregation endpoint is the one that actually needed thought — mocking async failures with `AsyncMock` + `side_effect` to make the "one vendor down" case deterministic instead of relying on the random failure rate.
- Carrier data being hardcoded in `list_carriers()` is fine for a lab exercise but wouldn't survive a real client engagement — next iteration would move that into a config file or small DB table.
