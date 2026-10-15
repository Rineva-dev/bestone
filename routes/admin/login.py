from flask import Blueprint, render_template, request, redirect, url_for, session

login_bp = Blueprint('login', __name__, url_prefix='/admin')

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "bestone2026"

# Halaman Login
@login_bp.route('/login')
def login():
    return render_template('admin/login.html')

# Proses Login
@login_bp.route('/proses-login', methods=['POST'])
def proses_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        # ✅ Arahkan ke dashboard yang ada di file dashboard.py
        return redirect(url_for('admin_dashboard.dashboard'))
    else:
        return render_template('admin/login.html', error="Nama pengguna atau kata sandi salah!")

# Logout
@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))