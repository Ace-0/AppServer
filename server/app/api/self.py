# coding=utf-8
"""Deal with authorization-related APIs."""
from sqlalchemy.exc import IntegrityError
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user
from .utils import get_message_json, HTTPStatus

api = Namespace('self')


@api.route('/')
class SelfResource(Resource):
    """Deal with current user."""

    @login_required
    def get(self):
        """Retrieve account_id of current user."""
        json_res = get_message_json('ID获取成功')
        json_res['account_id'] = current_user.account_id
        return json_res, HTTPStatus.OK

