import psycopg2
import sqlalchemy
from sqlalchemy import text


DSN = 'postgresql://postgres:nekokun@localhost:5432/diplom'
engine = sqlalchemy.create_engine(DSN)
connection = engine.connect()


def create_db():
    initial_connection = psycopg2.connect(
        database='diplom',
        user='postgres',
        password='nekokun',
        host='localhost',
        port='5432'
    )


def create_tables():
    connection.execute(text('''CREATE TABLE IF NOT EXISTS founduser (iduser integer PRIMARY KEY);'''))

def insert_users(found_user):
    if not connection.execute(text(f"SELECT iduser FROM founduser WHERE iduser = {found_user};")).fetchone():
        connection.execute(text(f"INSERT INTO founduser (iduser) VALUES ({found_user});"))


def check_users(found_user):
    if connection.execute(text(f"SELECT iduser FROM founduser WHERE iduser = {found_user};")).fetchone():
        return False
    return True
