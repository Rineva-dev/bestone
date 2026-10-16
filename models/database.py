from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# ===== Model Pengguna Admin =====
class Pengguna(UserMixin, db.Model):
    __tablename__ = 'pengguna'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    kata_sandi = db.Column(db.String(255), nullable=False)

# ===== Model Program Kursus =====
class ProgramKursus(db.Model):
    __tablename__ = 'program_kursus'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(5), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(100))
    deskripsi_singkat = db.Column(db.String(255))
    deskripsi = db.Column(db.Text)
    materi = db.Column(db.Text)
    keuntungan = db.Column(db.Text)
    jadwal = db.Column(db.String(200))
    metode = db.Column(db.String(100))
    syarat = db.Column(db.Text)
    durasi_nilai = db.Column(db.Integer)
    durasi_satuan = db.Column(db.String(30))
    dibuat_pada = db.Column(db.DateTime, default=db.func.now())

    # Fungsi buat kode otomatis
    @staticmethod
    def buat_kode_otomatis(nama_baru):
        if not nama_baru:
            return 'P'
        
        nama = nama_baru.strip()
        kode = nama[0].upper()
        
        while True:
            ada = ProgramKursus.query.filter_by(kode=kode).first()
            if not ada:
                return kode
            
            tambahan = None
            for huruf in nama[1:]:
                if huruf.upper() != kode[0]:
                    tambahan = huruf.upper()
                    break
            
            if not tambahan:
                tambahan = 'X'
            
            kode = kode[0] + tambahan
            ada_lagi = ProgramKursus.query.filter_by(kode=kode).first()
            if not ada_lagi:
                return kode
            
            angka = 2
            while True:
                kode_angka = kode + str(angka)
                ada_angka = ProgramKursus.query.filter_by(kode=kode_angka).first()
                if not ada_angka:
                    return kode_angka
                angka += 1

# ===== Model Periode Pendaftaran =====
class Periode(db.Model):
    __tablename__ = 'periode'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    mulai = db.Column(db.DateTime)
    selesai = db.Column(db.DateTime)
    kelas_mulai = db.Column(db.DateTime)
    program_dibuka = db.Column(db.String(255))
    level_dibuka = db.Column(db.Text, nullable=True)
    biaya = db.Column(db.Integer)
    diskon = db.Column(db.Integer)
    link_grup_wa = db.Column(db.String(255))
    # Kolom 'aktif' TIDAK LAGI dipakai manual, dihapus cek lewat tanggal
    dibuat_pada = db.Column(db.DateTime, default=db.func.now())
    
    pendaftar = db.relationship('Pendaftar', backref='periode', lazy=True, cascade='all, delete-orphan')

    @property
    def biaya_akhir(self):
        if not self.biaya:
            return 0
        if not self.diskon:
            return self.biaya
        return int(self.biaya * (100 - self.diskon) / 100)

    # ✅ Status otomatis berdasarkan tanggal
    @property
    def sedang_aktif(self):
        from datetime import datetime
        sekarang = datetime.now()
        # Ada rentang tanggal → cek apakah sekarang di dalamnya
        if self.mulai and self.selesai:
            return self.mulai <= sekarang <= self.selesai
        # Hanya tanggal mulai
        if self.mulai:
            return sekarang >= self.mulai
        # Hanya tanggal selesai
        if self.selesai:
            return sekarang <= self.selesai
        # Tidak ada tanggal
        return False

    @staticmethod
    def buat_kode_otomatis(nama):
        # Contoh: "Kelas Bahasa Inggris Pemula" → "kelas-bahasa-inggris-pemula"
        import re
        kode = nama.lower()
        kode = re.sub(r'[^a-z0-9\s-]', '', kode)
        kode = re.sub(r'[\s-]+', '-', kode).strip('-')
        return kode

# ===== Model Pendaftar =====
class Pendaftar(db.Model):
    __tablename__ = 'pendaftar'
    id = db.Column(db.Integer, primary_key=True)
    periode_id = db.Column(db.Integer, db.ForeignKey('periode.id'), nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20))
    program = db.Column(db.String(100))
    
    # === TAMBAHKAN BARIS INI ===
    level = db.Column(db.String(20), nullable=True)
    
    email = db.Column(db.String(100), nullable=True)
    alamat = db.Column(db.Text, nullable=True)
    jenis_kelamin = db.Column(db.String(10))
    tempat_lahir = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.Date)
    nomor_identitas = db.Column(db.String(50))
    
    # Kontak tambahan
    telepon = db.Column(db.String(20))
    
    # Alamat bertingkat
    provinsi = db.Column(db.String(100))
    kabupaten = db.Column(db.String(100))
    kecamatan = db.Column(db.String(100))
    kelurahan = db.Column(db.String(100))
    
    # Informasi tambahan
    pendidikan = db.Column(db.String(50))
    tujuan_belajar = db.Column(db.String(50))
    sumber_info = db.Column(db.String(50))
    catatan = db.Column(db.Text, nullable=True)
    
    waktu_daftar = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(20), default='Baru')
    id_pendaftar = db.Column(db.String(20), unique=True)
    sudah_bayar = db.Column(db.Boolean, default=False)

    # Ambil kode dari ProgramKursus
    @staticmethod
    def ambil_kode_program(nama_program):
        prog = ProgramKursus.query.filter_by(nama=nama_program).first()
        if prog:
            return prog.kode
        if not nama_program:
            return 'X'
        return nama_program[0].upper()

    # Generate ID pendaftar lengkap
    @staticmethod
    def buat_id_pendaftar(program_nama, waktu_daftar=None):
        from datetime import datetime
        if not waktu_daftar:
            waktu_daftar = datetime.now()
        kode = Pendaftar.ambil_kode_program(program_nama)
        tahun = waktu_daftar.strftime('%Y')
        bulan = waktu_daftar.strftime('%m')
        
        # Cari nomor TERBESAR yang sudah ada, bukan sekadar COUNT
        awalan = f'{kode}{tahun}{bulan}'
        pendaftar_terakhir = Pendaftar.query.filter(
            Pendaftar.id_pendaftar.like(f'{awalan}%')
        ).order_by(Pendaftar.id_pendaftar.desc()).first()
        
        if not pendaftar_terakhir:
            nomor_berikutnya = 1
        else:
            # Ambil 4 digit terakhir dan tambah 1
            nomor_terakhir = int(pendaftar_terakhir.id_pendaftar[-4:])
            nomor_berikutnya = nomor_terakhir + 1
        
        nomor = str(nomor_berikutnya).zfill(4)
        return f'{awalan}{nomor}'

from datetime import datetime

# === TAMBAH MODEL INI DI BAWAH MODEL ProgramKursus ===
class Level(db.Model):
    __tablename__ = 'level'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(20), nullable=False, unique=True)
    nama = db.Column(db.String(100), nullable=False)
    keterangan = db.Column(db.Text, nullable=True)
    
    # === TAMBAHKAN BARIS INI ===
    program_id = db.Column(db.Integer, db.ForeignKey('program_kursus.id'), nullable=True)
    # Hubungkan ke model ProgramKursus
    program = db.relationship('ProgramKursus', backref=db.backref('daftar_level', lazy=True))
    
    dibuat_pada = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Level: {self.kode} — {self.nama}>"