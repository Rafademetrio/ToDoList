import sqlite3
import click
from flask import current_app
from flask import g

def get_db():
    
    # reusa a conexao já existente
    
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db


def close_db(e=None):
    
    db = g.pop("db", None)
    
    if db is not None:
        db.close()
        

def init_db():
    
    #Exclui tudo e reclia as tabelas do banco
    db = get_db()
    
    with current_app.open_resource("ddl.sql") as f:
        db.executescript(f.read().decode("utf8"))
        

@click.command("init-db")
def init_db_command():
    #exclui tudo e recia as tabelas
    
    init_db()
    click.echo("Inicializando o Banco de Dados!")
    
    
def init_app(app):
    #registra a funcao do DB na fabrica de app
    
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)