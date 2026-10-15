from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.database import db, Level

level_bp = Blueprint('admin_level', __name__, url_prefix='/admin')

def cek_login():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login.login'))

@level_bp.route('/level')
def daftar_level():
    cek = cek_login()
    if cek: return cek
    daftar_level = Level.query.order_by(Level.kode).all()
    return render_template('admin/level.html', daftar_level=daftar_level)

@level_bp.route('/level/tambah', methods=['POST'])
def tambah():
    cek = cek_login()
    if cek: return cek
    
    kode = request.form.get('kode', '').strip().upper()
    nama = request.form.get('nama', '').strip()
    keterangan = request.form.get('keterangan', '').strip()
    
    # Cek kode sudah dipakai
    if Level.query.filter_by(kode=kode).first():
        flash(f"Kode {kode} sudah digunakan! Silakan pakai kode lain.", "error")
        return redirect(url_for('admin_level.daftar_level') + '#tambah')
    
    # Cek nama sudah dipakai
    if Level.query.filter_by(nama=nama).first():
        flash(f"Nama level '{nama}' sudah ada! Silakan gunakan nama lain.", "error")
        return redirect(url_for('admin_level.daftar_level') + '#tambah')
    
    level = Level(kode=kode, nama=nama, keterangan=keterangan)
    db.session.add(level)
    db.session.commit()
    flash(f"Level {kode} — {nama} berhasil ditambahkan!", "sukses")
    return redirect(url_for('admin_level.daftar_level'))

@level_bp.route('/level/edit/<int:level_id>', methods=['POST'])
def edit(level_id):
    cek = cek_login()
    if cek: return cek
    
    lv = Level.query.get_or_404(level_id)
    
    kode_baru = request.form.get('kode', '').strip().upper()
    nama_baru = request.form.get('nama', '').strip()
    keterangan_baru = request.form.get('keterangan', '').strip()
    
    # Cek kode dipakai orang lain
    if kode_baru != lv.kode and Level.query.filter_by(kode=kode_baru).first():
        flash(f"Kode {kode_baru} sudah digunakan oleh level lain!", "error")
        return redirect(url_for('admin_level.daftar_level') + f'#edit-{lv.id}')
    
    # Cek nama dipakai orang lain
    if nama_baru != lv.nama and Level.query.filter_by(nama=nama_baru).first():
        flash(f"Nama level '{nama_baru}' sudah dipakai!", "error")
        return redirect(url_for('admin_level.daftar_level') + f'#edit-{lv.id}')
    
    lv.kode = kode_baru
    lv.nama = nama_baru
    lv.keterangan = keterangan_baru
    db.session.commit()
    flash(f"Level berhasil diperbarui menjadi {kode_baru} — {nama_baru}!", "sukses")
    return redirect(url_for('admin_level.daftar_level'))

@level_bp.route('/level/hapus/<int:level_id>', methods=['POST'])
def hapus(level_id):
    cek = cek_login()
    if cek: return cek
    lv = Level.query.get_or_404(level_id)
    db.session.delete(lv)
    db.session.commit()
    flash(f"Level {lv.kode} — {lv.nama} telah dihapus.", "sukses")
    return redirect(url_for('admin_level.daftar_level'))