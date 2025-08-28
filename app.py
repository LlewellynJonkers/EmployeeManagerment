from flask import Flask, redirect, url_for,render_template
from flask_login import LoginManager, current_user
from auth import auth_bp
from employee import employee_bp
from school import school_bp
from route import route_bp
from models import db, User,District,Province
import os

app = Flask(__name__)
app.secret_key = "moresupersecretkey"  # Change in production

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app3"
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(school_bp)
app.register_blueprint(route_bp)

@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)