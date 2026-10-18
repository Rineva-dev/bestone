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
    if cek:
        return cek

    periode = Periode.query.get_or_404(periode_id)

    # Parameter pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Pilihan jumlah data per halaman
    pilihan_per_page = [10, 15, 25, 50, 100]

    if per_page not in pilihan_per_page:
        per_page = 10

    # Query pendaftar berdasarkan periode
    query = Pendaftar.query.filter_by(
        periode_id=periode.id
    ).order_by(
        Pendaftar.waktu_daftar.desc()
    )

    # Pagination
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return render_template(
        'admin/detail_pendaftar.html',
        halaman='pendaftar',
        periode=periode,
        daftar_pendaftar=pagination.items,
        pagination=pagination,
        per_page=per_page,
        pilihan_per_page=pilihan_per_page
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

# ===== TAMBAH PENDAFTAR SECARA MANUAL =====
@pendaftar_bp.route(
    '/pendaftar/tambah-manual/<int:periode_id>',
    methods=['GET', 'POST']
)
def tambah_manual(periode_id):
    cek = cek_login()
    if cek:
        return cek

    periode = Periode.query.get_or_404(periode_id)

    # Ambil program yang dibuka oleh gelombang ini
    daftar_nama_program = [
        nama.strip()
        for nama in (periode.program_dibuka or '').split(',')
        if nama.strip()
    ]

    daftar_program = ProgramKursus.query.filter(
        ProgramKursus.nama.in_(daftar_nama_program)
    ).order_by(ProgramKursus.nama.asc()).all()

    # Ambil level yang dibuka oleh gelombang ini
    daftar_nama_level = [
        nama.strip()
        for nama in (periode.level_dibuka or '').split(',')
        if nama.strip()
    ]

    daftar_level = Level.query.filter(
        Level.nama.in_(daftar_nama_level)
    ).order_by(Level.nama.asc()).all()

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        program = request.form.get('program', '').strip()
        level = request.form.get('level', '').strip()

        if not nama or not whatsapp or not program:
            return render_template(
                'admin/form_tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                error='Nama lengkap, WhatsApp, dan program wajib diisi.'
            )

        # Pastikan program memang dibuka pada gelombang ini
        if program not in daftar_nama_program:
            return render_template(
                'admin/form_tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                error='Program tidak tersedia pada gelombang ini.'
            )

        # Pastikan level valid jika diisi
        if level and level not in daftar_nama_level:
            return render_template(
                'admin/form_tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                error='Level tidak tersedia pada gelombang ini.'
            )

        tanggal_lahir = request.form.get('tanggal_lahir', '').strip()

        try:
            tanggal_lahir = (
                datetime.strptime(tanggal_lahir, '%Y-%m-%d').date()
                if tanggal_lahir else None
            )
        except ValueError:
            return render_template(
                'admin/ftambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                error='Format tanggal lahir tidak valid.'
            )

        pendaftar_baru = Pendaftar(
            periode_id=periode.id,
            nama=nama,
            whatsapp=whatsapp,
            email=request.form.get('email', '').strip() or None,
            alamat=request.form.get('alamat', '').strip() or None,
            program=program,
            level=level or None,
            jenis_kelamin=request.form.get('jenis_kelamin') or None,
            tempat_lahir=request.form.get('tempat_lahir', '').strip() or None,
            tanggal_lahir=tanggal_lahir,
            nomor_identitas=request.form.get('nomor_identitas', '').strip() or None,
            telepon=request.form.get('telepon', '').strip() or None,
            provinsi=request.form.get('provinsi', '').strip() or None,
            kabupaten=request.form.get('kabupaten', '').strip() or None,
            kecamatan=request.form.get('kecamatan', '').strip() or None,
            kelurahan=request.form.get('kelurahan', '').strip() or None,
            pendidikan=request.form.get('pendidikan') or None,
            tujuan_belajar=request.form.get('tujuan_belajar') or None,
            sumber_info=request.form.get('sumber_info') or None,
            catatan=request.form.get('catatan', '').strip() or None,
            status='Baru',
            sudah_bayar=False
        )

        # Gunakan waktu pendaftaran yang dibuat oleh model
        db.session.add(pendaftar_baru)
        db.session.flush()

        pendaftar_baru.id_pendaftar = Pendaftar.buat_id_pendaftar(
            pendaftar_baru.program,
            pendaftar_baru.waktu_daftar
        )

        db.session.commit()

        return redirect(
            url_for(
                'admin_pendaftar.detail',
                periode_id=periode.id
            )
        )

    return render_template(
        'admin/tambah_pendaftar.html',
        halaman='pendaftar',
        periode=periode,
        daftar_program=daftar_program,
        daftar_level=daftar_level
    )

@pendaftar_bp.route('/pendaftar/data/<int:pendaftar_id>')
def detail_data(pendaftar_id):
    cek = cek_login()
    if cek:
        return cek

    pendaftar = Pendaftar.query.get_or_404(pendaftar_id)

    return render_template(
        'admin/detail_data_pendaftar.html',
        halaman='pendaftar',
        pendaftar=pendaftar
    )

# ===== EDIT DATA PENDAFTAR =====
@pendaftar_bp.route('/pendaftar/edit/<int:pendaftar_id>', methods=['GET', 'POST'])
def edit_pendaftar(pendaftar_id):
    cek = cek_login()
    if cek:
        return cek

    p = Pendaftar.query.get_or_404(pendaftar_id)
    periode = Periode.query.get_or_404(p.periode_id)

    # Program dan level yang tersedia pada periode asal pendaftar
    daftar_nama_program = [
        nama.strip()
        for nama in (periode.program_dibuka or '').split(',')
        if nama.strip()
    ]

    daftar_program = ProgramKursus.query.filter(
        ProgramKursus.nama.in_(daftar_nama_program)
    ).order_by(ProgramKursus.nama.asc()).all()

    daftar_nama_level = [
        nama.strip()
        for nama in (periode.level_dibuka or '').split(',')
        if nama.strip()
    ]

    daftar_level = Level.query.filter(
        Level.nama.in_(daftar_nama_level)
    ).order_by(Level.nama.asc()).all()

    if request.method == 'POST':
        nama = request.form.get('nama', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        program = request.form.get('program', '').strip()
        level = request.form.get('level', '').strip()

        # Validasi data wajib
        if not nama or not whatsapp or not program:
            return render_template(
                'admin/tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                pendaftar=p,
                mode_edit=True,
                error='Nama lengkap, WhatsApp, dan program wajib diisi.'
            )

        if program not in daftar_nama_program:
            return render_template(
                'admin/tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                pendaftar=p,
                mode_edit=True,
                error='Program tidak tersedia pada periode ini.'
            )

        if level and level not in daftar_nama_level:
            return render_template(
                'admin/tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                pendaftar=p,
                mode_edit=True,
                error='Level tidak tersedia pada periode ini.'
            )

        tanggal_lahir_str = request.form.get(
            'tanggal_lahir', ''
        ).strip()

        try:
            tanggal_lahir = (
                datetime.strptime(
                    tanggal_lahir_str, '%Y-%m-%d'
                ).date()
                if tanggal_lahir_str else None
            )
        except ValueError:
            return render_template(
                'admin/tambah_pendaftar.html',
                halaman='pendaftar',
                periode=periode,
                daftar_program=daftar_program,
                daftar_level=daftar_level,
                pendaftar=p,
                mode_edit=True,
                error='Format tanggal lahir tidak valid.'
            )

        # Perbarui data pendaftar yang sudah ada
        p.nama = nama
        p.whatsapp = whatsapp
        p.program = program
        p.level = level or None

        p.email = request.form.get('email', '').strip() or None
        p.alamat = request.form.get('alamat', '').strip() or None
        p.jenis_kelamin = request.form.get('jenis_kelamin') or None
        p.tempat_lahir = (
            request.form.get('tempat_lahir', '').strip() or None
        )
        p.tanggal_lahir = tanggal_lahir
        p.nomor_identitas = (
            request.form.get('nomor_identitas', '').strip() or None
        )
        p.telepon = request.form.get('telepon', '').strip() or None

        p.provinsi = request.form.get('provinsi', '').strip() or None
        p.kabupaten = request.form.get('kabupaten', '').strip() or None
        p.kecamatan = request.form.get('kecamatan', '').strip() or None
        p.kelurahan = request.form.get('kelurahan', '').strip() or None

        p.pendidikan = request.form.get('pendidikan') or None
        p.tujuan_belajar = request.form.get('tujuan_belajar') or None
        p.sumber_info = request.form.get('sumber_info') or None
        p.catatan = request.form.get('catatan', '').strip() or None

        # Jangan mengubah periode_id, status, waktu_daftar,
        # id_pendaftar, atau status pembayaran saat edit profil.

        db.session.commit()

        return redirect(
            url_for(
                'admin_pendaftar.detail',
                periode_id=p.periode_id
            )
        )

    return render_template(
        'admin/tambah_pendaftar.html',
        halaman='pendaftar',
        periode=periode,
        daftar_program=daftar_program,
        daftar_level=daftar_level,
        pendaftar=p,
        mode_edit=True
    )