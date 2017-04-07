import flask_sqlalchemy
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from .app import app

# Database Connection Object
db = flask_sqlalchemy.SQLAlchemy(app)

userRoles = {}


def initialize_user_roles(urls):
    for url in urls:
        userRoles[url] = ["admin"]


def add_to_user_roles(role_name, urls):
    for url in urls:
        userRoles[url].append(role_name)


# Base Class for Tables
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class Role(Base, RoleMixin):
    __tablename__ = 'auth_role'
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name, description, pages):
        self.name = name
        self.description = description
        self.pages = pages

    def set_description(self, description):
        self.description = description

    def to_string(self):
        return {"name": self.name, "description": self.description}

    def display(self):
        return {"name": self.name,
                "description": self.description}

    def __repr__(self):
        return '<Role %r>' % self.name


class User(Base, UserMixin):
    # Define Models
    roles_users = db.Table('roles_users',
                           db.Column('user_id', db.Integer(), db.ForeignKey('auth_user.id')),
                           db.Column('role_id', db.Integer(), db.ForeignKey('auth_role.id')))

    __tablename__ = 'auth_user'
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(45))
    current_login_ip = db.Column(db.String(45))
    login_count = db.Column(db.Integer)

    def display(self):
        return {"username": self.email,
                "roles": [role.to_string() for role in self.roles],
                "active": self.active}

    def set_roles(self, roles):
        for role in roles:
            if role and not self.has_role(role):
                q = user_datastore.find_role(role)
                if q:
                    user_datastore.add_role_to_user(self, q)

    def __repr__(self):
        return self.email


# Setup Flask Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
