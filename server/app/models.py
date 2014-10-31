from server import db, app
from datetime import datetime
from validate_email import validate_email
from passlib.apps import custom_app_context as pwd_ctx
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature


class User(db.Model):
    username = db.Column(db.Unicode(250), nullable=False)
    email = db.Column(db.Unicode(254), primary_key=True, nullable=False,
                      unique=True)
    password_hash = db.Column(db.Unicode(254), nullable=False)
    posts = db.relationship('Post', backref='user',
                            cascade='all, delete, delete-orphan')
    comments = db.relationship('Comment', backref='user',
                               cascade='all, delete, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)

    @staticmethod
    def hash_password(password):
        """
        Returns password's hash.
        password - unicode, plain.
        """
        return pwd_ctx.encrypt(password)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        return User.query.get(data['email'])

    def __init__(self, username, email, password):
        """
            Initializes a new user.
            username - user name, unicode no spaces.
            email - unicode.
            password - unicode, plain. Note: will be hashed.
        """
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)

    def get_auth_token(self, expiration=600):
        """
        Generates an authentication token.
        """
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({
                        'username': self.username,
                        'email': self.email,
                        'password': self.password_hash
                        })

    def is_authenticated(self):
        return True  # All users are authenticated

    def is_active(self):
        return True  # All accounts are active

    def is_anonymous(self):
        return False

    def validate_password(self, password):
        """
        Returns true if password matches stored.
        password - unicode, plain
        """
        return pwd_ctx.verify(password, self.password_hash)

    def is_author(self, entity):
        """
        Returns True if this user is the author of entity.
        entity - A post or comment.
        """
        return entity.user.username == self.username

    @db.validates('email')
    def validate_email(self, key, email):
        assert validate_email(email)

    @db.validates('username')
    def validate_username(self, key, username):
        assert len(username) > 0
        assert username.count(' ') == 0

    @db.validates('password')
    def validates_password(self, key, password):
        assert len(password) > 0


class Entity(db.Model):
    __mapper_args__ = {'polymorphic_identity': 'entity'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)


class Post(Entity):
    __mapper_args__ = {'polymorphic_identity': 'post'}
    id = db.Column(db.Integer, db.ForeignKey('entity.id'), primary_key=True)
    title = db.Column(db.Unicode(250), nullable=False)
    body = db.Column(db.UnicodeText, nullable=False)
    user_id = db.Column(db.Unicode(250), db.ForeignKey('user.username'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

    @db.validates('title')
    def validates_title(self, key, title):
        assert len(title) > 5

    @db.validates('body')
    def validates_body(self, key, body):
        assert len(body) > 10


class Comment(Entity):

    id = db.Column(db.Integer, db.ForeignKey('entity.id'), primary_key=True)
    body = db.Column(db.UnicodeText, nullable=False)
    user_id = db.Column(db.Unicode(250), db.ForeignKey('user.username'))
    parent_id = db.Column(db.Integer, db.ForeignKey('entity.id'))
    parent = db.relationship('Entity', backref='comments',
                             foreign_keys=[parent_id])

    __mapper_args__ = {
        'polymorphic_identity': 'comment',
        'inherit_condition': (id == Entity.id)
    }

    def __init__(self, body, user, parent):
        self.body = body
        self.user = user
        self.parent = parent

    @db.validates('body')
    def validates_body(self, key, body):
        assert len(body) > 0
