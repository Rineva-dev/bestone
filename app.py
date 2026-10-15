from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Impor dari folder models
from models.database import db, Pengguna

load_dotenv()
app = Flask(__name__)

# ===== Konfigurasi =====
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'kunci-sementara-ganti-nanti'),
    SQLALCHEMY_DATABASE_URI='sqlite:///bestone.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=os.path.join('static', 'uploads')
)

# ===== Hubungkan Database =====
db.init_app(app)

# ===== Sistem Masuk Admin =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'  # Sesuaikan dengan nama blueprint kamu
login_manager.login_message = 'Silakan masuk terlebih dahulu'

@login_manager.user_loader
def load_user(user_id):
    return Pengguna.query.get(int(user_id))

# ===== Impor Rute =====
from routes.public.beranda import bp as beranda_bp
from routes.public.form import form_bp
from routes.admin.login import login_bp
from routes.admin.dashboard import dashboard_bp
from routes.admin.pendaftar import pendaftar_bp
from routes.admin.program import program_bp
from routes.admin.level import level_bp

app.register_blueprint(beranda_bp)
app.register_blueprint(form_bp)
app.register_blueprint(login_bp, url_prefix='/admin')
app.register_blueprint(dashboard_bp)
app.register_blueprint(pendaftar_bp)
app.register_blueprint(program_bp)
app.register_blueprint(level_bp)

# Buat Tabel
with app.app_context():
    db.create_all()
    print('✅ Basis data siap!')

if __name__ == '__main__':
    app.run(debug=True)