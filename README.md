# ANMS - Flask auth scaffold

This is a minimal Flask scaffold with login and registration pages using Jinja2 templates and Bootstrap. The app supports Microsoft SQL Server via SQLAlchemy + pyodbc when `DATABASE_URL` is set, but it will default to a local SQLite file for quick testing.

Setup

1. Create a virtual environment and activate it.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run with SQLite (default):

```bash
python app.py
```

3. Or run with SQL Server using the provided connection settings:

```bash
set DATABASE_URL="mssql+pyodbc://ratib.nsamba:ratib.nsamba@localhost\\SQLEXPRESS/AgentNetworkOperations?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=Yes"
set SECRET_KEY="change-this-secret"
python app.py
```

Test SQL Server connection

```bash
python test_db.py
```

Notes

- The default fallback is still `sqlite:///anms.db` for quick testing if SQL Server is unavailable.
- Your requested MSSQL instance is `localhost\SQLEXPRESS` and the database is `AgentNetworkOperations`.
- This scaffold uses server-side form handling and Werkzeug password hashing.
