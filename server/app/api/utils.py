# coding=utf-8
"""Provide common utilities for API processing."""
from flask import current_app, send_file, make_response
from http import HTTPStatus
import inspect
import re
import time
import os
import fcntl
import errno
from werkzeug._compat import text_type, PY2


label_field_mapping = {
    'quality': '图片质量',
    'dr': '糖尿病视网膜病变',
    'stage': '糖尿病视网膜病变阶段',
    'dme': '黄斑水肿',
    'hr': '高血压视网膜病变',
    'age_dme': '年龄相关性黄斑变性',
    'rvo': '视网膜静脉阻塞',
    'crao': '视网膜动脉阻塞',
    'myopia': '病理性近视',
    'od': '视盘、视神经疾病',
    'glaucoma': '疑似青光眼',
    'others': '其他疾病',
    'comment': '备注'
}

label_code_mapping = {
    '400': '没有黄斑水肿',
    '401': '糖尿病黄斑水肿',
    '402': '非糖尿病黄斑水肿',
    '500': '不患有高血压视网膜病变',
    '501': '轻度高血压视网膜病变',
    '502': '中度高血压视网膜病变',
    '503': '重度高血压视网膜病变',
    '600': '不患有年龄相关性黄斑变性',
    '601': '早期年龄相关性黄斑变性',
    '602': '中期年龄相关性黄斑变性',
    '603': '晚期年龄相关性黄斑变性',
    '700': '可接受',
    '701': '曝光问题',
    '702': '镜头污迹',
    '703': '视野偏差',
    '704': '图像失焦',
    '705': '其他问题',
    '800': '无',
    '801': '1期',
    '802': '2期',
    '803': '3期',
    '804': '4期',
    '805': '5期',
    '806': '6期',
    '807': '7期',
}


class DBErrorCodes(object):
    """
    Collect MySQL error codes that are used in this project.

    Refer to
    https://dev.mysql.com/doc/refman/8.0/en/error-messages-server.html
    """
    # Duplicate entry for unique key
    DUPLICATE_ENTRY = 1062
    # Foreign key failes
    FOREIGN_KEY_FAILURE = 1452


class ConstantCodes(object):
    """Constant codes for some states."""
    # Authority 1XX
    Empty = 100
    Admin = 101
    Doctor = 102
    Guest = 103
    Expert = 104
    # Job State 2XX
    Unlabeled = 200
    Labeling = 201
    Finished = 202
    # Image State 3XX
    Unassigned = 300
    Running = 301
    Different = 302
    DifferentII = 303
    Done = 304


def get_message_json(message):
    """Return a json with message."""
    return {'message': message}


def handle_internal_error(message):
    """
    Log unknown error and return tuple of json and status code.
    :param message: error message
    :return: tuple of json and status code
    """
    current_app.logger.exception(message)
    return get_message_json('服务器内部错误'), HTTPStatus.INTERNAL_SERVER_ERROR


def convert_to_int(argument):
    """
    A helper function to convert argument in the query string into int.
    :param argument: the string-type argument got by `request.args.get('...')`
    :return: the corresponding int or None
    """
    return int(argument) if argument else None


def convert_to_int_default0(argument):
    """
    A helper function to convert argument in the query string into int.
    :param argument: the string-type argument got by `request.args.get('...')`
    :return: the corresponding int or 0
    """
    return int(argument) if argument else 0


def get_all_constant_codes():
    """Get all codes defined in ConstantCodes."""
    attributes = inspect.getmembers(ConstantCodes, lambda a: not (inspect.isroutine(a)))
    all_codes = [a[1] for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
    return all_codes


def validate_authority_code(code):
    """Check if the given code is valid authority code."""
    return code in [c for c in get_all_constant_codes() if str(c).startswith('1')]


def validate_job_state_code(code):
    """Check if the given code is valid job state code."""
    return code in [c for c in get_all_constant_codes() if str(c).startswith('2')]


def validate_image_state_code(code):
    """Check if the given code is valid image state code."""
    return code in [c for c in get_all_constant_codes() if str(c).startswith('3')]


def validate_password(password):
    """Check if the given password is valid"""
    if password is None:
        return True
    pattern = r'^[a-zA-Z0-9]{8,32}$'
    return bool(re.match(pattern, password))


def validate_username(username):
    """Check if the given username is valid"""
    if username is None:
        return True
    pattern = r'^[a-zA-Z0-9]{3,32}$'
    return bool(re.match(pattern, username))


def validate_nickname(nickname):
    """Check if the given nickname is valid"""
    if nickname is None:
        return True
    length = len(nickname)
    return length <= 32


def secure_filename(filename):
    """
    Modified version of werkzeug.utils.secure_filename to support Chinese.
    :param filename: the filename to secure
    """
    _filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
    _filename_gbk_strip_re = re.compile(u"[^\u4e00-\u9fa5A-Za-z0-9_.-]")
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                             'LPT2', 'LPT3', 'PRN', 'NUL')

    if isinstance(filename, text_type):
        from unicodedata import normalize
        # filename = normalize('NFKD', filename).encode('ascii', 'ignore')
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        if not PY2:
            filename = filename.decode('utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_gbk_strip_re.sub('', '_'.join(
        filename.split()))).strip('._')

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename


def send_csv_file(file_path):
    """Send csv file with lock."""
    with open(file_path, 'r') as f:
        # Set a loop to get lock
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except IOError as e:
                # raise on unrelated IOErrors
                if e.errno != errno.EAGAIN:
                    raise
                else:
                    time.sleep(0.1)
        response = make_response(send_file(file_path, as_attachment=True))
        file_name = os.path.basename(file_path)
        response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name.encode().decode('latin-1'))
        fcntl.flock(f, fcntl.LOCK_UN)
    return response
