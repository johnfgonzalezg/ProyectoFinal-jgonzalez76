from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from db import db
from models.ingredient import Ingredient
from models.product import Product
from models.product_ingredient import ProductIngredient
from models.ingredient_type import IngredientType
from models.daily_sells import DailySells
from datetime import datetime
from decimal import Decimal
from controllers.product_controller import calculate_profitability, calculate_cost


ice_cream_shop_bp = Blueprint('ice_cream_shop', __name__)

@ice_cream_shop_bp.route('/', methods = ['GET'], endpoint = 'index')
def index():
    print('Entro a la función del index de la heladería')
    return render_template('index.html')

@ice_cream_shop_bp.route('/most_profitable_product', methods=['GET'], endpoint='most_profitable_product')
def most_profitable_product():
    products = Product.query.all()
    for product in products:
        calculate_cost(product.id)
        calculate_profitability(product.id)
    
    most_profitable_product = Product.query.order_by(Product.profitability.desc()).first()
    return render_template('most_profitable_product.html', product = most_profitable_product)

@ice_cream_shop_bp.route('/daily_sails', methods=['GET'], endpoint='daily_sails')
def daily_sails():
    today = datetime.today().date()
    daily_sail = DailySells.query.filter_by(sell_date = today).first()
    return render_template('daily_sails.html', daily_sail = daily_sail)

@ice_cream_shop_bp.route('/sold_product', methods=['GET', 'POST'], endpoint='sold_product')
def sold_product():
    ingredients = Ingredient.query.all()
    products = Product.query.all()
    sold_message = request.args.get('sold_message')
    if request.method == 'POST':
        try:
            id_product = request.form['sell_product']
            print('id_product: ' + str(id_product))
            product = Product.query.get_or_404(id_product)
            product_sold = sell_product(product.name)
            if product_sold == 'Vendido!':
                actual_date = datetime.today().date()
                daily_sell = DailySells.query.filter_by(sell_date=actual_date).first()
                if not daily_sell:
                    sell_date = actual_date
                    total_sell_value = product.public_price
                    daily_sell = DailySells(sell_date=sell_date, total_sell_value=total_sell_value)
                    db.session.add(daily_sell)
                    db.session.commit()
                else:
                    daily_sell.total_sell_value += product.public_price
                    db.session.commit()
                
            if 'api' in request.path:
                return jsonify({'Mensaje': product_sold}), 201
            else:
                return redirect(url_for('ice_cream_shop.sold_product', sold_message = product_sold))
        except ValueError as e:
            sold_message = str(e)
            if 'api' in request.path:
                return jsonify({'Mensaje': sold_message}), 201
            else:
                return redirect(url_for('ice_cream_shop.sold_product', sold_message = sold_message))
                print('Error: '+ str(e))
    return render_template('sold_product.html', products=products, sold_message = sold_message)

def sell_product(productName:str) -> bool:
    """
        Método para vender productos de la heladería de la siguiente manera:
            1. Recibe el nombre del producto a vender
            2. Valida en el menú de la heladería si el producto existe
            3. Si el producto existe, valida que haya existencias suficientes de los ingredientes para preparar el producto
            4. Si hay existencias de todos los ingredientes, hace la respectiva dismininución de cada ingrediente en el inventario
                para prepararlo
            5. Si se vende el producto, suma el valor del producto a las ventas del día
            6. Retorna True si se vendió el producto y False en caso contrario (que no se cumpla alguna de las condiciones anteriores) 

            **Parámetros:
                Entrada:
                    - productName(str): Nombre del producto a vender 
                Salida:
                    - productSold(bool): Bandera booleana que define si se vendió o no el producto 
    """
    productSold = False
    sold_product = Product.query.filter_by(name = productName).first()
    try:
        if sold_product != None:
            product_ingredients = ProductIngredient.query.filter_by(id_product = sold_product.id).all()
            for ingredient in product_ingredients:
                print(f'Checking stock for ingredient: {ingredient}')
                have_stock = check_stock(ingredient.id_ingredient)
                if not have_stock:
                    temp_ingredient = Ingredient.query.get_or_404(ingredient.id_ingredient)
                    raise ValueError(f'¡Oh no! Nos hemos quedado sin {temp_ingredient.name}')
            
            if have_stock == True:
                print('Hay stock de ingredientes')
                ingredients = Ingredient.query.all()
                id_ingredients = [pi.id_ingredient for pi in product_ingredients]
                for id_ingredient in id_ingredients:
                    print(f'id_ingredient to subtract: {id_ingredient}')
                    subtrack_stock(ingredients, id_ingredient)
                productSold = True
        else:
            raise ValueError('No existe el producto en el menu')
        return 'Vendido!'
    except ValueError as e:
        sold_message = str(e)
        return sold_message
        
def check_stock(id_ingredient: int) -> bool:
    """
        Método que recible una lista de ingredientes (las de cada producto) y valida hay existencias suficientes de dichos ingredientes 
        en el inventario de la heladería
        **Parámentros
            Entrada:
                - lstIngredients(list): Lista de ingredientes que se van a validar en el inventario
            Salida:
                - (bool): Retorna True si existe el ingrediente y además suficiente cantidad en el inventario, False en caso contrario
    """
    ingredient = Ingredient.query.filter_by(id = id_ingredient).first()
    if ingredient.id_ingredient_type == 1:
        if ingredient.quantity >= 1.0:
            return True
        else: 
            return False
    elif ingredient.id_ingredient_type == 2:
        if ingredient.quantity >= 0.2:
            return True
        else:
            return False


def subtrack_stock(ingredients_inventory: list, id_ingredient: int) -> None:
    """
        Método que recible una lista de ingredientes (las de cada producto) y resta la cantidad necesaria para preparar y vender un producto 
        determinado
        **Parámentros
            Entrada:
                - lstIngredients(list): Lista de ingredientes que se van a modificar en el inventario
    """
    
    for ingredient in ingredients_inventory:
        
        if id_ingredient == ingredient.id:
            print('Cantidad de ingrediente 1: ' + str(ingredient.quantity))
            if ingredient.id_ingredient_type == 1:
                ingredient.quantity = ingredient.quantity - Decimal(1.0)
            elif ingredient.id_ingredient_type == 2:
                ingredient.quantity = ingredient.quantity - Decimal(0.2)
            print('Cantidad de ingrediente 2: ' + str(ingredient.quantity))
    db.session.commit()