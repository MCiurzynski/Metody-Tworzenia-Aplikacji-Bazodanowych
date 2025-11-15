from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, User
from flask_login import login_user, logout_user, login_required, current_user

main_bp = Blueprint('main', __name__, url_prefix='/')

@login_required
@main_bp.route('')
def index():
    if not current_user.is_authenticated:
        return render_template('main/default.html')
    if current_user.role == 'admin':
        return render_template('main/admin.html')
    if current_user.role == 'trainer':
        return render_template('main/trainer.html')
    if current_user.role == 'client':
        return render_template('main/client.html')
    else:
        return render_template('main/default.html')