from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Date, Time
from datetime import date, time
import click
from flask import current_app

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Client(db.Model):
    __tablename__ = "client"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(256), nullable=False)
    last_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pesel: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    email_address: Mapped[str] = mapped_column(String(256), nullable=False)

    memberships: Mapped[List["Membership"]] = relationship(back_populates="client")
    participations: Mapped[List["Participation"]] = relationship(back_populates="client")

class Membership(db.Model):
    __tablename__ = "membership"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False) 
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))

    client: Mapped["Client"] = relationship(back_populates="memberships")

class Trainer(db.Model):
    __tablename__ = "trainer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(256), nullable=False)
    last_name: Mapped[str] = mapped_column(String(256), nullable=False)
    pesel: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    email_address: Mapped[str] = mapped_column(String(256), nullable=False)

    group_classes: Mapped[List["GroupClass"]] = relationship(back_populates="trainer")

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
    app.cli.add_command(init_db_command)