from flask import Blueprint, render_template

bp = Blueprint('beranda', __name__)

@bp.route('/')
def beranda():
    return render_template('public/index.html')