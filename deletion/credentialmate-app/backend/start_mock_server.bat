@echo off
set USE_MOCK_DOCUMENT_PARSER=true
set SKIP_AUTH=true
python -m uvicorn main:app --reload --port 8000
