# coding=utf-8
"""Deal with label-related APIs."""
from flask_restplus import Namespace, Resource, reqparse
from flask_login import login_required,current_user
from flask import request
from ..model import labels, jobs, images
from .utils import get_message_json, handle_internal_error, HTTPStatus, ConstantCodes, convert_to_int_default0

api = Namespace('labels')


@api.route('/<int:label_id>')
class LabelResource(Resource):
    """Deal with single label."""

    @login_required
    def get(self, label_id):
        """Retrieve a single label by id."""
        try:
            if not current_user.is_admin()\
                    and current_user.account_id != jobs.find_job_by_label_id(label_id).account_id:
                return get_message_json('用户无法访问其他用户的标注信息'), HTTPStatus.FORBIDDEN
            result = labels.find_label_by_id(label_id)
            if result is None:
                return get_message_json('标注不存在'), HTTPStatus.NOT_FOUND
            json_res = result.to_json()
            json_res['message'] = '标注获取成功'
            return json_res, HTTPStatus.OK
        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
             )
    def put(self, label_id):
        """Edit a single label by id."""
        form = request.get_json()
        try:
            if not current_user.is_admin():
                the_job = jobs.find_job_by_label_id(label_id)
                if the_job is None:
                    return get_message_json('标注不存在'), HTTPStatus.NOT_FOUND
                if the_job.account_id != current_user.get_id():
                    return get_message_json('用户没有权限修改其他用户的标注信息'), HTTPStatus.FORBIDDEN
                elif the_job.job_state == ConstantCodes.Finished:
                    return get_message_json('用户无法修改已完成任务的标注信息'), HTTPStatus.FORBIDDEN
            elif images.find_image_by_label_id(label_id) is None:
                # The admin can only manage ground truth label
                return get_message_json('标注不存在'), HTTPStatus.NOT_FOUND

            result = labels.update_label_by_id(
                label_id,
                form.get('quality'),
                form.get('dr'),
                form.get('stage'),
                form.get('dme'),
                form.get('hr'),
                form.get('age_dme'),
                form.get('rvo'),
                form.get('crao'),
                form.get('myopia'),
                form.get('od'),
                form.get('glaucoma'),
                form.get('others'),
                form.get('comment')
            )
            if result == 1:
                json_res = form.copy()
                json_res['message'] = '标注修改成功'
                return json_res, HTTPStatus.OK
            else:
                return get_message_json('未知的标注修改错误'), HTTPStatus.BAD_REQUEST
        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    def delete(self, label_id):
        """Delete a single label by id."""
        try:
            if not current_user.is_admin():
                the_job = jobs.find_job_by_label_id(label_id)
                if the_job is None:
                    return get_message_json('标注不存在'), HTTPStatus.NOT_FOUND
                if the_job.account_id != current_user.get_id():
                    return get_message_json('用户没有权限删除其他用户的标注信息'), HTTPStatus.FORBIDDEN
                elif the_job.job_state == ConstantCodes.Finished:
                    return get_message_json('用户无法删除已完成任务的标注信息'), HTTPStatus.FORBIDDEN
            elif images.find_image_by_label_id(label_id) is None:
                # The admin can only manage ground truth label
                return get_message_json('标注不存在'), HTTPStatus.NOT_FOUND

            result = labels.delete_label_by_id(label_id)
            if result == 1:
                return get_message_json('标注删除成功'), HTTPStatus.OK
            else:
                return get_message_json('未知的标注删除错误'), HTTPStatus.BAD_REQUEST
        except Exception as err:
            return handle_internal_error(str(err))


@api.route('/')
class LabelsCollectionResource(Resource):
    """Deal with collection of labels."""

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
             )
    def post(self):
        """Create a label."""
        form = request.get_json()
        try:
            result = labels.add_label(
                form.get('quality'),
                form.get('dr'),
                form.get('stage'),
                form.get('dme'),
                form.get('hr'),
                form.get('age_dme'),
                form.get('rvo'),
                form.get('crao'),
                form.get('myopia'),
                form.get('od'),
                form.get('glaucoma'),
                form.get('others'),
                form.get('comment'))
    
            json_res = result.to_json()
            json_res['message'] = '标注创建成功'
            return json_res, HTTPStatus.CREATED
        except Exception as err:
            return handle_internal_error(str(err))