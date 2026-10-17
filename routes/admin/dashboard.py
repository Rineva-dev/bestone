from flask import Blueprint, render_template, session, redirect, url_for
from models.database import db, Pendaftar, ProgramKursus
from datetime import datetime

dashboard_bp = Blueprint(
    'admin_dashboard',
    __name__,
    url_prefix='/admin'
)


def cek_login():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login.login'))


@dashboard_bp.route('/dashboard')
def dashboard():
    cek = cek_login()
    if cek:
        return cek

    # 1. Total seluruh pendaftar
    total_pendaftar = (
        db.session.query(db.func.count(Pendaftar.id))
        .scalar() or 0
    )

    # 2. Pendaftar yang mendaftar pada bulan dan tahun ini
    sekarang = datetime.now()
    awal_bulan = sekarang.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    if sekarang.month == 12:
        awal_bulan_berikutnya = awal_bulan.replace(
            year=sekarang.year + 1,
            month=1
        )
    else:
        awal_bulan_berikutnya = awal_bulan.replace(
            month=sekarang.month + 1
        )

    pendaftar_bulan_ini = (
        Pendaftar.query
        .filter(
            Pendaftar.waktu_daftar >= awal_bulan,
            Pendaftar.waktu_daftar < awal_bulan_berikutnya
        )
        .count()
    )

    # 3. Total program kursus yang tersimpan
    total_program = ProgramKursus.query.count()

    return render_template(
        'admin/dashboard.html',
        halaman='dashboard',
        total_pendaftar=total_pendaftar,
        pendaftar_bulan_ini=pendaftar_bulan_ini,
        total_program=total_program
    )