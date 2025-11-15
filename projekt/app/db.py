from flask_sqlalchemy import SQLAlchemy
from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Date, Time
from datetime import date, time
import click
from flask import current_app
from flask_login import UserMixin
from passlib.hash import argon2

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256))
    
    role: Mapped[str] = mapped_column(String(20), nullable=False, default='client')

    client_profile: Mapped[Optional["Client"]] = relationship(back_populates="user", uselist=False)
    trainer_profile: Mapped[Optional["Trainer"]] = relationship(back_populates="user", uselist=False)

    def set_password(self, password):
        self.password_hash = argon2.hash(password)

    def check_password(self, password):
        return argon2.verify(password, self.password_hash)

class Client(db.Model):
    __tablename__ = "client"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(256), nullable=False)
    last_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pesel: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True, unique=True)

    memberships: Mapped[List["Membership"]] = relationship(back_populates="client")
    participations: Mapped[List["Participation"]] = relationship(back_populates="client")
    user: Mapped["User"] = relationship(back_populates="client_profile")

class Membership(db.Model):
    __tablename__ = "membership"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False) 
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))

    client: Mapped["Client"] = relationship(back_populates="memberships")

    def is_active(self):
        return self.start_date >= date.today() and self.end_date <= date.today()

class Trainer(db.Model):
    __tablename__ = "trainer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(256), nullable=False)
    last_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pesel: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True, unique=True)

    group_classes: Mapped[List["GroupClass"]] = relationship(back_populates="trainer")
    user: Mapped["User"] = relationship(back_populates="trainer_profile")

class GroupClass(db.Model):
    __tablename__ = "group_class"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    day: Mapped[int] = mapped_column(Integer, nullable=False) # 0=Pon, 1=Wt...
    start_hour: Mapped[time] = mapped_column(Time, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False) # w minutach

    trainer_id: Mapped[int] = mapped_column(ForeignKey("trainer.id"))

    trainer: Mapped["Trainer"] = relationship(back_populates="group_classes")
    participations: Mapped[List["Participation"]] = relationship(back_populates="group_class")

class Participation(db.Model):
    __tablename__ = "participation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    group_class_id: Mapped[int] = mapped_column(ForeignKey("group_class.id"))

    client: Mapped["Client"] = relationship(back_populates="participations")
    group_class: Mapped["GroupClass"] = relationship(back_populates="participations")

def init_db():
    with current_app.app_context():
        db.create_all()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database')

def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_admin_command)

def add_admin(username, email, password):
    existing_user = db.session.execute(
        db.select(User).where((User.username == username) | (User.email == email))
    ).scalar()
    
    if existing_user:
        click.echo(click.style(f"Błąd: Użytkownik {username} lub email {email} już istnieje!", fg='red'))
        return

    new_admin = User(
        username=username,
        email=email,
        role='admin'
    )
    
    new_admin.set_password(password)

    try:
        db.session.add(new_admin)
        db.session.commit()
        click.echo(click.style(f"Sukces! Administrator {username} został utworzony.", fg='green'))
    except Exception as e:
        db.session.rollback()
        click.echo(click.style(f"Wystąpił błąd bazy danych: {e}", fg='red'))

@click.command('add-admin')
@click.argument('username')
@click.argument('email')
@click.password_option()
def add_admin_command(username, email, password):
    """Clear the existing data and create new tables"""
    add_admin(username, email, password)
    click.echo('Added admin')