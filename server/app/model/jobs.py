# coding=utf-8
"""Define table and operations for jobs."""
import errno
import time
import fcntl
import os
from flask import current_app
from sqlalchemy import Column, Integer, VARCHAR, DATE, ForeignKey, DATETIME, func
from . import Base, session, handle_db_exception, images, accounts, labels, is_testing
from ..api.utils import ConstantCodes, label_code_mapping, label_field_mapping
from random import randint


class Jobs(Base):
    """Table constructed for jobs."""
    if is_testing:
        __tablename__ = 'TEST_Jobs'
        image_id = Column(Integer, ForeignKey('TEST_Images.image_id'))
        label_id = Column(Integer, ForeignKey('TEST_Labels.label_id'))
        account_id = Column(Integer, ForeignKey('TEST_Accounts.account_id'))
    else:
        __tablename__ = 'Jobs'
        image_id = Column(Integer, ForeignKey('Images.image_id'))
        label_id = Column(Integer, ForeignKey('Labels.label_id'))
        account_id = Column(Integer, ForeignKey('Accounts.account_id'))

    job_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    finished_date = Column(DATE)
    job_state = Column(Integer, nullable=False)

    def to_json(self):
        """Return a json for the record."""
        return {
            'job_id': self.job_id,
            'image_id': self.image_id,
            'label_id': self.label_id,
            'account_id': self.account_id,
            'finished_date': str(self.finished_date) if self.finished_date else None,
            'job_state': self.job_state
        }

    def __repr__(self):
        return '<Jobs: job_id:{} image_id:{} label_id:{} account_id:{} finished_date:{} job_state:{}>'.\
            format(self.job_id,
                   self.image_id,
                   self.label_id,
                   self.account_id,
                   self.finished_date,
                   self.job_state)


def add_job(_image_id: int,
            _account_id: int):
    """Add a job to database."""
    job = Jobs()
    job.image_id = _image_id
    job.account_id = _account_id
    job.job_state = ConstantCodes.Unlabeled
    try:
        session.add(job)
        # Modify the state of the image
        images._update_image_by_id_without_commit(_image_id, _image_state=ConstantCodes.Running)
        session.commit()
        return job
    except Exception as err:
        handle_db_exception(err)


def delete_job_by_id(_job_id):
    """Delete an account by id and return 1 or 0 representing result"""
    try:
        result = session.query(Jobs).filter(Jobs.job_id == _job_id).delete()
        session.commit()
        return result
    except Exception as err:
        handle_db_exception(err)


def update_job_by_id(_job_id: int,
                     _label_id: int,
                     _finished_date: DATETIME,
                     _job_state: int,
                     the_image_id: int,
                     the_account_id: int):
    """Update the information of a job given id and return 1 or 0 representing result"""
    try:
        result = session.query(Jobs).filter(Jobs.job_id == _job_id).update({
            'label_id': _label_id if _label_id is not None else Jobs.label_id,
            'finished_date': _finished_date if _finished_date is not None else Jobs.finished_date,
            'job_state': _job_state if _job_state is not None else Jobs.job_state
        })
        # Check whether to update corresponding image
        if _job_state == ConstantCodes.Finished:
            # Write finished label to files
            _write_label_to_files(the_account_id, _label_id)
            cur_image_state = session.query(images.Images).\
                filter(images.Images.image_id == the_image_id).first().image_state
            if cur_image_state == ConstantCodes.DifferentII:
                # It means that the job is finished by an expert
                images._update_image_by_id_without_commit(the_image_id, _label_id, ConstantCodes.Done)
            else:
                jobs_of_same_image = session.query(Jobs).filter(Jobs.image_id == the_image_id).all()
                images._update_image_state(the_image_id, cur_image_state, jobs_of_same_image)
        # Regard the above operations as a transaction and ensure to commit only once
        session.commit()
        return result
    except Exception as err:
        handle_db_exception(err)


def find_job_by_id(_id: int):
    """Find a job by id and return a job object"""
    try:
        job_list = session.query(Jobs).filter(Jobs.job_id == _id)
        session.commit()
        return job_list.first()
    except Exception as err:
        handle_db_exception(err)


def find_job_by_image_id(_image_id: int):
    """Find jobs by image id and return a list"""
    try:
        job_list = session.query(Jobs).filter(Jobs.image_id == _image_id)
        session.commit()
        return job_list.all()
    except Exception as err:
        handle_db_exception(err)


def find_job_by_account_id(_account_id: int):
    """Find jobs by account id and return a list"""
    try:
        job_list = session.query(Jobs).filter(Jobs.account_id == _account_id)
        session.commit()
        return job_list.all()
    except Exception as err:
        handle_db_exception(err)


def find_job_by_label_id(_label_id: int):
    """Find jobs by label id and return a job object"""
    try:
        job_list = session.query(Jobs).filter(Jobs.label_id == _label_id)
        session.commit()
        return job_list.first()
    except Exception as err:
        handle_db_exception(err)


def find_all_jobs(_account_id: int,
                  _image_id: int,
                  _job_state: int):
    """Return all jobs related to the given arguments via a list."""
    try:
        query = {}
        if _account_id is not None:
            query['account_id'] = _account_id
        if _image_id is not None:
            query['image_id'] = _image_id
        if _job_state is not None:
            query['job_state'] = _job_state
        jobs_list = session.query(Jobs).filter_by(**query)

        session.commit()
        return jobs_list.all()
    except Exception as err:
        handle_db_exception(err)


def get_performance_by_account_id(_account_id: int):
    """Return performance related to the given account."""
    try:
        job_list = session.query(Jobs).filter(Jobs.account_id == _account_id).all()
        progress = _get_job_progress(job_list)
        metrics = _get_job_metrics(job_list)
        performance = {'progress': progress, **metrics}

        session.commit()
        return performance
    except Exception as err:
        handle_db_exception(err)


def _find_doctors_not_assigned_the_image(image_id):
    """
    Find all doctors that has never been assigned the given image.
    :param image_id: the id of the image
    :return: a doctor id list (may be empty)
    """
    job_list = session.query(Jobs).filter(Jobs.image_id == image_id).all()
    excluded_account_id_list = [job.account_id for job in job_list]
    account_list = session.query(accounts.Accounts).filter(
        ~accounts.Accounts.account_id.in_(excluded_account_id_list)).all()
    doctor_id_list = [account.account_id for account in account_list if account.authority == ConstantCodes.Doctor]
    return doctor_id_list


def _add_job_without_commit(_image_id: int, _account_id: int):
    """Add a job to database without commit."""
    job = Jobs()
    job.image_id = _image_id
    job.account_id = _account_id
    job.job_state = ConstantCodes.Unlabeled
    session.add(job)


def _add_job_to_an_expert(_image_id: int):
    """Add a job to a randomly chosen expert."""
    expert_list = session.query(accounts.Accounts).filter(accounts.Accounts.authority == ConstantCodes.Expert).all()
    chosen_expert_id = expert_list[randint(0, len(expert_list)-1)].account_id
    _add_job_without_commit(_image_id, chosen_expert_id)


def _get_job_progress(job_list):
    """Calculate progress given a job list."""
    progress = dict()
    progress['total_jobs'] = len(job_list)
    progress['unlabeled_jobs'] = progress['labeling_jobs'] = progress['finished_jobs'] = 0
    for job in job_list:
        if job.job_state == ConstantCodes.Unlabeled:
            progress['unlabeled_jobs'] += 1
        elif job.job_state == ConstantCodes.Labeling:
            progress['labeling_jobs'] += 1
        elif job.job_state == ConstantCodes.Finished:
            progress['finished_jobs'] += 1
    return progress


def _get_job_metrics(job_list):
    """Calculate metrics (like accuracy) given a job list."""
    ground_truth_label_ids = []
    inspected_label_ids = []
    for job in job_list:
        if job.job_state == ConstantCodes.Finished:
            the_image = session.query(images.Images).filter(images.Images.image_id == job.image_id).first()
            if the_image.image_state == ConstantCodes.Done:
                ground_truth_label_ids.append(the_image.label_id)
                inspected_label_ids.append(job.label_id)
    return labels._calculate_metrics(ground_truth_label_ids, inspected_label_ids)


def _write_label_to_files(account_id, label_id):
    the_label = session.query(labels.Labels).filter(labels.Labels.label_id == label_id).first()
    the_account = session.query(accounts.Accounts).filter(accounts.Accounts.account_id == account_id).first()
    csv_all_file = os.path.join(
        os.path.join(os.environ['HOME'], current_app.config['CSV_ALL_FOLDER']), 'all_labels.csv')
    csv_personal_file = os.path.join(
        os.path.join(os.environ['HOME'], current_app.config['CSV_PERSONAL_FOLDER']), the_account.username + '.csv')
    _add_new_line_to_file(csv_all_file, the_account.username, the_label)
    _add_new_line_to_file(csv_personal_file, the_account.username, the_label)


def _add_new_line_to_file(file_path, name, label):
    items = label.to_json()
    label_items = [
        'quality',
        'dr',
        'stage',
        'dme',
        'hr',
        'age_dme',
        'rvo',
        'crao',
        'myopia',
        'od',
        'glaucoma',
        'others',
        'comment'
    ]

    is_empty = not os.path.exists(file_path)
    with open(file_path, 'a') as f:
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

        if is_empty:
            # The file is empty and we should write item names at first
            to_write = ['用户名'] + [label_field_mapping[x] for x in label_items]
            f.write(','.join(to_write) + '\n')

        to_write = [name]
        for x in label_items:
            if x == 'quality':
                descriptions = [label_code_mapping[str(code)] for code in items[x]]
                to_write.append('、'.join(descriptions))
            else:
                val = str(items[x])
                if label_code_mapping.get(val):
                    to_write.append(label_code_mapping[val])
                else:
                    to_write.append(val)
        f.write(','.join(to_write) + '\n')
        fcntl.flock(f, fcntl.LOCK_UN)
