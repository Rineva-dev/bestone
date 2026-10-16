from app import app, db
from sqlalchemy import text  # ← tambahkan baris ini

with app.app_context():
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN kategori VARCHAR(100)"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN deskripsi_singkat VARCHAR(255)"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN materi TEXT"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN keuntungan TEXT"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN jadwal VARCHAR(200)"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN metode VARCHAR(100)"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN level VARCHAR(80)"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN biaya VARCHAR(100)"))
    db.session.execute(text("ALTER TABLE program_kursus ADD COLUMN syarat TEXT"))
    db.session.commit()
    print("✅ Semua kolom baru ditambahkan!")