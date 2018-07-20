# coding=utf-8
"""Deal with account-related APIs."""
from flask_restplus import Namespace, Resource
from werkzeug.security import generate_password_hash
from flask import request
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from ..model import accounts, jobs
from .utils import *


api = Namespace('accounts')


@api.route('/<int:account_id>')
class AccountResource(Resource):
    """Deal with single account."""

    @login_required
    def get(self, account_id):
        """Retrieve a single account by id."""
        try:
            if not current_user.is_admin():
                if current_user.account_id != account_id:
                    return get_message_json('用户无法访问他人账号'), HTTPStatus.UNAUTHORIZED
            result = accounts.find_account_by_id(account_id)
            if result is None:
                return get_message_json('用户不存在'), HTTPStatus.NOT_FOUND
            json_res = result.to_json()
            json_res['message'] = '用户获取成功'
            return json_res, HTTPStatus.OK
        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
            )
    def put(self, account_id):
        """Edit a single account by id."""
        form = request.get_json()
        try:
            if not (validate_password(form.get('password'))
                    and validate_username(form.get('username'))
                    and validate_nickname(form.get('nickname'))):
                return get_message_json('用户信息格式有误'), HTTPStatus.BAD_REQUEST
            """doctor and guest can not modify their authority or other users' info"""
            """admin can not modify his authority"""
            """admin can not modify other users' authority as admin"""
            """admin can only modify authority of others"""
            if not current_user.is_admin():
                if account_id == current_user.account_id and form.get('authority') != current_user.authority:
                    return get_message_json('用户无法修改权限'), HTTPStatus.UNAUTHORIZED
                elif account_id != current_user.account_id:
                    return get_message_json('用户无法修改他人信息'), HTTPStatus.UNAUTHORIZED
                result = accounts.update_account_by_id(
                    account_id,
                    form.get('nickname'),
                    generate_password_hash(form.get('password')) if form.get('password') else None,
                    form.get('email'),
                    None,
                    None
                )
            elif current_user.is_admin() and account_id == current_user.account_id:
                result = accounts.update_account_by_id(
                    account_id,
                    form.get('nickname'),
                    generate_password_hash(form.get('password')) if form.get('password') else None,
                    form.get('email'),
                    None,
                    None
                )                   
            elif current_user.is_admin() and account_id != current_user.account_id:
                form_authority = form.get('authority')
                if form_authority is not None and not validate_authority_code(form_authority):
                    return get_message_json('权限不合法'), HTTPStatus.BAD_REQUEST
                if form_authority == ConstantCodes.Admin:
                    return get_message_json('管理员无法修改他人权限为管理员'), HTTPStatus.UNAUTHORIZED
                result = accounts.update_authority_by_id(account_id, form_authority)

            if result == 1:
                json_res = accounts.find_account_by_id(account_id).to_json()
                json_res['message'] = '用户修改成功'
                return json_res, HTTPStatus.OK
            else:
                return get_message_json('用户不存在'), HTTPStatus.NOT_FOUND
        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    def delete(self, account_id):
        """Delete a single account by id."""
        try:
            if not current_user.is_admin() and current_user.account_id != account_id:
                return get_message_json('用户无法删除他人账号'), HTTPStatus.UNAUTHORIZED
            elif current_user.is_admin() and current_user.account_id == account_id:
                return get_message_json('管理员不可删除'), HTTPStatus.UNAUTHORIZED
            result = accounts.delete_account_by_id(account_id)
            if result == 1:
                return get_message_json('用户删除成功'), HTTPStatus.NO_CONTENT
            else:
                return get_message_json('用户不存在'), HTTPStatus.NOT_FOUND
        except Exception as err:
            return handle_internal_error(str(err))


@api.route('/')
class AccountsCollectionResource(Resource):
    """Deal with collection of accounts."""

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('username', type=str, required=False, help='username', location='args')
             .add_argument('authority', type=int, required=False, help='authority', location='args')
            )
    def get(self):
        """List all accounts."""
        try:
            query_username = request.args.get('username')
            query_authority = request.args.get('authority')
            if not current_user.is_admin():
                return get_message_json('用户无法查看他人账号'), HTTPStatus.UNAUTHORIZED
            result = accounts.find_all_users()
            accounts_list = []
            
            for _, account in enumerate(result):
                if ((not query_username or (query_username == account.username)) and
                    (not query_authority or (int(query_authority) == account.authority))
                ):
                    accounts_list.append(account.to_json())

            json_res = {'message': '用户集合获取成功',
                        'data': accounts_list}
            return json_res, HTTPStatus.OK
        except Exception as err:
            return get_message_json(str(err))
    
    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
            )
    def post(self):
        """Create an account."""
        form = request.get_json()

        try:
            if not (validate_password(form.get('password'))
                    and validate_username(form.get('username'))
                    and validate_nickname(form.get('nickname'))):
                return get_message_json('用户信息格式有误'), HTTPStatus.BAD_REQUEST

            result = accounts.add_account(
                form.get('username'),
                form.get('nickname'),
                generate_password_hash(form.get('password')),
                form.get('email'),
                'default.png',
                ConstantCodes.Empty
            )
            json_res = result.to_json()
            json_res['message'] = '用户创建成功'

            return json_res, HTTPStatus.CREATED
        except IntegrityError as err:
            if err.orig.args[0] == DBErrorCodes.DUPLICATE_ENTRY:
                return get_message_json('用户名已存在'), HTTPStatus.CONFLICT
            else:
                return handle_internal_error(err.orig.args[1])

        except Exception as err:
            return handle_internal_error(str(err))


@api.route('/performance/<int:account_id>')
class AccountPerformanceResource(Resource):
    """Deal with account performance."""

    @login_required
    def get(self, account_id):
        """Get performance of an account."""
        try:
            if not current_user.is_admin() and current_user.account_id != account_id:
                return get_message_json('用户无法访问他人的工作统计量'), HTTPStatus.UNAUTHORIZED
            if accounts.find_account_by_id(account_id) is None:
                return get_message_json('用户不存在'), HTTPStatus.NOT_FOUND
            performance = jobs.get_performance_by_account_id(account_id)
            res = {
                'message': '工作统计量获取成功',
                'data': performance
            }
            return res, HTTPStatus.OK
        except Exception as err:
            return handle_internal_error(str(err))
