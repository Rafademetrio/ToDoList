import os
from flask import Flask


def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        
        DATABASE=os.path.join(app.instance_path, "todolist.sqlite")
    )
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
     
    from . import db   
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import todo
    app.register_blueprint(todo.bp)
    
    app.add_url_rule('/', endpoint="pages.index")
    
    return app



    
