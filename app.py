from flask import Flask, g
from flask_cors import CORS
import sqlite3
from db import init_db, close_db

app = Flask(__name__)
CORS(app) 

# Configuración de la base de datos
app.config['DATABASE'] = 'ventas.db'

# Inicialización de la base de datos
init_db(app)

# Importar blueprints
from ventas.routes import ventas_bp

# Registrar blueprints
app.register_blueprint(ventas_bp)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def teardown_appcontext(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)