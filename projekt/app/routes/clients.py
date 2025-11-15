import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, Client
from flask_login import login_user, logout_user, login_required, current_user
from app.routes.auth import admin_required

clients_bp = Blueprint('clients', __name__, url_prefix='/client')

@clients_bp.route('/')
@admin_required
def index(): #clients list
    sql = db.select(Client).scalars
    clients = db.session.execute(sql)
    return render_template('clients/clients_list.html', clients=clients)

@clients_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add(): #add client
    if request.method == 'POST':
        pass
    return render_template()

@clients_bp.route('/<int:id>')
@admin_required
def client(id: int): #select client
    pass

@clients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_client(id: int):
    pass

@clients_bp.route('/<int:id>/membership')
@admin_required
def membership(id: int): #select membership
    pass

@clients_bp.route('/<int:id>/membership/add', methods=['GET', 'POST'])
@admin_required
def add_membership(id: int):
    pass