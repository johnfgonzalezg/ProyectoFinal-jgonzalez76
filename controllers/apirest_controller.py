from flask import Blueprint, jsonify, render_template, request
from models.user import User
from models.ingredient import Ingredient
from models.product import Product
from controllers.product_controller import calculate_profitability, calculate_cost, calculate_calories
from controllers.ingredient_controller import its_healthy, supply, renew
from controllers.ice_cream_shop_controller import sell_product
from db import db
import requests
import json
from flask_login import current_user, login_required

apirest_bp = Blueprint('api', __name__, url_prefix='/api')

@apirest_bp.route('/', methods=['GET'], endpoint='api_index')
@login_required
def index():
    """
    Renderiza la página principal del API REST.

    Returns:
        Response: La página HTML `api.html`.
    """
    return render_template('api.html')

@apirest_bp.route('/product/all', methods=['GET'], endpoint='product_all')
def get_all_products():
    """
    Obtiene todos los productos de la base de datos.

    Returns:
        Response: JSON con la lista de todos los productos y estado 201.
    """
    products = Product.query.all()
    products_list = [product.to_dict() for product in products]
    return jsonify({'Productos': products_list}), 201

@apirest_bp.route('/product/id/<int:id>', methods=['GET'], endpoint='product_id')
def get_product_x_id(id):
    """
    Obtiene un producto por su ID y calcula sus calorías, costo y rentabilidad.

    Args:
        id (int): ID del producto.

    Returns:
        Response: JSON con los detalles del producto y estado 201, o mensaje de error y estado 404.
    """
    calculate_calories(id)
    calculate_cost(id)
    calculate_profitability(id)
    product = Product.query.get_or_404(id)
    if product:
        return jsonify({'Producto': product.to_dict()}), 201
    else:
        return jsonify({'Mensaje': 'No se encontró el producto'}), 404

@apirest_bp.route('/product/name/<string:name>', methods=['GET'], endpoint='product_name')
def get_product_x_name(name):
    """
    Obtiene un producto por su nombre.

    Args:
        name (string): Nombre del producto.

    Returns:
        Response: JSON con los detalles del producto y estado 201, o mensaje de error y estado 404.
    """
    product = Product.query.filter_by(name=name).first_or_404()
    if product:
        return jsonify({'Producto': product.to_dict()}), 201
    else:
        return jsonify({'Mensaje': 'No se encontró el producto'}), 404

@apirest_bp.route('/product/calories/<int:id>', methods=['GET'], endpoint='product_calories')
def get_product_calories(id):
    """
    Calcula y obtiene las calorías de un producto por su ID.

    Args:
        id (int): ID del producto.

    Returns:
        Response: JSON con las calorías del producto y estado 201, o mensaje de error y estado 404.
    """
    calculate_calories(id)
    product = Product.query.get_or_404(id)
    calories = product.calories
    if calories:
        return jsonify({'Calorias': calories}), 201
    else:
        return jsonify({'Mensaje': 'No se encontró el producto'}), 404

@apirest_bp.route('/product/profitability/<int:id>', methods=['GET'], endpoint='product_profitability')
@login_required
def get_product_profitability(id):
    """
    Calcula y obtiene la rentabilidad de un producto por su ID.

    Args:
        id (int): ID del producto.

    Returns:
        Response: JSON con la rentabilidad del producto y estado 201, o mensaje de error y estado 404.
    """
    print('current_user: ', current_user)
    if current_user.is_admin:
        calculate_profitability(id)
        product = Product.query.get_or_404(id)
        profitability = product.profitability
        if profitability:
            return jsonify({'Rentabilidad': profitability}), 201
        else:
            return jsonify({'Mensaje': 'No se encontró el producto'}), 404
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

@apirest_bp.route('/product/cost/<int:id>', methods=['GET'], endpoint='product_cost')
def get_product_cost(id):
    """
    Calcula y obtiene el costo de un producto por su ID.

    Args:
        id (int): ID del producto.

    Returns:
        Response: JSON con el costo del producto y estado 201, o mensaje de error y estado 404.
    """
    calculate_cost(id)
    product = Product.query.get_or_404(id)
    cost = product.cost
    if cost:
        return jsonify({'Costo de produccion': cost}), 201
    else:
        return jsonify({'Mensaje': 'No se encontró el producto'}), 404

@apirest_bp.route('/product/sold/<string:name>', methods=['GET'], endpoint='product_sold')
def sold(name):
    """
    Vende un producto por su nombre.

    Args:
        name (string): Nombre del producto.

    Returns:
        Response: JSON con el mensaje de venta y estado 201, o mensaje de error y estado 404.
    """
    sold_product = sell_product(name)
    message_formatted = jsonify({'Mensaje de Venta': sold_product}), 201
    print('Mensaje vender producto: ' + str(message_formatted))
    if isinstance(message_formatted, tuple):
        return message_formatted
    else:
        return jsonify({'Mensaje': 'No se encontró el producto'}), 404

@apirest_bp.route('/ingredient/all', methods=['GET'], endpoint='ingredient_all')
@login_required
def get_all_ingredients():
    """
    Obtiene todos los ingredientes de la base de datos.

    Returns:
        Response: JSON con la lista de todos los ingredientes y estado 201.
    """
    if current_user.is_admin or current_user.is_employee:
        ingredients = Ingredient.query.all()
        ingredients_list = [ingredient.to_dict() for ingredient in ingredients]
        return jsonify({'Ingredientes': ingredients_list}), 201
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401


@apirest_bp.route('/ingredient/id/<int:id>', methods=['GET'], endpoint='ingredient_id')
@login_required
def get_ingredient_x_id(id):
    """
    Obtiene un ingrediente por su ID.

    Args:
        id (int): ID del ingrediente.

    Returns:
        Response: JSON con los detalles del ingrediente y estado 201, o mensaje de error y estado 401.
    """
    if current_user.is_admin or current_user.is_employee:
        ingredient = Ingredient.query.get_or_404(id)
        if ingredient:
            return jsonify({'Ingrediente': ingredient.to_dict()}), 201
        else:
            return jsonify({'Mensaje': 'No se encontró el producto'}), 404
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

@apirest_bp.route('/ingredient/name/<string:name>', methods=['GET'], endpoint='ingredient_name')
@login_required
def get_ingredient_x_name(name):
    """
    Obtiene un ingrediente por su nombre.

    Args:
        name (string): Nombre del ingrediente.

    Returns:
        Response: JSON con los detalles del ingrediente y estado 201, o mensaje de error y estado 401.
    """
    if current_user.is_admin or current_user.is_employee:
        ingredient = Ingredient.query.filter_by(name=name).first_or_404()
        if ingredient:
            return jsonify({'Ingrediente': ingredient.to_dict()}), 201
        else:
            return jsonify({'Mensaje': 'No se encontró el producto'}), 404
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

@apirest_bp.route('/ingredient/is_healthy/<int:id>', methods=['GET'], endpoint='ingredient_is_healthy')
@login_required
def get_ingredient_is_healthy(id):
    """
    Verifica si un ingrediente es sano.

    Args:
        id (int): ID del ingrediente.

    Returns:
        Response: JSON con el mensaje sobre la salud del ingrediente.
    """
    if current_user.is_admin or current_user.is_employee:
        return its_healthy(id)
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

@apirest_bp.route('/ingredient/supply/<int:id>', methods=['GET'], endpoint='ingredient_supply')
@login_required
def supply_ingredient(id):
    """
    Reabastece un ingrediente por su ID.

    Args:
        id (int): ID del ingrediente.

    Returns:
        Response: JSON con el mensaje de reabastecimiento y estado 201, o mensaje de error y estado 401.
    """
    if current_user.is_admin or current_user.is_employee:
        message_formatted = supply(id)
        print('Mensaje reabastecer: ' + str(message_formatted))
        if isinstance(message_formatted, tuple):
            return message_formatted
        else:
            return jsonify({'Mensaje': 'No se encontró el producto'}), 404
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

@apirest_bp.route('/ingredient/renew/<int:id>', methods=['GET'], endpoint='ingredient_renew')
@login_required
def renew_inventory(id):
    """
    Renueva un ingrediente por su ID.

    Args:
        id (int): ID del ingrediente.

    Returns:
        Response: JSON con el mensaje de renovación y estado 201, o mensaje de error y estado 401.
    """
    if current_user.is_admin or current_user.is_employee:
        message_formatted = renew(id)
        if isinstance(message_formatted, tuple):
            print('Renew entro al if: ' + str(message_formatted))
            return message_formatted
        else:
            print('Renew No entro al if')
            return jsonify({'Mensaje': 'No se encontró el producto'}), 404
    else:
        return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

@apirest_bp.route('/query', methods=['GET'], endpoint='api_query')
@login_required
def query():
    """
    Realiza una consulta al API REST y muestra los resultados.

    Returns:
        Response: Página HTML `api.html` con los resultados de la consulta en formato JSON.
    """
    base_url = "https://proyectofinal-jgonzalez76-production.up.railway.app/api"
    endpoint = request.args.get('endpoint')
    param1 = request.args.get('param1')
    param2 = request.args.get('param2')

    # Construir la URL de consulta con los parámetros
    if endpoint == 'product/all' or endpoint == 'ingredient/all':
        query_url = f"{base_url}/{endpoint}"
    elif endpoint == 'product/name' or endpoint == 'ingredient/name' or endpoint == 'product/sold':
        query_url = f"{base_url}/{endpoint}/{param2}"
    else:
        query_url = f"{base_url}/{endpoint}/{param1}"

    print('URL Query: ' + query_url)
    try:
        response = requests.get(query_url, cookies=request.cookies, allow_redirects=False)  # No seguir redirecciones
        response.raise_for_status()  # Levantar una excepción si hay un error en la solicitud
        print('response: ', response.text)
        if response.status_code == 200 or response.status_code == 201:
            if response.text:
                results = response.json()
                results_formatted = json.dumps(results, indent=4)
            else:
                results_formatted = "Error: Respuesta vacía de la API"
        else:
            results_formatted = f"Error en la consulta: Código de estado {response.status_code}"
    except requests.RequestException as e:
        results_formatted = f"Error en la consulta: {e}"
    except json.JSONDecodeError:
        results_formatted = "Error: Respuesta no es un JSON válido"

    return render_template('api.html', results=results_formatted)
