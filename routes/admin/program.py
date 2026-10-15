from flask import Blueprint, render_template, session, redirect, url_for, request
from models.database import db, ProgramKursus

program_bp = Blueprint('admin_program', __name__, url_prefix='/admin')

def cek_login():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login.login'))

@program_bp.route('/program')
def daftar_program():
    cek = cek_login()
    if cek: return cek
    daftar = ProgramKursus.query.order_by(ProgramKursus.nama).all()
    return render_template('admin/program_kursus.html',
        halaman='program',
        daftar=daftar
    )

@program_bp.route('/program/tambah', methods=['POST'])
def tambah():
    cek = cek_login()
    if cek: return cek
    nama = request.form.get('nama', '').strip()
    kode = ProgramKursus.buat_kode_otomatis(nama)  # Kode otomatis
    
    program = ProgramKursus(
        kode=kode,
        nama=nama,
        deskripsi=request.form.get('deskripsi', '').strip(),
        durasi_nilai=request.form.get('durasi_nilai', type=int),
        durasi_satuan=request.form.get('durasi_satuan')
    )
    db.session.add(program)
    db.session.commit()
    return redirect(url_for('admin_program.daftar_program'))

@program_bp.route('/program/edit/<int:program_id>', methods=['POST'])
def edit(program_id):
    cek = cek_login()
    if cek: return cek
    p = ProgramKursus.query.get_or_404(program_id)
    nama_baru = request.form.get('nama', '').strip()
    
    # Kalau nama diubah, buat kode baru otomatis
    if nama_baru != p.nama:
        p.kode = ProgramKursus.buat_kode_otomatis(nama_baru)
    
    p.nama = nama_baru
    p.deskripsi = request.form.get('deskripsi', '').strip()
    p.durasi_nilai = request.form.get('durasi_nilai', type=int)
    p.durasi_satuan = request.form.get('durasi_satuan')
    db.session.commit()
    return redirect(url_for('admin_program.daftar_program'))

@program_bp.route('/program/hapus/<int:program_id>', methods=['POST'])
def hapus(program_id):
    cek = cek_login()
    if cek: return cek
    p = ProgramKursus.query.get_or_404(program_id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('admin_program.daftar_program'))

@program_bp.route('/daftar-untuk-header')
def daftar_program_header():
    daftar = ProgramKursus.query.order_by(ProgramKursus.nama).all()
    return {
        "programs": [
            {
                "kode": p.kode,
                "nama": p.nama,
                "deskripsi": p.deskripsi,
                "durasi_nilai": p.durasi_nilai,
                "durasi_satuan": p.durasi_satuan
            }
            for p in daftar
        ]
    }