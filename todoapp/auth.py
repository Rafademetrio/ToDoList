import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
    else:
        g.user =(
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


#cria uma rota para o usuario se registrar (/register)
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        
        #user = db.execute("SELECT * FROM user WHERE username = ?", (username)).fetchone()
        
        if not username:
            error = "Username obrigatório"
        elif not password:
            error = "Password obrigatório"
        
        if error is None:
            try:
                db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)),)
                db.commit()
            except db.IntegrityError:
                error = f"Usuário {username} já existe."
            else:
                return redirect(url_for('auth.login'))
        flash(error)
    
    return render_template("auth/register.html")


#cria uma rota para o login do usuario
@bp.route('/login', methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        
        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
        
        if user is None:
            error = "Username inválido."
        elif not check_password_hash(user["password"], password):
            error = "Password inválido."
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('pages.index1'))
        
        flash(error)
        
    return render_template('auth/login.html')


#cria uma rota para deslogar 
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('pages.index'))    
    

@bp.route('/')
def index():
    #return render_template('pages/index.html')
    return "hello"