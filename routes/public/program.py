from flask import Blueprint, render_template, abort
from models.database import ProgramKursus

program_bp = Blueprint('public_program', __name__)

@program_bp.route('/program/<kode_program>')
def detail(kode_program):
    program = ProgramKursus.query.filter_by(kode=kode_program).first()
    if not program:
        abort(404)
    return render_template('public/detail_program.html', program=program)