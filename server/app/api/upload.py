# coding=utf-8
import os
import datetime
from sqlalchemy.exc import IntegrityError
from flask import request, current_app, send_file
from flask_restplus import Namespace, Resource
from flask_login import login_required, current_user
from werkzeug.datastructures import FileStorage
from ..model import accounts, images, labels
from .utils import get_message_json, handle_internal_error, HTTPStatus, ConstantCodes, DBErrorCodes, secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

api = Namespace('uploads')


@api.route('/photos/')
class PhotosCollectionResource(Resource):
    """Deal with collection of accounts' photos."""
    
    @login_required
    @api.doc(parser=api.parser()
             .add_argument('file', type=FileStorage, required=True, help='photo', location='files')
            )
    def post(self):
        """upload a photo."""

        photo_file = request.files['file']
        if photo_file and allowed_file(photo_file.filename):
            photo_filename = current_user.username + '.png'
            try:
                photo_location = os.path.join(os.environ['HOME'], current_app.config['PHOTOS_FOLDER'])
                photo_file.save(os.path.join(photo_location, photo_filename))
                
                if current_user.photo == 'default.png':
                    current_user.photo = photo_filename

                return get_message_json('头像上传成功'), HTTPStatus.CREATED

            except Exception as err:
                return handle_internal_error(str(err))
        else:
            return get_message_json('头像上传失败'), HTTPStatus.BAD_REQUEST


@api.route('/photos/<string:filename>/')
class PhotoResource(Resource):
    """Deal with single photos."""
    
    @login_required
    @api.doc(parser=api.parser()
             .add_argument('timestemp', type=str, required=False, help='time stamp', location='args')
            )
    def get(self, filename):
        """retrive a photo."""

        photo_file_path = os.path.join(os.environ['HOME'], current_app.config['PHOTOS_FOLDER'], filename)
        if os.path.exists(photo_file_path):
            try:
                return send_file(photo_file_path)
            except Exception as err:
                return handle_internal_error(str(err))
        else:
            return get_message_json('头像不存在'), HTTPStatus.NOT_FOUND


@api.route('/medical-images/')
class MedicalImagesCollectionResource(Resource):
    """Deal with collection of medical images."""
    
    @login_required
    @api.doc(parser=api.parser()
             .add_argument('file', type=FileStorage, required=True, help='medical-images', location='files')
            )
    def post(self):
        """upload a madical image."""
        if not current_user.is_admin():
            return get_message_json("创建图片需要管理员权限"), HTTPStatus.UNAUTHORIZED

        medical_file = request.files['file']
        if medical_file and allowed_file(medical_file.filename):
            medical_filename = secure_filename(medical_file.filename)
            raw_filename = medical_filename.rsplit('.', 1)[0]
            hash_filename = str(hash(raw_filename))
            
            try:
                """save the image data"""
                expand_name = medical_filename.rsplit('.', 1)[1]
                time_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')
                medical_url = time_name + hash_filename + '.' + expand_name
                medical_location = os.path.join(os.environ['HOME'], current_app.config['MEDICAL_IMAGES_FOLDER'])
                medical_file.save(os.path.join(medical_location, medical_url))

                """create an instance of Image"""
                image_object = images.add_image(
                    ConstantCodes.Unassigned,
                    medical_filename,
                    medical_url,
                    'default source',
                )
                json_res = image_object.to_json()
                json_res['message'] = '医学图像上传成功'

                return json_res, HTTPStatus.CREATED
            
            except IntegrityError as err:
                if err.orig.args[0] == DBErrorCodes.DUPLICATE_ENTRY:
                    return get_message_json('图片已存在'), HTTPStatus.CONFLICT
                else:
                    return handle_internal_error(err.orig.args[1])

            except Exception as err:
                return handle_internal_error(str(err))

        else:
            return get_message_json('医学影像上传失败'), HTTPStatus.BAD_REQUEST


@api.route('/medical-images/<string:url>')
class MedicalImageResource(Resource):
    """Deal with single medical-images."""
    
    @login_required
    def get(self, url):
        """retrive a medical image."""
        
        medical_file_path = os.path.join(os.environ['HOME'], current_app.config['MEDICAL_IMAGES_FOLDER'], url)
        if os.path.exists(medical_file_path):
            try:
                return send_file(medical_file_path)
            except Exception as err:
                return handle_internal_error(str(err))
        else:
            return get_message_json('图像不存在'), HTTPStatus.NOT_FOUND


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
