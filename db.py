import sqlite3
from flask import g

DATABASE = 'ventas.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def create_tables():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Ventas (
            ID_SALES INTEGER PRIMARY KEY,
            RUC TEXT,
            NAME TEXT,
            COST_TOTAL REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DetalleVentas (
            ID INTEGER PRIMARY KEY,
            ID_SALES INTEGER,
            ID_PROD INTEGER,
            NOMBRE TEXT,
            NAME_PROD TEXT,
            UNIT INTEGER,
            AMOUNT INTEGER,
            COST REAL,
            TOTAL REAL,
            FOREIGN KEY (ID_SALES) REFERENCES Ventas(ID_SALES)
        )
    ''')
    db.commit()

def init_db(app):
    with app.app_context():
        create_tables()
        app.teardown_appcontext(close_db)

def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()