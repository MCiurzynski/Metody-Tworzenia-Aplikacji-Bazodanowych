import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, User, Client
from app.forms import RegistrationForm, LoginForm
from app.services import create_user_with_profile
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        success, message = create_user_with_profile(form, role='client')
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()

    if form.validate_on_submit():

        user = db.session.execute(
            db.select(User).where(User.username == form.username.data)
        ).scalar()

        if user is None or not user.check_password(form.password.data):
            flash('Nieprawidłowy login lub hasło.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
            
        return redirect(next_page)

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano pomyślnie.')
    return redirect(url_for('main.index'))

def employee_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_authenticated or current_user.role != 'employee':
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view