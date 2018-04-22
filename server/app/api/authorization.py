# coding=utf-8
"""Deal with authorization-related APIs."""
from flask_restplus import Namespace, Resource, reqparse

api = Namespace('authorization')


@api.route('/')
class AuthorizationResource(Resource):
    """Deal with user authorization."""

    def post(self):
        """Create authorization given username and password."""
        pass

    def delete(self):
        """Remove an authorization by token."""
        pass
