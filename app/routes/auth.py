from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from app.models.usuario import Usuario
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('grafo.index'))
    
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        # Verificamos contraseña usando el hash de seguridad
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('grafo.index'))
        
        flash('Credenciales incorrectas. Inténtalo de nuevo.')
    
    # Se busca directamente en templates/
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if Usuario.query.filter_by(username=username).first():
            flash('Este usuario ya existe.')
            return redirect(url_for('auth.register'))
            
        # Encriptamos la contraseña para la base de datos
        hashed_pw = generate_password_hash(password)
        nuevo_usuario = Usuario(username=username, password=hashed_pw)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('auth.login'))
        
    # Se busca directamente en templates/
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))