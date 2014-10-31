import base64
from server import app, db, api
from models import User, Post, Comment
from parser import (posts_parser, users_parser, new_user_parser,
                    comment_parser, new_post_parser, new_comment_parser)
from flask import jsonify, g, request, abort
from flask.ext.restful import Resource, marshal_with
from functools import wraps
from formatters import user_fields, post_fields, comment_fields


def user_required(f):
    """
    Decorater that sets g.current_user according to authorization token.
    calls abort(403) if unable to verify token or no token in header.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.header.get('Authorization')
        if token:
            token = token.replace('Basic ', '', 1)
            try:
                token = base64.b64decode(token)
                g.current_user = User.verify_auth_token(token)
            except TypeError:
                abort(403)
        else:
            abort(403)


class TokenView(Resource):
    def post(self):
        """
        Logs in and creates a new token.
        """
        json = request.get_json()
        if json:
            username = json.get('username')
            password = json.get('password')
            user = User.query.get(username)
            if user and user.validate_password(password):
                token = user.gen_auth_token()
                return {'token': token}
            else:
                abort(403)
        else:
            abort(403)


class PostView(Resource):
    @marshal_with(post_fields)
    def get(self, id):
        """Returns a post by id."""
        post = Post.query.get(id)
        if post:
            return post
        else:
            abort(404)

    @user_required
    def put(self, id):
        """Updates a post."""
        args = posts_parser.parse_args()
        post = Post.get(id)
        if post is None:
            abort(404)
        elif g.current_user.is_author(post):
            title, body = args['title'], args['body']
            if title:
                post.title = title
            if body:
                post.body = body
            db.session.add(post)
            db.session.commit()
            return '', 204
        else:
            abort(403)


class PostsView(Resource):

    @user_required
    @marshal_with(post_fields)
    def get(self):
        """Returns posts belonging to a certain user."""
        return g.current_user.posts

    @user_required
    @marshal_with(post_fields)
    def post(self):
        """Creates a new post."""
        args = posts_parser.parse_args()
        title = args['title']
        body = args['body']
        new_post = Post(title, body, g.current_user)
        db.session.add(new_post)
        db.session.commit()
        return new_post


class UserView(Resource):
    @marshal_with(user_fields)
    def get(self, username):
        return User.query.get(username)

    @user_required
    @marshal_with(user_fields)
    def put(self, username):
        if g.current_user.username != username:
            abort(403)
        else:
            args = users_parser.parse_args()
            for key, value in args:
                setattr(g.current_user, key, value)
            db.session.add(g.current_user)
            db.session.commit()
            return g.current_user, 200

    @user_required
    def delete(self, username):
        if g.current_user.username != username:
            abort(403)
        else:
            db.session.delete(g.current_user)
            db.session.commit()
            return '', 204  # Success but no content


class UsersView(Resource):
    @marshal_with(user_fields)
    def post(self):
        args = new_user_parser.parse_args()
        user = User(username=args['username'], password=args['password'],
                    email=args['email'])
        db.session.add(user)
        db.session.commit()
        return user

    @marshal_with(user_fields)
    def get(self):
        return User.query.all()


class CommentView(Resource):
    @marshal_with(comment_fields)
    def get(self, id):
        return Comment.query.get(id)

    @user_required
    @marshal_with(comment_fields)
    def put(self, id):
        comment = Comment.query.get(id)
        if comment is None:
            abort(404)
        if g.current_user.is_author(comment):
            args = comment_parser.parse_args()
            if args['body']:
                comment.body = args['body']
                db.session.add(comment)
                db.session.commit()
            return comment
        else:
            abort(403)

    @user_required
    @marshal_with(comment_fields)
    def post(self, id):
        comment = Comment.query.get(id)
        if comment is None:
            abort(404)
        else:
            args = new_comment_parser.parse_args()
            new_comment = Comment(body=args['body'], user=g.current_user,
                                  parent=comment)
            db.session.add(new_comment)
            db.session.commit()
            return new_comment


class PostComments(Resource):
    @marshal_with(comment_fields)
    def get(self, id):
        post = Post.query.get(id)
        if post:
            return post.comments
        else:
            abort(404)

    @user_required
    def post(self, id):
        post = Post.query.get(id)
        args = new_comment_parser.parse_args()
        if post:
            comment = Comment(body=args['body'], user=g.current_user,
                              parent=post)
            db.session.add(comment)
            db.session.commit()
            return '', 204
        else:
            abort(404)


class UserComments(Resource):
    @marshal_with(comment_fields)
    def get(self, username):
        user = User.query.get(username)
        if user:
            return user.comments
        else:
            abort(404)


class UserPosts(Resource):
    @marshal_with(post_fields)
    def get(self, username):
        user = User.query.get(username)
        if user:
            return user.posts
        else:
            abort(404)

    @user_required
    def post(self, username):
        args = new_post_parser.parse_args()
        post = Post(title=args['title'], body=args['body'],
                    user=g.current_user)
        db.session.add(post)
        db.session.commit()
        return '', 204


api.add_resource(TokenView, '/token')


api.add_resource(PostView, '/posts/<int:id>', endpoint='post_ep')
api.add_resource(PostsView, '/posts')
api.add_resource(PostComments, '/posts/<int:id>/comments')


api.add_resource(UsersView, '/users')
api.add_resource(UserView, '/users/<string:username>', endpoint='user_ep')
api.add_resource(UserPosts, '/users/<string:username>/posts')
api.add_resource(UserComments, '/users/<string:username>/comments')


api.add_resource(CommentView, '/comments/<int:id>', endpoint='comment_ep')


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': "Entity doesn't exist"}), 404


@app.errorhandler(403)
def forbidden(e):
    return jsonify({'error': 'Access Forbidden'}), 403
