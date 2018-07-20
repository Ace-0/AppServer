# coding=utf-8
"""
Initialize `api` module.

Refer to http://flask-restplus.readthedocs.io/en/stable/scaling.html
"""
from flask_restplus import Api

from .account import api as account_ns
from .authorization import api as authorization_ns
from .job import api as job_ns
from .image import api as image_ns
from .label import api as label_ns
from .self import api as self_ns
from .upload import api as upload_ns
from .download import api as download_ns

api = Api(
    title='Yelda',
    version='1.0'
)

# `path` is somehow required
api.add_namespace(account_ns, path='/accounts')
api.add_namespace(authorization_ns, path='/authorization')
api.add_namespace(job_ns, path='/jobs')
api.add_namespace(image_ns, path='/images')
api.add_namespace(label_ns, path='/labels')
api.add_namespace(self_ns, path='/self')
api.add_namespace(upload_ns, path='/uploads')
api.add_namespace(download_ns, path='/download')
