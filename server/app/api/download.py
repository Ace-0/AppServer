# coding=utf-8
"""Deal with download-related APIs."""
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user
from flask import request
from ..model import accounts
from .utils import *


api = Namespace('download')


@api.route('/')
class DownloadResource(Resource):
    """Deal with personal csv file download."""

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('account_id', type=str, required=False, help='account_id', location='args')
             )
    def get(self):
        """Retrieve a single csv file by id."""
        try:
            if not current_user.is_admin():
                return get_message_json('只有管理员有下载权限'), HTTPStatus.FORBIDDEN
            account_id = convert_to_int(request.args.get('account_id'))
            if account_id:
                account = accounts.find_account_by_id(account_id)
                if account is None:
                    return get_message_json('用户不存在'), HTTPStatus.NOT_FOUND
                csv_personal_file = os.path.join(
                    os.path.join(os.environ['HOME'], current_app.config['CSV_PERSONAL_FOLDER']),
                    account.username + '.csv')
                return send_csv_file(csv_personal_file)
            else:
                csv_all_file = os.path.join(
                    os.path.join(os.environ['HOME'], current_app.config['CSV_ALL_FOLDER']), 'all_labels.csv')
                return send_csv_file(csv_all_file)
        except Exception as err:
            return handle_internal_error(str(err))
