from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, current_user
from db import db, init_db
from dotenv import load_dotenv
from controllers.init_values import insert_initial_values
from models.ingredient import Ingredient
from models.product import Product
from models.user import User
import os
from controllers.ice_cream_shop_controller import ice_cream_shop_bp
from controllers.product_controller import product_bp
from controllers.ingredient_controller import ingredient_bp
from controllers.user_controller import user_bp
from controllers.apirest_controller import apirest_bp

load_dotenv()

app = Flask(__name__, template_folder = 'views')

secret_key = os.urandom(24)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'user.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.context_processor
def inject_user_roles():
    if current_user.is_authenticated:
        return {
            'is_logued': True,
            'is_admin': current_user.is_admin,
            'is_employee': current_user.is_employee
        }
    return {
            'is_logued': False,
            'is_admin': False,
            'is_employee': False
    }

@app.errorhandler(401) 
def unauthorized_error(error): 
    """ Maneja el error 401 Unauthorized y devuelve un mensaje JSON personalizado. 
    Args: 
        error: El error de autorización. 
    Returns: 
        Response: JSON con el mensaje de error personalizado y estado 401. 
    """ 
    return jsonify({'Mensaje': 'No se encuentra autorizado para realizar la operación'}), 401

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
app.config['SESSION_COOKIE_SECURE'] = True 
app.config['SESSION_COOKIE_HTTPONLY'] = True 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
 
db.init_app(app)
init_db(app)
insert_initial_values(app)

# Importa y registra los blueprints de los controladores
app.register_blueprint(ice_cream_shop_bp, url_prefix='/')
app.register_blueprint(product_bp, url_prefix='/product')
app.register_blueprint(ingredient_bp, url_prefix='/ingredient')
app.register_blueprint(user_bp)
app.register_blueprint(apirest_bp)

@app.route('/')
def index():
    welcome_message = request.args.get('welcome_message')
    print('index welcome_message: ' + str(welcome_message))
    return render_template('index.html')
    #return render_template('index.html', welcome_message=welcome_message)

if __name__ == '__main__':
    app.run(debug = True)