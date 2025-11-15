import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, User, Client
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/')

@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pesel = request.form['pesel']
        phone_number = request.form['phone_number']
        user = User(username=username, email=email)
        user.set_password(password)
        client = Client(first_name=first_name, last_name=last_name, pesel=pesel, phone_number=phone_number, user=user)
        db.session.add_all([user, client])
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.execute(db.select(User).where(User.username == username)).scalar()
        if user is None or not user.check_password(password):
            flash('Nieprawidłowy login lub hasło.')
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano pomyślnie.')
    return redirect(url_for('main.index'))

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('main.index'))
        return view(**kwargs)
    return wrapped_view