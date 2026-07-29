import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Use DATABASE_URL if provided; otherwise connect to the requested MSSQL server.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mssql+pyodbc://ratib.nsamba:ratib.nsamba@localhost\\SQLEXPRESS/AgentNetworkOperations?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=Yes'
    )
