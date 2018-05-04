# coding=utf-8
"""Deal with account-related APIs."""
from flask_restplus import Namespace, Resource
from werkzeug.security import generate_password_hash
from flask import request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from ..model import accounts
from .utils import get_message_json, DB_ERR_CODES, handle_internal_error, HTTPStatus

api = Namespace('accounts')


@api.route('/<int:account_id>')
class AccountResource(Resource):
    """Deal with single account."""

    @login_required
    def get(self, account_id):
        """Retrieve a single account by id."""
        try:
            if current_user.authority != accounts.Accounts.ADMIN_AUTHORITY:
                if current_user.id != account_id:
                    json_res = {'message': '用户权限不够访问他人账户'}
                    return json_res, HTTPStatus.BAD_REQUEST
            result = accounts.find_account_by_id(account_id)
            if len(result) == 0:
                return get_message_json('用户ID不存在'), HTTPStatus.NOT_FOUND
            json_res = result[0].to_json()
            json_res['message'] = '用户获取成功'
            return json_res, HTTPStatus.OK
        except Exception as err:
            return handle_internal_error(str(err))

    @api.doc(parser=api.parser()
             .add_argument('username', type=str, required=True, help='用户名', location='form')
             .add_argument('nickname', type=str, required=True, help='昵称', location='form')
             .add_argument('password', type=str, required=True, help='密码', location='form')
             .add_argument('email', type=str, required=True, help='邮箱', location='form')
             .add_argument('photo', type=str, required=True, help='照片文件名', location='form')
             .add_argument('authority', type=int, required=True, help='权限', location='form')
             )
    @login_required
    def put(self, account_id):
        """Edit a single account by id."""
        form = request.form
        try:
            if current_user.authority != accounts.Accounts.ADMIN_AUTHORITY:
                if current_user.authority != int(form['authority']):
                    json_res = {'message': '用户权限不足以修改权限等级'}
                    return json_res, HTTPStatus.BAD_REQUEST
            result = accounts.update_account_by_id(
                account_id,
                form['username'],
                form['nickname'],
                generate_password_hash(form['password']),
                form['email'],
                form['photo'],
                form['authority']
            )
            if result == 1:
                json_res = form.copy()
                json_res['message'] = '修改用户信息成功'
                return json_res, HTTPStatus.OK
            else:
                return get_message_json('修改失败'), HTTPStatus.NOT_FOUND
        except Exception as err:
            return get_message_json(str(err)), HTTPStatus.BAD_REQUEST

    @login_required
    def delete(self, account_id):
        """Delete a single account by id."""
        try:
            if current_user.authority != accounts.Accounts.ADMIN_AUTHORITY:
                if current_user.id != account_id:
                    json_res = {'message': '用户权限不足以删除他人账户'}
                    return json_res, HTTPStatus.BAD_REQUEST
            result = accounts.delete_account_by_id(account_id)
            json_res = {}
            if result == 1:
                json_res['message'] = '删除成功'
                return json_res, HTTPStatus.NO_CONTENT
            else:
                json_res['message'] = '删除失败'
                return json_res, HTTPStatus.NOT_FOUND
        except Exception as err:
            return handle_internal_error(err)


@api.route('/')
class AccountsCollectionResource(Resource):
    """Deal with collection of accounts."""

    @login_required
    def get(self):
        """List all accounts."""
        try:
            if current_user.authority != accounts.Accounts.ADMIN_AUTHORITY:
                json_res = {'message': '用户权限不足以查看所有账户'}
                return json_res, HTTPStatus.BAD_REQUEST
            result = accounts.find_all_users()
            accounts_list = []
            for i, account in enumerate(result):
                accounts_list.append(account.to_json())
            json_res = {'message': '查找成功',
                        'data': accounts_list}
            return json_res, HTTPStatus.OK
        except Exception as err:
            return get_message_json(str(err))
    
    @api.doc(parser=api.parser()
             .add_argument('username', type=str, required=True, help='用户名', location='form')
             .add_argument('nickname', type=str, required=True, help='昵称', location='form')
             .add_argument('password', type=str, required=True, help='密码', location='form')
             .add_argument('email', type=str, required=True, help='邮箱', location='form')
             .add_argument('photo', type=str, required=True, help='照片文件名', location='form')
             )
    def post(self):
        """Create an account."""
        form = request.form
        try:
            result = accounts.add_account(
                form['username'],
                form['nickname'],
                generate_password_hash(form['password']),
                form['email'],
                form['photo']
            )
            json_res = result.to_json()
            # Return password before hashing
            json_res['password'] = form['password']
            json_res['message'] = '用户创建成功'

            return json_res, HTTPStatus.CREATED
        except IntegrityError as err:
            if err.orig.args[0] == DB_ERR_CODES.DUPLICATE_ENTRY:
                return get_message_json('用户名已存在'), HTTPStatus.CONFLICT
            else:
                return handle_internal_error(err.orig.args[1])

        except Exception as err:
            return handle_internal_error(str(err))
