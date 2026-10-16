from flask import Flask, render_template, request, redirect
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Impor dari folder models
from models.database import db, Pengguna

load_dotenv()
app = Flask(__name__)

from werkzeug.middleware.proxy_fix import ProxyFix

# Beri tahu Flask bahwa ada 1 lapis proxy di depan
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1 
)

@app.before_request
def force_https():
    # Hanya jika benar-benar lewat HTTPS dari proxy
    if request.headers.get("X-Forwarded-Proto") == "https":
        request.environ["wsgi.url_scheme"] = "https"

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
from routes.public.program import program_bp as public_program_bp

app.register_blueprint(beranda_bp)
app.register_blueprint(form_bp)
app.register_blueprint(login_bp, url_prefix='/admin')
app.register_blueprint(dashboard_bp)
app.register_blueprint(pendaftar_bp)
app.register_blueprint(program_bp)
app.register_blueprint(level_bp)
app.register_blueprint(public_program_bp, name='public_program')

# Buat Tabel
with app.app_context():
    db.create_all()
    print('✅ Basis data siap!')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)