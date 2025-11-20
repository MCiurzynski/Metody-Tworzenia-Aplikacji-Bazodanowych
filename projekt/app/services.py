from app.db import db, User, Client, Trainer, Employee
from flask import request

def create_user_with_profile(form_data, role):
    try:
        new_user = User(
            username=form_data.username.data,
            email=form_data.email.data,
            role=role
        )
        new_user.set_password(form_data.password.data)

        if role == 'client':
            profile = Client(
                first_name=form_data.first_name.data,
                last_name=form_data.last_name.data,
                pesel=form_data.pesel.data,
                phone_number=form_data.phone_number.data,
                user=new_user
            )
        elif role == 'trainer':
            profile = Trainer(
                first_name=form_data.first_name.data,
                last_name=form_data.last_name.data,
                pesel=form_data.pesel.data,
                phone_number=form_data.phone_number.data,
                user=new_user
            )
        elif role == 'employee':
            profile = Employee(
                first_name=form_data.first_name.data,
                last_name=form_data.last_name.data,
                pesel=form_data.pesel.data,
                phone_number=form_data.phone_number.data,
                user=new_user
            )
        else:
            raise ValueError("Nieznana rola")

        db.session.add_all([new_user, profile])
        db.session.commit()
        return True, "Konto zostało utworzone pomyślnie."

    except Exception as e:
        db.session.rollback()
        return False, f"Błąd bazy danych: {str(e)}"

def search(stmt, search_columns, table):
    search_query = request.args.get('search')

    if search_query:
        search_terms = search_query.split()
        
        for term in search_terms:
            term_pattern = f"%{term}%"

            or_filters = []
            for col_name in search_columns:
                column = getattr(table, col_name)
                or_filters.append(column.ilike(term_pattern))

            stmt = stmt.where(db.or_(*or_filters))
    return stmt
