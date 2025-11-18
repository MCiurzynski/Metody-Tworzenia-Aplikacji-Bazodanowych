from flask import Blueprint, render_template

from flask_login import current_user
from app.db import db, MembershipType

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route('')
def index():
    if not current_user.is_authenticated:
        mem_types = db.session.execute(db.select(MembershipType).where(MembershipType.active == True)).scalars().all()
        return render_template('main/default.html', mem_types=mem_types)
    if current_user.role == 'employee':
        return render_template('main/employee.html')
    if current_user.role == 'trainer':
        return render_template('main/trainer.html')
    if current_user.role == 'client':
        return render_template('main/client.html')
    if current_user.role == 'owner':
        return render_template('main/owner.html')
    else:
        return render_template('main/default.html')