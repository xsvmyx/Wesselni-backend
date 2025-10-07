alembic revision --autogenerate -m "create all tables"
alembic upgrade head
uvicorn app.main:app --reload
