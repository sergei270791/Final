from flask import Blueprint
from flask import g, request, jsonify
import requests
from db import get_db


ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/ventas', methods=['POST'])
def crear_venta():
    data = request.get_json()
    ruc = data.get('ruc')
    cost_total = data.get('cost_total')
    id_producto = data.get('id_prod')
    cantidad = data.get('cantidad')

    stock_response = requests.get(f'http://localhost:8080/almacen/stock/{id_producto}')
    
    g.db = get_db()

    if stock_response.status_code == 200:
        stock_data = stock_response.json()
        stock = stock_data.get('stock')
        nombre_producto = stock_data.get('nombre')

        if cantidad > stock:
            return jsonify({'message': f'No hay suficiente stock para {nombre_producto} ({id_producto})'}), 400

        # Si hay suficiente stock, proceder con la creación de la venta
        cursor = g.db.cursor()
        cursor.execute('INSERT INTO Ventas (RUC, NAME, COST_TOTAL) VALUES (?, ?, ?)', (ruc, nombre_producto, cost_total))
        g.db.commit()

        # Actualizar el stock en el otro servidor
        stock_update_response = requests.post(f'http://localhost:8080/almacen/stock/{id_producto}', json={'amountSold': cantidad})
        if stock_update_response.status_code != 200:
            return jsonify({'message': 'Error al actualizar el stock en el servidor externo'}), 500

        return jsonify({'message': f'Venta de {nombre_producto} creada exitosamente y stock actualizado', 'ruc': ruc, 'nombre_producto': nombre_producto, 'costo_total': cost_total}), 201

    else:
        # Manejar el caso en que la solicitud de stock no fue exitosa
        return jsonify({'message': f'Error al obtener el stock para el producto con ID {id_producto}'}), 500




@ventas_bp.route('/ventas/<int:id_venta>', methods=['PUT'])
def actualizar_venta(id_venta):
    data = request.get_json()
    ruc = data.get('ruc')
    name = data.get('name')
    cost_total = data.get('cost_total')
    
    g.db = get_db()
    
    cursor = g.db.cursor()
    cursor.execute('UPDATE Ventas SET RUC=?, NAME=?, COST_TOTAL=? WHERE ID_SALES=?',
                   (ruc, name, cost_total, id_venta))
    g.db.commit()
    
    return jsonify({'message': f'Venta con ID {id_venta} actualizada'}), 200

@ventas_bp.route('/ventas/<int:id_venta>', methods=['DELETE'])
def eliminar_venta(id_venta):
    g.db = get_db()
    cursor = g.db.cursor()
    cursor.execute('DELETE FROM Ventas WHERE ID_SALES=?', (id_venta,))
    g.db.commit()
    
    return jsonify({'message': f'Venta con ID {id_venta} eliminada'}), 200

@ventas_bp.route('/ventas/<int:id_venta>/detalle', methods=['POST'])
def crear_detalle_venta(id_venta):
    g.db = get_db()
    data = request.get_json()
    id_prod = data.get('id_prod')
    nombre = data.get('nombre')
    name_prod = data.get('name_prod')
    unit = data.get('unit')
    amount = data.get('amount')
    cost = data.get('cost')
    total = data.get('total')
    
    cursor = g.db.cursor()
    cursor.execute('INSERT INTO DetalleVentas (ID_SALES, ID_PROD, NOMBRE, NAME_PROD, UNIT, AMOUNT, COST, TOTAL) '
                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (id_venta, id_prod, nombre, name_prod, unit, amount, cost, total))
    g.db.commit()
    
    return jsonify({'message': 'Detalle de venta creado exitosamente'}), 201


@ventas_bp.route('/ventas/<int:id_venta>/detalle/<int:id_detalle>', methods=['PUT'])
def actualizar_detalle_venta(id_venta, id_detalle):
    g.db = get_db()
    data = request.get_json()
    nombre = data.get('nombre')
    unit = data.get('unit')
    amount = data.get('amount')
    cost = data.get('cost')
    total = data.get('total')
    
    query = '''
        UPDATE DetalleVentas 
        SET NOMBRE=?, UNIT=?, AMOUNT=?, COST=?, TOTAL=?
        WHERE ID=? AND ID_SALES=?
    '''
    
    cursor = g.db.cursor()
    cursor.execute(query, (nombre, unit, amount, cost, total, id_detalle, id_venta))
    g.db.commit()
    
    return jsonify({'message': f'Detalle de venta con ID {id_detalle} actualizado'}), 200

@ventas_bp.route('/ventas', methods=['GET'])
def obtener_ventas():
    g.db = get_db()
    cursor = g.db.cursor()

    cursor.execute('SELECT * FROM Ventas')
    rows = cursor.fetchall()

    # Convertir cada fila en un diccionario
    ventas = []
    for row in rows:
        venta = {
            'ID_SALES': row[0],
            'RUC': row[1],
            'NAME': row[2],
            'COST_TOTAL': row[3]
        }
        ventas.append(venta)

    return jsonify(ventas), 200


@ventas_bp.route('/ventas/<int:id_venta>', methods=['GET'])
def obtener_venta_por_id(id_venta):
    # Lógica para obtener una venta por su ID
    # Ejemplo:
    g.db = get_db()
    
    cursor = g.db.cursor()
    cursor.execute('SELECT * FROM Ventas WHERE ID_SALES=?', (id_venta,))
    venta = cursor.fetchone()

    return jsonify(venta), 200
    #return jsonify({'message': f'Obtener venta con ID {id_venta}'}), 200

# Rutas para obtener detalles de ventas similares a las anteriores




@ventas_bp.route('/ventas/<int:id_venta>/detalle/<int:id_detalle>', methods=['DELETE'])
def eliminar_detalle_venta(id_venta, id_detalle):
    cursor = g.db.cursor()
    cursor.execute('DELETE FROM DetalleVentas WHERE ID=? AND ID_SALES=?', (id_detalle, id_venta))
    g.db.commit()
    
    return jsonify({'message': f'Detalle de venta con ID {id_detalle} eliminado'}), 200

@ventas_bp.route('/ventas/<int:id_venta>/detalle', methods=['GET'])
def obtener_detalles_venta(id_venta):
    #Lógica para obtener los detalles de venta asociados a una venta específica (por su ID)
    #Por ejemplo:
    cursor = g.db.cursor()
    cursor.execute('SELECT * FROM DetalleVentas WHERE ID_SALES=?', (id_venta,))
    detalles_venta = cursor.fetchall()

    return jsonify(detalles_venta), 200
    #return jsonify({'message': f'Obtener detalles de venta para venta con ID {id_venta}'}), 200

@ventas_bp.route('/ventas/<int:id_venta>/detalle/<int:id_detalle>', methods=['GET'])
def obtener_detalle_venta_por_id(id_venta, id_detalle):
    # Lógica para obtener un detalle de venta específico asociado a una venta (por sus IDs)
    # Por ejemplo:
    cursor = g.db.cursor()
    cursor.execute('SELECT * FROM DetalleVentas WHERE ID=? AND ID_SALES=?', (id_detalle, id_venta))
    detalle_venta = cursor.fetchone()

    return jsonify(detalle_venta), 200
    #return jsonify({'message': f'Obtener detalle de venta con ID {id_detalle} para venta con ID {id_venta}'}), 200
