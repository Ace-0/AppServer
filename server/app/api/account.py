# coding=utf-8
"""Deal with account-related APIs."""
from flask_restplus import Namespace, Resource, reqparse

api = Namespace('accounts')


@api.route('/<int:account_id>')
class AccountResource(Resource):
    """Deal with single account."""

    def get(self, account_id):
        """Retrieve a single account by id."""
        pass

    def put(self, account_id):
        """Edit a single account by id."""
        pass

    def delete(self, account_id):
        """Delete a single account by id."""
        pass


@api.route('/')
class AccountsCollectionResource(Resource):
    """Deal with collection of accounts."""

    # The url must provide username argument
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True, help='Username not provided!')

    def get(self):
        """List all accounts."""
        pass

    def post(self):
        """Create an account."""
        args = AccountsCollectionResource.parser.parse_args()
        pass
