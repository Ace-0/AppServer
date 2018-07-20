# coding=utf-8
"""Deal with authorization-related APIs."""
from sqlalchemy.exc import IntegrityError
from flask import request
from flask_restplus import Namespace, Resource
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from ..model import accounts
from .utils import get_message_json, handle_internal_error, HTTPStatus, ConstantCodes


api = Namespace('authorization')

@api.route('/')
class AuthorizationResource(Resource):
    """Deal with user authorization."""

    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
            )
    def post(self):
        """Create authorization given username and password."""

        req_json = request.get_json()
        if not req_json or not req_json.get('username') or not req_json.get('password'):
            return get_message_json('请求非法'), HTTPStatus.BAD_REQUEST
        
        req_username = req_json['username']
        req_password = req_json['password']
        try:
            accounts_list = accounts.find_account_by_username(req_username)
            if not accounts_list or len(accounts_list) == 0:
                return get_message_json('用户不存在'), HTTPStatus.UNAUTHORIZED
            
            account = accounts_list[0]
            if not check_password_hash(account.password, req_password):
                return get_message_json('密码错误'), HTTPStatus.UNAUTHORIZED
            
            if account.authority == ConstantCodes.Empty:
                return get_message_json('用户审核未通过'), HTTPStatus.UNAUTHORIZED

            login_user(account, remember=True)
            json_res = get_message_json('登录成功')
            json_res['account_id'] = account.account_id
            json_res['authority'] = account.authority
            return json_res, HTTPStatus.OK

        except IntegrityError as err:
            handle_internal_error(err.orig.args[1])
        except Exception as err:
            handle_internal_error(str(err))

    @login_required
    def delete(self):
        """Remove an authorization by token."""
        logout_user()
        return get_message_json('登出成功'), HTTPStatus.OK
