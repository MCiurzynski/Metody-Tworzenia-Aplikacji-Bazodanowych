import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, Client, Membership, MembershipType, Employee
from flask_login import login_user, logout_user, login_required, current_user
from app.routes.auth import employee_required, owner_required
from app.forms import MembershipTypeForm, RegistrationForm, PersonForm
from flask import abort
from app.services import create_user_with_profile

gym_bp = Blueprint('gym', __name__, url_prefix='/')

@gym_bp.route('/membership/type')
@employee_required
def view_membership_types():
    mem_types = db.session.execute(db.select(MembershipType)).scalars().all()
    return render_template('gym/view_membership_types.html', mem_types=mem_types)

@gym_bp.route('/membership/type/add', methods=['GET', 'POST'])
@owner_required
def add_membership_type():
    form = MembershipTypeForm()
    if form.validate_on_submit():
        new_type = MembershipType(
            name=form.name.data,
            price=form.price.data,
            duration=form.duration.data
        )
        db.session.add(new_type)
        db.session.commit()
        flash('Dodano nowy typ karnetu.', 'success')
        return redirect(url_for('gym.view_membership_types'))
        
    return render_template('gym/add_membership_type.html', form=form)

@gym_bp.route('/membership/type/<int:id>/delete', methods=['POST'])
@owner_required
def delete_membership_type(id: int):
    mem_type = db.session.get(MembershipType, id)
    if mem_type is None:
        abort(404, f'Karnet id {id} nie istnieje')
    mem_type.active = False
    db.session.commit()
    return redirect(url_for('gym.view_membership_types'))

@gym_bp.route('/membership/type/<int:id>/edit', methods=['GET', 'POST'])
@owner_required
def edit_membership_type(id: int):
    mem_type = db.session.get(MembershipType, id)
    if mem_type is None:
        abort(404, f'Karnet id {id} nie istnieje')
    
    form = MembershipTypeForm(obj=mem_type)
    
    if form.validate_on_submit():
        form.populate_obj(mem_type)
        db.session.commit()
        flash('Zaktualizowano typ karnetu.', 'success')
        return redirect(url_for('gym.view_membership_types'))
        
    return render_template('gym/edit_membership_type.html', form=form, type=mem_type)


@gym_bp.route('/employee')
@owner_required
def view_employees():
    employees = db.session.execute(db.select(Employee)).scalars().all()
    return render_template('gym/view_employees.html', employees=employees)

@gym_bp.route('/employee/<int:id>')
@owner_required
def view_employee(id: int):
    employee = db.session.execute(db.select(Employee).where(Employee.id == id)).scalar()
    if employee is None:
        abort(404, f'Pracownik {id} nie istnieje')
    return render_template('gym/view_employee.html', employee=employee)

@gym_bp.route('/employee/add', methods=['GET', 'POST'])
@owner_required
def add_employee():
    form = RegistrationForm()

    if form.validate_on_submit():
        success, message = create_user_with_profile(form, 'employee')
        if success:
            flash(message, 'success')
            return redirect(url_for('gym.view_employees'))
        else:
            flash(message, 'danger')
    return render_template('gym/add_employee.html', form=form)


@gym_bp.route('/employee/<int:id>/delete', methods=['POST'])
@owner_required
def delete_employee(id: int):
    employee = db.session.execute(db.select(Employee).where(Employee.id == id)).scalar()
    if employee is None:
        abort(404, f'Pracownik {id} nie istnieje')
    employee.active = False
    db.session.commit()
    return redirect(url_for('gym.view_employees'))
    

@gym_bp.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
@owner_required
def edit_employee(id: int):
    employee = db.session.execute(db.select(Employee).where(Employee.id == id)).scalar()
    form = PersonForm(obj=employee)
    if form.validate_on_submit():
        form.populate_obj(employee)
        db.session.commit()
        flash('Zaktualizowano dane pracownika.', 'success')
        return redirect(url_for('gym.view_employees'))
    return render_template('gym/edit_employee.html', employee=employee, form=form)


@gym_bp.route('/trainer')
@employee_required
def view_trainers():
    pass

@gym_bp.route('/trainer/<int:id>')
@employee_required
def view_trainer():
    pass

@gym_bp.route('/trainer/add', methods=['GET', 'POST'])
@owner_required
def add_trainer():
    pass

@gym_bp.route('/trainer/<int:id>/delete', methods=['GET', 'POST'])
@owner_required
def delete_trainer(id: int):
    pass

@gym_bp.route('/trainer/<int:id>/edit', methods=['GET', 'POST'])
@owner_required
def edit_trainer(id: int):
    pass

@gym_bp.route('/classes')
@employee_required
def view_classes():
    pass

@gym_bp.route('/classes/<int:id>')
@employee_required
def view_class(id: int):
    pass

@gym_bp.route('/classes/add')
@employee_required
def add_class():
    pass

@gym_bp.route('/classes/<int:id>/delete')
@employee_required
def delete_class(id: int):
    pass

@gym_bp.route('/classes/<int:id>/edit')
@employee_required
def edit_class(id: int):
    pass