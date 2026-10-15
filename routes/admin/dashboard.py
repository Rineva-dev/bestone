from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/admin')

def cek_login():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login.login'))

@dashboard_bp.route('/dashboard')
def dashboard():
    cek = cek_login()
    if cek:
        return cek

    return render_template('admin/dashboard.html',
        halaman='dashboard',
        total_pendaftar=0,
        pendaftar_bulan_ini=0,
        total_program=3,
        total_foto=0
    )