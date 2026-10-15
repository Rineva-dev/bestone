from flask import Blueprint, render_template, session, redirect, url_for, request
from models.database import db, Periode, Pendaftar, ProgramKursus, Level
from datetime import datetime

pendaftar_bp = Blueprint('admin_pendaftar', __name__, url_prefix='/admin')

def cek_login():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login.login'))

# === DAFTAR SEMUA GELOMBANG ===
@pendaftar_bp.route('/pendaftar')
def pendaftar():
    cek = cek_login()
    if cek: return cek
    
    daftar_periode = Periode.query.order_by(Periode.dibuat_pada.desc()).all()
    daftar_program = ProgramKursus.query.order_by(ProgramKursus.nama).all()
    daftar_level = Level.query.order_by(Level.nama).all()
    
    return render_template('admin/pendaftar.html',
        halaman='pendaftar',
        daftar_periode=daftar_periode,
        daftar_program=daftar_program,
        daftar_level=daftar_level,
    )

# === HALAMAN DETAIL GELOMBANG + DAFTAR PENDAFTAR ===
@pendaftar_bp.route('/pendaftar/detail/<int:periode_id>')
def detail(periode_id):
    cek = cek_login()
    if cek: return cek
    
    periode = Periode.query.get_or_404(periode_id)
    daftar_pendaftar = Pendaftar.query.filter_by(periode_id=periode.id).order_by(Pendaftar.waktu_daftar.desc()).all()
    
    return render_template('admin/detail_pendaftar.html',
        halaman='pendaftar',
        periode=periode,
        daftar_pendaftar=daftar_pendaftar
    )

# === TAMBAH GELOMBANG ===
@pendaftar_bp.route('/pendaftar/periode-baru', methods=['POST'])
def periode_baru():
    cek = cek_login()
    if cek: return cek

    nama = request.form.get('nama', '').strip()
    mulai_str = request.form.get('mulai')
    selesai_str = request.form.get('selesai')
    kelas_mulai_str = request.form.get('kelas_mulai')
    
    program_dipilih = request.form.getlist('program_dibuka')
    program_dibuka = ', '.join(program_dipilih) if program_dipilih else ''
    level_dipilih = request.form.getlist('level_dibuka')
    level_dibuka = ', '.join(level_dipilih) if level_dipilih else ''
    
    biaya = request.form.get('biaya', type=int)
    diskon = request.form.get('diskon', type=int)
    link_grup_wa = request.form.get('link_grup_wa', '').strip()
    
    periode_baru = Periode(
        nama=nama,
        mulai=datetime.fromisoformat(mulai_str) if mulai_str else None,
        selesai=datetime.fromisoformat(selesai_str) if selesai_str else None,
        kelas_mulai=datetime.fromisoformat(kelas_mulai_str) if kelas_mulai_str else None,
        program_dibuka=program_dibuka,
        level_dibuka=level_dibuka,
        biaya=biaya,
        diskon=diskon,
        link_grup_wa=link_grup_wa
    )
    db.session.add(periode_baru)
    db.session.commit()
    return redirect(url_for('admin_pendaftar.pendaftar'))

# === KONFIRMASI PEMBAYARAN ===
@pendaftar_bp.route('/pendaftar/konfirmasi-bayar/<int:pendaftar_id>', methods=['POST'])
def konfirmasi_bayar(pendaftar_id):
    cek = cek_login()
    if cek: return cek

    p = Pendaftar.query.get_or_404(pendaftar_id)
    if not p.sudah_bayar:
        p.id_pendaftar = Pendaftar.buat_id_pendaftar(p.program, p.waktu_daftar)
        p.sudah_bayar = True
        db.session.commit()
    
    return redirect(url_for('admin_pendaftar.detail', periode_id=p.periode_id))

# === HAPUS GELOMBANG ===
@pendaftar_bp.route('/pendaftar/hapus/<int:periode_id>', methods=['POST'])
def hapus_periode(periode_id):
    cek = cek_login()
    if cek: return cek
    
    periode = Periode.query.get_or_404(periode_id)
    db.session.delete(periode)
    db.session.commit()
    
    return redirect(url_for('admin_pendaftar.pendaftar'))

# === AMBIL DATA PERIODE UNTUK MODAL UBAH ===
@pendaftar_bp.route('/pendaftar/api-periode/<int:periode_id>')
def api_periode(periode_id):
    from flask import jsonify
    cek = cek_login()
    if cek: return cek
    
    p = Periode.query.get_or_404(periode_id)
    program_list = [prg.strip() for prg in p.program_dibuka.split(',') if prg.strip()] if p.program_dibuka else []
    
    return jsonify({
        'nama': p.nama,
        'mulai': p.mulai.strftime('%Y-%m-%d') if p.mulai else '',
        'selesai': p.selesai.strftime('%Y-%m-%d') if p.selesai else '',
        'kelas_mulai': p.kelas_mulai.strftime('%Y-%m-%d') if p.kelas_mulai else '',
        'program_dibuka': program_list,
        'biaya': p.biaya,
        'diskon': p.diskon,
        'link_grup_wa': p.link_grup_wa,
        'level_dibuka': [lvl.strip() for lvl in p.level_dibuka.split(',') if lvl.strip()] if p.level_dibuka else []
    })

# === SIMPAN PERUBAHAN ===
@pendaftar_bp.route('/pendaftar/simpan-ubah/<int:periode_id>', methods=['POST'])
def simpan_ubah_periode(periode_id):
    cek = cek_login()
    if cek: return cek
    
    p = Periode.query.get_or_404(periode_id)
    
    p.nama = request.form.get('nama', '').strip()
    mulai_str = request.form.get('mulai')
    selesai_str = request.form.get('selesai')
    kelas_mulai_str = request.form.get('kelas_mulai')
    
    program_dipilih = request.form.getlist('program_dibuka')
    p.program_dibuka = ', '.join(program_dipilih) if program_dipilih else ''
    level_dipilih = request.form.getlist('level_dibuka')
    p.level_dibuka = ', '.join(level_dipilih) if level_dipilih else ''
    
    p.biaya = request.form.get('biaya', type=int)
    p.diskon = request.form.get('diskon', type=int)
    p.link_grup_wa = request.form.get('link_grup_wa', '').strip()
    
    p.mulai = datetime.fromisoformat(mulai_str) if mulai_str else None
    p.selesai = datetime.fromisoformat(selesai_str) if selesai_str else None
    p.kelas_mulai = datetime.fromisoformat(kelas_mulai_str) if kelas_mulai_str else None
    
    db.session.commit()
    return redirect(url_for('admin_pendaftar.pendaftar'))