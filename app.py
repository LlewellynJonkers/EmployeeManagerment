from flask import Flask, redirect, url_for,render_template, send_file, abort, request
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_required
from auth import auth_bp
from employee import employee_bp
from school import school_bp
from route import route_bp
from register import register_bp
from helpers import get_or_create
from models import db, User,District,Province, WorkWeek, File
from datetime import date, timedelta
import os

app = Flask(__name__, static_folder='lib', static_url_path='/lib')
migrate = Migrate(app, db)
#app = Flask(__name__)
app.secret_key = "pyeibeeipixleyusermanagementsecretkey"  # Change in production

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user_management.db"
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
app.register_blueprint(register_bp)

@app.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    return render_template("index.html")

@app.route("/admin/reset_all")
@login_required
def reset_all():
    db.drop_all()
    db.create_all()
    return redirect(url_for("index"))

def loadweeks():
    start_date = date(2025,6,2)
    end_date = date.today()
    
    weeks = []
    current = start_date
    week_index = 1
    while current <= end_date:
        end_week = current + timedelta(days=4)
        if end_week > end_date:
            break
        get_or_create(db.session,WorkWeek,defaults={"label":f"Week {str(week_index).zfill(2)}"},
                      start_date=current,end_date=end_week)
        current += timedelta(weeks=1)
        week_index+= 1
    db.session.commit()


@app.route("/admin/set_defaults")
@login_required
def set_defaults():
    loadweeks()
    return redirect(url_for("index"))

@app.route("/download/<int:file_id>")
@login_required
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)
    if not os.path.exists(file_record.file_path):
        abort(404)
    as_attachment = not request.args.get('inline')
    return send_file(file_record.file_path, as_attachment=as_attachment, download_name=file_record.filename)







if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)