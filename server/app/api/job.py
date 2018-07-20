# coding=utf-8
"""Deal with job-related APIs."""
from flask import request
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user
from ..model import jobs, images, accounts
from .utils import *
from sqlalchemy.exc import IntegrityError
import datetime

api = Namespace('jobs')


@api.route('/<int:job_id>')
class JobResource(Resource):
    """Deal with single job."""

    @login_required
    def get(self, job_id):
        """Retrieve a single job by id."""
        try:
            result = jobs.find_job_by_id(job_id)

            if result is None:
                return get_message_json('任务不存在'), HTTPStatus.NOT_FOUND

            # Admin can retrieve any job,
            # while others can only retrieve his own job
            if not current_user.is_admin() and result.account_id != current_user.account_id:
                return get_message_json('用户无法访问他人任务'), HTTPStatus.FORBIDDEN

            json_res = result.to_json()
            json_res['message'] = '成功查看任务'
            return json_res, HTTPStatus.OK

        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
            )
    def put(self, job_id):
        """Edit a single job by id."""
        form = request.get_json()
        try:
            the_job = jobs.find_job_by_id(job_id)
            if the_job is None:
                return get_message_json('任务不存在'), HTTPStatus.NOT_FOUND

            if the_job.account_id != current_user.account_id:
                return get_message_json('用户无法修改他人任务'), HTTPStatus.FORBIDDEN

            # The job state must be valid and can not go back
            form_job_state = form.get('job_state')
            if not(validate_job_state_code(form_job_state) and form_job_state >= the_job.job_state):
                return get_message_json('任务状态不合法'), HTTPStatus.BAD_REQUEST

            # Client can edit label id if and only if the job is 'unlabeled'
            form_label_id = form.get('label_id')
            if the_job.job_state == ConstantCodes.Unlabeled:
                if not form_label_id:
                    return get_message_json('必须为该任务提供对应的标注'), HTTPStatus.BAD_REQUEST
            elif the_job.job_state == ConstantCodes.Labeling:
                # Can NOT change the label id
                if form_label_id is not None and form_label_id != the_job.label_id:
                    return get_message_json('用户无法替换任务的标注'), HTTPStatus.FORBIDDEN
            elif the_job.job_state == ConstantCodes.Finished:
                return get_message_json('用户无法修改已完成的任务'), HTTPStatus.FORBIDDEN

            # Update finished date automatically when the job is updated to be finished
            finished_date = None
            if form_job_state == ConstantCodes.Finished:
                finished_date = datetime.date.today()

            if not form_label_id:
                form_label_id = the_job.label_id

            result = jobs.update_job_by_id(
                job_id,
                form_label_id,
                finished_date,
                form_job_state,
                the_job.image_id,
                the_job.account_id
            )
            if result == 1:
                json_res = form.copy()
                json_res['message'] = '成功编辑任务'

                return json_res, HTTPStatus.OK
            else:
                return get_message_json('未知的任务更新失败'), HTTPStatus.BAD_REQUEST

        except IntegrityError as err:
            if err.orig.args[0] == DBErrorCodes.FOREIGN_KEY_FAILURE:
                return get_message_json('指定的用户或标注不存在'), HTTPStatus.BAD_REQUEST
            else:
                return handle_internal_error(err.orig.args[1])
        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    def delete(self, job_id):
        """Delete a single job by id."""
        # Only admin can delete any job
        if not current_user.is_admin():
            return get_message_json('删除任务需要管理员权限'), HTTPStatus.FORBIDDEN

        try:
            result = jobs.delete_job_by_id(job_id)
            if result == 1:
                return get_message_json('已删除该任务'), HTTPStatus.OK
            else:
                if jobs.find_job_by_id(job_id) is None:
                    return get_message_json('任务不存在'), HTTPStatus.NOT_FOUND
                return get_message_json('未知的任务删除失败'), HTTPStatus.BAD_REQUEST
        except Exception as err:
            return handle_internal_error(str(err))


@api.route('/')
class JobsCollectionResource(Resource):
    """Deal with collection of jobs."""

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('image_id', type=str, required=False, help='id of image', location='args')
             .add_argument('account_id', type=str, required=False, help='id of account', location='args')
             .add_argument('job_state', type=str, required=False, help='state of job', location='args')
             )
    def get(self):
        """List all jobs."""
        # These arguments are all strings originally and should be cast to int
        account_id = convert_to_int(request.args.get('account_id'))
        image_id = convert_to_int(request.args.get('image_id'))
        job_state = convert_to_int(request.args.get('job_state'))

        if not current_user.is_admin()\
                and (account_id is None or account_id != current_user.account_id):
            return get_message_json('用户没有权限访问其他用户的任务列表'), HTTPStatus.FORBIDDEN

        try:
            result = jobs.find_all_jobs(account_id, image_id, job_state)

            data = []
            for job in result:
                data.append(job.to_json())
            json_res = {
                'message': '成功获取所有任务',
                'data': data
            }
            return json_res, HTTPStatus.OK
        except Exception as err:
            return handle_internal_error(str(err))

    @login_required
    @api.doc(parser=api.parser()
             .add_argument('body', type=str, required=True, help='json', location='json')
            )
    def post(self):
        """Create a job."""
        form = request.get_json()
        # Only admin can create jobs
        if not current_user.is_admin():
            return get_message_json('创建任务需要管理员权限'), HTTPStatus.FORBIDDEN
        
        try:
            image_id = form.get('image_id')
            account_id = form.get('account_id')
            if not image_id or not account_id:
                return get_message_json('请求非法'), HTTPStatus.BAD_REQUEST

            # Can only assign job to doctor
            the_account = accounts.find_account_by_id(account_id)
            if the_account is None:
                return get_message_json('指定的医生不存在'), HTTPStatus.BAD_REQUEST
            elif the_account.authority != ConstantCodes.Doctor:
                return get_message_json('只能为医生分配任务'), HTTPStatus.BAD_REQUEST

            # Can not assign the same image to an account more than once
            related_job_list = jobs.find_job_by_account_id(account_id)
            related_image_list = [job.image_id for job in related_job_list]
            if image_id in related_image_list:
                return get_message_json('已为此用户分配过该图像的标注任务'), HTTPStatus.BAD_REQUEST

            # Only unassigned or 'running' image can be assigned
            the_image = images.find_image_by_id(image_id)
            if the_image is None:
                return get_message_json('指定的图像不存在'), HTTPStatus.BAD_REQUEST
            elif the_image.image_state != ConstantCodes.Unassigned and the_image.image_state != ConstantCodes.Running:
                return get_message_json('无法再为该图像分配标注任务'), HTTPStatus.BAD_REQUEST
            
            result = jobs.add_job(
                image_id,
                account_id
            )
            json_res = result.to_json()
            json_res['message'] = '任务创建成功'

            return json_res, HTTPStatus.CREATED

        except IntegrityError as err:
            if err.orig.args[0] == DBErrorCodes.FOREIGN_KEY_FAILURE:
                return get_message_json('指定的用户或图像不存在'), HTTPStatus.BAD_REQUEST
            else:
                return handle_internal_error(err.orig.args[1])
        except Exception as err:
            return handle_internal_error(str(err))
