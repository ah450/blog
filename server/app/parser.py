from flask.ext.restful import reqparse


posts_parser = reqparse.RequestParser()
posts_parser.add_argument('title', type=unicode, help='Post title')
posts_parser.add_argument('body', type=unicode, help='Post body')

new_post_parser = reqparse.RequestParser()
new_post_parser.add_argument('title', type=unicode, help='Post title',
                             required=True)
new_post_parser.add_argument('body', type=unicode, help='Post body',
                             required=True)


users_parser = reqparse.RequestParser()
users_parser.add_argument('username', type=unicode, help='Username')
users_parser.add_argument('email', type=unicode, help='Email')
users_parser.add_argument('password', type=unicode, help='Password')


new_user_parser = reqparse.RequestParser()
new_user_parser.add_argument('username', type=unicode, help='Username',
                             required=True)
new_user_parser.add_argument('email', type=unicode, help='Email',
                             required=True)
new_user_parser.add_argument('password', type=unicode, help='Password',
                             required=True)

comment_parser = reqparse.RequestParser()
comment_parser.add_argument('body', type=unicode, help='Comment text')

new_comment_parser = reqparse.RequestParser()
comment_parser.add_argument('body', type=unicode, help='Comment text',
                            required=True)
