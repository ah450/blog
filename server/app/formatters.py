from flask.ext.restful import fields

user_fields = {
    'email': fields.String,
    'uri': fields.Url('user_ep')
}

post_fields = {
    'title': fields.String,
    'body': fields.String,
    'user': fields.Nested(user_fields),
    'uri': fields.Url('post_ep')
}

comment_fields = {
    'body': fields.String,
    'user': fields.Nested(user_fields),
    'uri': fields.Url('comment_ep')
}
