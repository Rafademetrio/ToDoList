import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from todoapp.auth import login_required
from .db import get_db

bp = Blueprint("pages", __name__, )

@bp.route('/')
def index():
    return render_template('pages/index.html')
    
    

@bp.route('/todo')
def index1():
    #exibe a lista de atividades:
    
    db = get_db()
    todolist = db.execute(
        "SELECT t.id, t.title, t.description, t.created_by, t.user_id, u.username, t.status"
        " FROM todo t JOIN user u ON t.user_id = u.id"
        " ORDER BY created_by DESC"
    ).fetchall()
    return render_template("pages/index1.html", todolists=todolist)


@bp.route('/create', methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        
        error = None
        
        if not title:
            error = "Título obrigatório."
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("INSERT INTO todo (title, description, user_id) VALUES (?, ?, ?)"), (title, description, g.user['id'],)
            db.commit()
            
            return redirect(url_for('pages.index1'))    
        
    return render_template('pages/create.html')
