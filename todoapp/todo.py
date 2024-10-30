import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

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
            db.execute("INSERT INTO todo (title, description, user_id) VALUES (?, ?, ?)", (title, description, g.user['id']),)
            db.commit()
            
            return redirect(url_for('pages.index1'))    
        
    return render_template('pages/create.html')


def get_todo(id, check_user=True):
    todolist = (
        get_db()
        .execute(
            "SELECT t.id, t.title, t.description, t.created_by, t.user_id, u.username, t.status"
            " FROM todo t JOIN user u ON t.user_id = u.id"
            " WHERE t.id = ?", (id,),).fetchone()
    )
    
    if todolist is None:
        abort(404, f"ToDo-List id {id} não existe.")
        
    if check_user and todolist['user_id'] != g.user['id']:
        abort(403)
        
    return todolist


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    todolist = get_todo(id)

    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        status = True if request.form.get('status') == 'on' else False
        error = None

        if not title:
            error = "Título obrigatório."

        if error is not None:
            flash(error)

        else:
            db =  get_db()
            db.execute("UPDATE todo SET title = ?, description = ?, status = ? WHERE id = ?", 
                       (title, description, status, id) )
            db.commit()
            return redirect(url_for("pages.index1"))
    return render_template("./pages/update.html", todolist=todolist)    

@bp.route("/<int:id>/delete", methods=("POST", "GET"))
@login_required
def delete(id):
    get_todo(id)
    db = get_db()
    db.execute("DELETE FROM todo WHERE id = ?", (id,) )
    db.commit()
    
    return redirect(url_for("pages.index1"))

@bp.route("/<int:id>/complete", methods=("POST", "GET"))
@login_required
def complete(id):

    status = True

    db = get_db()
    db.execute("UPDATE todo SET status = ? WHERE id = ?", (status, id) )
    db.commit()

    return redirect(url_for("pages.index1"))
