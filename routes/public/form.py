from flask import Blueprint, render_template, request, redirect, url_for
from models.database import db, Periode, ProgramKursus, Pendaftar, Level
from datetime import datetime

form_bp = Blueprint('form', __name__)

# ===== PILIH PROGRAM — GABUNG SEMUA GELOMBANG AKTIF =====
@form_bp.route('/pilih-program')
def pilih_program():
    sekarang = datetime.now()
    
    # Ambil SEMUA gelombang yang sedang aktif
    semua_gelombang_aktif = []
    semua_periode = Periode.query.all()
    
    for p in semua_periode:
        if p.mulai and p.selesai and p.mulai <= sekarang <= p.selesai:
            semua_gelombang_aktif.append(p)
    
    if not semua_gelombang_aktif:
        return render_template('public/pilih_program.html', 
                               gelombang_aktif=None,
                               daftar_program=[],
                               program_kode={},
                               daftar_level_per_program={},
                               sumber_gelombang={})
    
    # 1. Kumpulkan semua program unik + gelombang yang membukanya
    daftar_program = []
    sudah_ada = set()
    program_dari_gelombang = {}  # nama_program → [daftar gelombang]
    
    for gelombang in semua_gelombang_aktif:
        if gelombang.program_dibuka:
            for nama_prog in gelombang.program_dibuka.split(','):
                nama_prog = nama_prog.strip()
                if nama_prog:
                    if nama_prog not in sudah_ada:
                        sudah_ada.add(nama_prog)
                        daftar_program.append(nama_prog)
                        program_dari_gelombang[nama_prog] = []
                    program_dari_gelombang[nama_prog].append(gelombang)
    
    # 2. Ambil kode program
    program_kode = {}
    semua_level = Level.query.all()
    daftar_level_per_program = {}
    sumber_gelombang = {}  # untuk referensi di halaman kalau perlu
    
    for nama_prog in daftar_program:
        prog = ProgramKursus.query.filter_by(nama=nama_prog).first()
        if prog:
            program_kode[nama_prog] = prog.kode
        
        # Kumpulkan SEMUA level yang diizinkan oleh SEMUA gelombang yang membuka program ini
        level_terkumpul = set()
        ada_gelombang_tanpa_level = False
        
        for gelombang in program_dari_gelombang[nama_prog]:
            if not gelombang.level_dibuka or gelombang.level_dibuka.strip() == '':
                # Gelombang ini TIDAK pilih level = langsung lanjut, TIDAK gabung level lain
                ada_gelombang_tanpa_level = True
            else:
                # Gelombang ini pilih level → tambahkan ke daftar
                for nama_lv in gelombang.level_dibuka.split(','):
                    nama_lv = nama_lv.strip()
                    if nama_lv:
                        level_terkumpul.add(nama_lv)
        
        # Tentukan level untuk program ini
        if ada_gelombang_tanpa_level and not level_terkumpul:
            # Semua gelombang yang membuka program ini TIDAK pilih level → langsung lanjut
            daftar_level_per_program[nama_prog] = None
        elif level_terkumpul:
            # Ada gelombang yang pilih level → tampilkan level tersebut
            daftar_level_per_program[nama_prog] = [
                lv for lv in semua_level 
                if lv.nama in level_terkumpul
            ]
        else:
            # Tidak ada level dipilih sama sekali → langsung lanjut
            daftar_level_per_program[nama_prog] = None
    
    return render_template('public/pilih_program.html',
        gelombang_aktif=semua_gelombang_aktif,
        daftar_program=daftar_program,
        program_kode=program_kode,
        daftar_level_per_program=daftar_level_per_program
    )

# ===== FORMULIR =====
@form_bp.route('/daftar')
def daftar():
    program_terpilih = request.args.get('program', '')
    level_kode = request.args.get('level', '')  # Terima parameter level
    sekarang = datetime.now()
    
    # Cari gelombang aktif yang memuat program ini
    gelombang_aktif = (
        Periode.query
        .filter(
            Periode.mulai <= sekarang,
            Periode.selesai >= sekarang
        )
        .order_by(Periode.mulai.desc(), Periode.id.desc())
        .all()
    )

    gelombang_aktif = next(
        (
            p for p in gelombang_aktif
            if p.program_dibuka
            and program_terpilih in [
                nama.strip()
                for nama in p.program_dibuka.split(',')
            ]
        ),
        None
    )

    if not gelombang_aktif:
        return redirect(url_for('form.pilih_program'))

    
    if not gelombang_aktif or not program_terpilih:
        return redirect(url_for('form.pilih_program'))
    
    # Ambil data level jika ada
    level_terpilih = None
    if level_kode:
        level_terpilih = Level.query.filter_by(kode=level_kode).first()
    
    return render_template('public/form.html',
        program_terpilih=program_terpilih,
        level_terpilih=level_terpilih,
        gelombang=gelombang_aktif
    )

# ===== KIRIM PENDAFTARAN =====
@form_bp.route('/kirim-pendaftaran', methods=['POST'])
def kirim_pendaftaran():
    sekarang = datetime.now()
    
    nama = request.form.get('nama', '').strip()
    whatsapp = request.form.get('whatsapp', '').strip()
    email = request.form.get('email', '').strip() or None
    alamat = request.form.get('alamat', '').strip()
    program = request.form.get('program', '').strip()
    level = request.form.get('level', '').strip()  # Terima level dari form
    catatan = request.form.get('catatan', '').strip()
    
    if not nama or not whatsapp or not program:
        return """
        <script>
        alert('❌ Nama, Nomor WhatsApp, dan Program wajib diisi!');
        window.history.back();
        </script>
        """
    
    # Cari gelombang yang aktif dan memuat program ini
    gelombang_aktif = None
    semua_periode = Periode.query.all()
    for p in semua_periode:
        if p.mulai and p.selesai and p.mulai <= sekarang <= p.selesai:
            daftar_valid = [prg.strip() for prg in p.program_dibuka.split(',')] if p.program_dibuka else []
            if program in daftar_valid:
                gelombang_aktif = p
                break
    
    if not gelombang_aktif:
        return redirect(url_for('form.pilih_program'))
    
    # Simpan pendaftaran
    pendaftar_baru = Pendaftar(
        periode_id=gelombang_aktif.id,
        nama=nama,
        whatsapp=whatsapp,
        email=email,
        alamat=alamat,
        program=program,
        level=level,
        catatan=catatan,
        
        # Tambahan baru
        jenis_kelamin=request.form.get('jenis_kelamin'),
        tempat_lahir=request.form.get('tempat_lahir'),
        tanggal_lahir=datetime.strptime(tgl, '%Y-%m-%d').date() if (tgl := request.form.get('tanggal_lahir')) else None,
        nomor_identitas=request.form.get('nomor_identitas'),
        telepon=request.form.get('telepon'),
        provinsi=request.form.get('provinsi'),
        kabupaten=request.form.get('kabupaten'),
        kecamatan=request.form.get('kecamatan'),
        kelurahan=request.form.get('kelurahan'),
        pendidikan=request.form.get('pendidikan'),
        tujuan_belajar=request.form.get('tujuan_belajar'),
        sumber_info=request.form.get('sumber_info'),
    )

    if not pendaftar_baru.id_pendaftar:
        pendaftar_baru.id_pendaftar = Pendaftar.buat_id_pendaftar(program)

    db.session.add(pendaftar_baru)
    db.session.commit()
    
    return redirect(url_for('form.konfirmasi', id_pendaftar=pendaftar_baru.id_pendaftar))

# ===== HALAMAN KONFIRMASI PENDAFTARAN =====
@form_bp.route('/konfirmasi/<id_pendaftar>')
def konfirmasi(id_pendaftar):
    pendaftar = Pendaftar.query.filter_by(
        id_pendaftar=id_pendaftar
    ).first_or_404()

    link_grup_wa = (
        pendaftar.periode.link_grup_wa
        if pendaftar.periode
        else None
    )

    return render_template(
        'public/konfirmasi.html',
        pendaftar=pendaftar,
        link_grup_wa=link_grup_wa
    )
