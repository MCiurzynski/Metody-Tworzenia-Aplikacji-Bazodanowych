from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from app.db import db, Client, Membership, MembershipType, Employee, Trainer, GroupClass
from flask_login import login_user, logout_user, login_required, current_user
from app.routes.auth import employee_required, owner_required
from app.forms import MembershipTypeForm, RegistrationForm, PersonForm, GroupClassForm, PersonDataForm
from flask import abort
from app.services import create_user_with_profile, search

gym_bp = Blueprint('gym', __name__, url_prefix='/')

@gym_bp.route('/membership/type')
@employee_required
def view_membership_types():
    stmt = db.select(MembershipType).order_by(MembershipType.active.desc())
    search_columns = ['name', 'price']
    stmt = search(stmt, search_columns, MembershipType)

    mem_types = db.session.execute(stmt).scalars().all()
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
    stmt = db.select(Employee).order_by(Employee.active.desc())

    search_columns = ['first_name', 'last_name', 'pesel', 'phone_number']

    stmt = search(stmt, search_columns, Employee)

    employees = db.session.execute(stmt).scalars().all()
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

    form = PersonDataForm(obj=employee) 
    
    if form.validate_on_submit():
        form.populate_obj(employee) 
        db.session.commit()
        flash('Zaktualizowano dane pracownika.', 'success')
        return redirect(url_for('gym.view_employees'))
        
    return render_template('gym/edit_employee.html', employee=employee, form=form)


@gym_bp.route('/trainer')
def view_trainers():
    stmt = db.select(Trainer).order_by(Trainer.active.desc())
    search_columns = ['first_name', 'last_name', 'pesel', 'phone_number']
    stmt = search(stmt, search_columns, Trainer)

    trainers = db.session.execute(stmt).scalars().all()
    return render_template('gym/view_trainers.html', trainers=trainers)

@gym_bp.route('/trainer/<int:id>')
def view_trainer(id):
    trainer = db.get_or_404(Trainer, id)
    return render_template('gym/view_trainer.html', trainer=trainer)

@gym_bp.route('/trainer/add', methods=['GET', 'POST'])
@owner_required
def add_trainer():
    form = RegistrationForm()
    if form.validate_on_submit():
        success, message = create_user_with_profile(form, 'trainer')
        if success:
            flash(message, 'success')
            return redirect(url_for('gym.view_trainers'))
        else:
            flash(message, 'danger')
    return render_template('gym/add_trainer.html', form=form)


@gym_bp.route('/trainer/<int:id>/delete', methods=['POST'])
@owner_required
def delete_trainer(id: int):
    trainer = db.get_or_404(Trainer, id)
    if len(trainer.group_classes) == 0:
        trainer.active = False
        db.session.commit()
        flash('Udało się usunąć trenera', 'success')
    else:
        flash('Nie udało się usunąć trenera. Ma on przypisane zajęcia grupowe', 'danger')
    return redirect(url_for('gym.view_trainers'))

@gym_bp.route('/trainer/<int:id>/edit', methods=['GET', 'POST'])
@owner_required
def edit_trainer(id: int):
    trainer = db.get_or_404(Trainer, id)
    form = PersonForm(obj=trainer)
    if form.validate_on_submit():
        form.populate_obj(trainer)
        db.session.commit()
        flash('Zaktualizowano dane trenera', 'success')
        return redirect(url_for('gym.view_trainers'))
    return render_template('gym/edit_trainer.html', form=form, trainer=trainer)


@gym_bp.route('/classes')
def view_classes():
    trainer_id = request.args.get('trainer_id', type=int)
    client_id = request.args.get('client_id', type=int)
    
    stmt = db.select(GroupClass)
    
    if client_id:
        stmt = stmt.join(GroupClass.participations).where(Participation.client_id == client_id)

    if trainer_id:
        stmt = stmt.where(GroupClass.trainer_id == trainer_id)

    stmt = stmt.order_by(GroupClass.day, GroupClass.start_hour)

    classes = db.session.execute(stmt).scalars().all()
    
    return render_template('gym/view_classes.html', classes=classes)

@gym_bp.route('/classes/<int:id>')
def view_class(id: int):
    group_class = db.get_or_404(GroupClass, id)
    return render_template('gym/view_class.html', group_class=group_class)

@gym_bp.route('/classes/add', methods=['GET', 'POST'])
@employee_required
def add_class():
    form = GroupClassForm()
    
    active_trainers = db.session.execute(
        db.select(Trainer).where(Trainer.active == True)
    ).scalars().all()
    
    form.trainer_id.choices = [
        (t.id, f"{t.first_name} {t.last_name}") for t in active_trainers
    ]
    if form.validate_on_submit():
        new_class = GroupClass(
            name=form.name.data,
            day=form.day.data,
            start_hour=form.start_hour.data,
            length=form.length.data,
            trainer_id=form.trainer_id.data
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        flash(f'Dodano zajęcia "{new_class.name}" do grafiku.', 'success')
        return redirect(url_for('gym.view_classes'))
    else:
        print(form.errors)
    return render_template('gym/add_class.html', form=form)

@gym_bp.route('/classes/<int:id>/delete', methods=['POST'])
@employee_required
def delete_class(id: int):
    group_class = db.get_or_404(GroupClass, id)
    db.session.delete(group_class)
    db.session.commit()
    return redirect(url_for('gym.view_classes'))

@gym_bp.route('/classes/<int:id>/edit', methods=['GET', 'POST'])
@employee_required
def edit_class(id: int):
    group_class = db.get_or_404(GroupClass, id)
    form = GroupClassForm(obj=group_class)
    active_trainers = db.session.execute(db.select(Trainer).where(Trainer.active == True)).scalars().all()

    form.trainer_id.choices = [(t.id, f'{t.first_name} {t.last_name}') for t in active_trainers]

    if form.validate_on_submit():
        form.populate_obj(group_class)
        db.session.commit()
        flash('Zaktualizowano dane zajęć grupowych', 'success')
        return redirect(url_for('gym.view_classes'))
    return render_template('gym/edit_class.html', form=form, group_class=group_class)

from app.db import Participation # Pamiętaj o imporcie modelu Participation!

@gym_bp.route('/classes/<int:id>/join', methods=['POST'])
@login_required 
def join_class(id):
    if current_user.role != 'client':
        flash('Tylko klienci mogą zapisywać się na zajęcia.', 'warning')
        return redirect(url_for('gym.view_classes'))

    client = current_user.person_profile #

    has_active_membership = any(m.is_active for m in client.memberships)
    
    if not has_active_membership:
        flash('Nie możesz się zapisać. Nie masz aktywnego karnetu!', 'danger')
        return redirect(url_for('gym.view_classes'))

    already_joined = any(p.group_class_id == id for p in client.participations)
    
    if already_joined:
        flash('Jesteś już zapisany na te zajęcia.', 'info')
        return redirect(url_for('gym.view_classes'))

    participation = Participation(
        client_id=client.id,
        group_class_id=id
    )
    db.session.add(participation)
    db.session.commit()
    
    flash('Pomyślnie zapisano na zajęcia!', 'success')
    return redirect(request.referrer or url_for('gym.view_classes'))


@gym_bp.route('/classes/<int:id>/leave', methods=['POST'])
@login_required
def leave_class(id):
    if current_user.role != 'client':
        return redirect(url_for('gym.view_classes'))

    client = current_user.person_profile

    participation = db.session.execute(
        db.select(Participation).where(
            Participation.client_id == client.id,
            Participation.group_class_id == id
        )
    ).scalar()

    if participation:
        db.session.delete(participation)
        db.session.commit()
        flash('Wypisano z zajęć.', 'info')
    else:
        flash('Nie byłeś zapisany na te zajęcia.', 'warning')

    return redirect(request.referrer or url_for('gym.view_classes'))