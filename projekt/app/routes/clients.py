import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, Client, Membership, MembershipType
from flask_login import login_user, logout_user, login_required, current_user
from app.routes.auth import employee_required
from app.forms import AssignMembershipForm, RegistrationForm, PersonForm
from app.services import create_user_with_profile

clients_bp = Blueprint('clients', __name__, url_prefix='/client')

@clients_bp.route('/')
@employee_required
def index():  # clients list
    clients = db.session.execute(db.select(Client)).scalars().all()
    return render_template('clients/clients_list.html', clients=clients)

@clients_bp.route('/add', methods=['GET', 'POST'])
@employee_required
def add(): #add client
    form = RegistrationForm()
    if form.validate_on_submit():
        success, message = create_user_with_profile(form, 'client')
        if success:
            flash(message, 'success')
            return redirect(url_for('clients.index'))
        else:
            flash(message, 'danger')

    return render_template('clients/add_client.html', form=form)

@clients_bp.route('/<int:id>')
@employee_required
def view_client(id: int): #select client
    client = db.get_or_404(Client, id)
    return render_template('clients/client_info.html', client=client)

@clients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@employee_required
def edit_client(id: int):
    client = db.get_or_404(Client, id)
    form = PersonForm(obj=client)
    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        flash('Zaktualizowano dane klienta', 'success')
        return redirect(url_for('clients.index'))
    return render_template('clients/edit_client.html', form=form, client=client)

@clients_bp.route('/<int:id>/delete', methods=['POST'])
@employee_required
def delete_client(id: int):
    client = db.get_or_404(Client, id)
    client.active = False
    db.session.commit()
    flash('Usunięto klienta', 'success')
    return redirect(url_for('clients.index'))

@clients_bp.route('/<int:id>/membership')
@employee_required
def view_membership(id: int): #select membership
    client = db.get_or_404(Client, id)
    return render_template('clients/membership_info.html', client=client)

@clients_bp.route('/<int:client_id>/membership/add', methods=['GET', 'POST'])
@employee_required
def add_membership(client_id: int):
    client=db.get_or_404(Client, client_id)
    form = AssignMembershipForm()
    active_mem_types = db.session.execute(db.select(MembershipType).where(MembershipType.active == True)).scalars().all()

    form.membership_type_id.choices = [
        (m.id, m.name) for m in active_mem_types
    ]
    if form.validate_on_submit():
        membership = Membership(
            start_date=form.start_date.data,
            client_id=client_id,
            type_id=form.membership_type_id.data
        )
        db.session.add(membership)
        db.session.commit()
        return redirect(url_for('clients.view_membership', id=client_id))
    return render_template('clients/add_membership.html', form=form, client=client)