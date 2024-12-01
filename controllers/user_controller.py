from models.user import User
from db import db
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    try:
        print('Request method: ' + request.method)
        if request.method == 'GET':
            print('Login GET')
            return render_template('login.html')
        elif request.method == 'POST':
            print('Login POST')
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                print('Encontró el usuario')
                welcome_message = f'¡Bienvenido a mi proyecto Flask, {user.username}!'
                flash(welcome_message, 'success')
                login_user(user)
                print('welcome_message: ' + welcome_message)
                if user.is_admin:
                    return redirect(url_for('user.admin_dashboard') )
                elif user.is_employee:
                    return redirect(url_for('user.employee_dashboard'))
                else:
                    return redirect(url_for('user.client_dashboard'))
            else:
                print('No encontró el usuario')
                flash('Usuario y/o password incorrectos', 'danger')
                return redirect(url_for('user.login'))
    except Exception as e:
        flash(str(e))
        print('Error login: ' + str(e))
        return redirect(url_for('user.login'))

@user_bp.route('/employee_dashboard', methods = ['GET'], endpoint = 'employee_dashboard')
@login_required
def user_dashboar():
    return render_template('employee_dashboard.html')

@user_bp.route('/admin_dashboard', methods = ['GET'], endpoint = 'admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@user_bp.route('/client_dashboard', methods = ['GET'], endpoint = 'client_dashboard')
@login_required
def client_dashboard():
    return render_template('client_dashboard.html')

@user_bp.route('/logout', methods=['GET'], endpoint='logout')
@login_required 
def logout(): 
    logout_user() 
    return redirect(url_for('index'))

def load_user(user_id):
    return User.query.get(int(user_id))


