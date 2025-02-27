def get_sqlalchemy_db_url():
    """
    Returns the database URL for the application
    """
    return "postgresql+psycopg2://admin:securepassword@localhost:5432/users"
