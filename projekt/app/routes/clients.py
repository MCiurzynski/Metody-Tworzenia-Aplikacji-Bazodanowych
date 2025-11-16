import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, Client, Membership
from flask_login import login_user, logout_user, login_required, current_user
from app.routes.auth import employee_required
from app.forms import AssignMembershipForm

clients_bp = Blueprint('clients', __name__, url_prefix='/client')

@clients_bp.route('/')
@employee_required
def index():  # clients list
    stmt = db.select(Client)
    clients = db.session.execute(stmt).scalars().all()
    return render_template('clients/clients_list.html', clients=clients)

@clients_bp.route('/add', methods=['GET', 'POST'])
@employee_required
def add(): #add client
    if request.method == 'POST':
        pass            ## TODO
    return render_template('clients/add_client.html')

@clients_bp.route('/<int:id>')
@employee_required
def view_client(id: int): #select client
    client = db.session.get_or_404(Client, id)
    return render_template('clients/client_info.html', client=client)

@clients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@employee_required
def edit_client(id: int):
    if request.method == 'POST':
        pass            ## TODO
    return render_template('clients/edit_client.html')

@clients_bp.route('/<int:id>/membership')
@employee_required
def view_membership(id: int): #select membership
    client = db.session.get_or_404(Client, id)
    return render_template('clients/membership_info.html', client=client)

@clients_bp.route('/<int:id>/membership/add', methods=['GET', 'POST'])
@employee_required
def add_membership(id: int):
    if request.method == 'POST':
        pass            ## TODO
    return render_template('clients/add_membership.html')