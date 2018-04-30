# coding=utf-8
"""Define table and operations for images."""
from . import *


class Images(Base):
    """Table constructed for images."""

    __tablename__ = 'Images'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    state = Column(Integer)
    filename = Column(VARCHAR(128), nullable=False)
    Source = Column(VARCHAR(128))

    # def __repr__(self):
    #     return '<Images: ground_truth_id:{} state:{} info_id:{}>'.\
    #         format(self.ground_truth_id, self.state, self.info_id)


def add_image(_state: str,
              _filename: str,
              _source: str,
              add_fail_callback=None,
              add_succeed_callback=None):
    """
    :param _state:
    :param _filename:
    :param _source:
    :param add_fail_callback: (err)
    :param add_succeed_callback: (Image)
    """
    pass


def update_image_by_id(_id: str,
                       _filename=None,
                       _state=None,
                       _ground_truth_id=None,
                       _source=None,
                       find_fail_callback=None,
                       update_fail_callback=None,
                       update_succeed_callback=None):
    """
    :param _id:
    :param _filename:
    :param _state:
    :param _ground_truth_id:
    :param _source:
    :param find_fail_callback: (err)
    :param update_fail_callback: (err)
    :param update_succeed_callback: (Image)
    :return:
    """
    pass


def find_image_by_id(_id: str,
                     find_fail_callback=None,
                     find_succeed_callback=None):
    """
    :param _id:
    :param find_fail_callback: (err)
    :param find_succeed_callback: (Image)
    :return:
    """
    pass


def find_images_by_state(_state: int,
                         find_fail_func=None,
                         find_succeed_func=None):
    """
    :param _state:
    :param find_fail_func: (err)
    :param find_succeed_func: (Images List)
    :return:
    """
    pass


def delete_image_by_id(_id: str,
                       delete_fail_func=None,
                       delete_succeed_func=None):
    """
    :param _id:
    :param delete_fail_func: (err)
    :param delete_succeed_func: (None)
    :return:
    """
    pass
