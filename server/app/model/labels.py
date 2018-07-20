# coding=utf-8
"""Define table and operations for labels."""
from sqlalchemy import Column, Integer, VARCHAR, BOOLEAN, ForeignKey, TEXT, func
from . import Base, session, handle_db_exception, is_testing


class Labels(Base):
    """Table constructed for labels."""
    if is_testing:
        __tablename__ = 'TEST_Labels'
    else:
        __tablename__ = 'Labels'

    label_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    quality = Column(VARCHAR(256))  # 图片质量，用字符串来表示整数数组，以逗号分隔
    dr = Column(BOOLEAN)  # 是否有糖尿病视网膜病变
    stage = Column(Integer)  # 糖尿病视网膜病变阶段
    dme = Column(Integer)  # 黄斑水肿类型
    hr = Column(Integer)    # 高血压视网膜病变
    age_dme = Column(Integer)   # 年龄相关性黄斑变性
    rvo = Column(BOOLEAN)  # 是否有视网膜静脉阻塞
    crao = Column(BOOLEAN)  # 是否有视网膜动脉阻塞
    myopia = Column(BOOLEAN)    # 病理性近视
    od = Column(BOOLEAN)  # 视盘、视神经疾病
    glaucoma = Column(BOOLEAN)  # 是否有疑似青光眼
    others = Column(BOOLEAN)  # 是否有其他疾病
    comment = Column(TEXT)  # 备注

    def to_json(self):
        """Return a json for the record."""
        try:
            return {
                'label_id': self.label_id,
                'quality': _convert_str_to_list(self.quality),
                'dr': self.dr,
                'stage': self.stage,
                'dme': self.dme,
                'hr': self.hr,
                'age_dme': self.age_dme,
                'rvo': self.rvo,
                'crao': self.crao,
                'myopia': self.myopia,
                'od': self.od,
                'glaucoma': self.glaucoma,
                'others': self.others,
                'comment': self.comment
                }
        except Exception as err:
            handle_db_exception(str(err))

    def __repr__(self):
        return '<Labels: label_id:{} quality:{} dr:{} stage:{} dme:{} hr:{} '\
               'age_dme:{} rvo:{} crao:{} myopia:{} od:{} glaucoma:{} others:{} comment:{}>'.\
            format(self.label_id,
                   self.quality,
                   self.dr,
                   self.stage,
                   self.dme,
                   self.hr,
                   self.age_dme,
                   self.rvo,
                   self.crao,
                   self.myopia,
                   self.od,
                   self.glaucoma,
                   self.others,
                   self.comment)

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            for field in self.__dict__:
                if field == 'label_id' or field == 'comment' or field == '_sa_instance_state':
                    continue
                if not getattr(self, field) == getattr(other, field):
                    return False
            return True
        return False

    def __hash__(self):
        return hash(
            tuple([getattr(self, field) for field in self.__dict__
                   if field not in ['label_id', 'comment', '_sa_instance_state']]))


def add_label(_quality: list,
              _dr: BOOLEAN,
              _stage: int,
              _dme: int,
              _hr: int,
              _age_dme: int,
              _rvo: BOOLEAN,
              _crao: BOOLEAN,
              _myopia: BOOLEAN,
              _od: BOOLEAN,
              _glaucoma: BOOLEAN,
              _others: BOOLEAN,
              _comment: str):
    """Add a label to database and return this label"""
    label = Labels()

    label.quality = _convert_list_to_str(_quality)
    label.dr = _dr
    label.stage = _stage
    label.dme = _dme
    label.hr = _hr
    label.age_dme = _age_dme
    label.rvo = _rvo
    label.crao = _crao
    label.myopia = _myopia
    label.od = _od
    label.glaucoma = _glaucoma
    label.others = _others
    label.comment = _comment
    try:
        session.add(label)
        session.commit()
        return label
    except Exception as err:
        handle_db_exception(err)


def update_label_by_id(_id: int,
                       _quality: list=None,
                       _dr: BOOLEAN=None,
                       _stage: int=None,
                       _dme: int=None,
                       _hr: int=None,
                       _age_dme: int=None,
                       _rvo: BOOLEAN=None,
                       _crao: BOOLEAN=None,
                       _myopia: BOOLEAN=None,
                       _od: BOOLEAN=None,
                       _glaucoma: BOOLEAN=None,
                       _others: BOOLEAN=None,
                       _comment: str=None):
    """Update the information of an label given id and return 1 or 0 represented result"""

    try:
        _quality = _convert_list_to_str(_quality)
        result = session.query(Labels).filter(Labels.label_id == _id).update({
            "quality": _quality if _quality is not None else Labels.quality,
            "dr": _dr if _dr is not None else Labels.dr,
            "stage": _stage if _stage is not None else Labels.stage_id,
            "dme": _dme if _dme is not None else Labels.dme,
            "hr": _hr if _hr is not None else Labels.hr_id,
            "age_dme": _age_dme if _age_dme is not None else Labels.age_dme_id,
            "rvo": _rvo if _rvo is not None else Labels.rvo,
            "crao": _crao if _crao is not None else Labels.crao,
            "myopia": _myopia if _myopia is not None else Labels.myopia,
            "od": _od if _od is not None else Labels.od,
            "glaucoma": _glaucoma if _glaucoma is not None else Labels.glaucoma,
            "others": _others if _others is not None else Labels.others,
            "comment": _comment if _comment is not None else Labels.comment
        })
        session.commit()
        return result
    except Exception as err:
        handle_db_exception(err)


def delete_label_by_id(_id: int):
    """Delete a label by id and return 1 or 0 represented result"""
    try:
        result = session.query(Labels).filter(Labels.label_id == _id).delete()
        session.commit()
        return result
    except Exception as err:
        handle_db_exception(err)


def find_label_by_id(_id: int):
    """Find a label by id and return a label object"""
    try:
        label_list = session.query(Labels).filter(Labels.label_id == _id)
        session.commit()
        return label_list.first()
    except Exception as err:
        handle_db_exception(err)


def _check_if_labels_unquestioned(label_list):
    """
    If more than half in the label list are identical, then the labels are considered unquestioned.
    :param label_list: the list of labels to be checked
    :return: a representative label id or None
    """
    mapping = dict()
    for label in label_list:
        if mapping.get(label):
            mapping[label] += 1
        else:
            mapping[label] = 1
    if max(mapping.values()) > len(label_list)/2:
        return max(mapping, key=mapping.get).label_id
    return None


def _calculate_metrics(ground_truth_label_ids, inspected_label_ids):
    """Compare two label lists and calculate metrics."""
    if not ground_truth_label_ids:
        return {}
    ground_truth_labels = [session.query(Labels).filter(Labels.label_id == _id).first()
                           for _id in ground_truth_label_ids]
    inspected_labels = [session.query(Labels).filter(Labels.label_id == _id).first()
                        for _id in inspected_label_ids]
    # Initialize metrics at first
    metrics = dict()
    for field in ground_truth_labels[0].__dict__:
        if field not in ['label_id', 'comment', '_sa_instance_state']:
            metrics[field] = {'accuracy': 0}
    for i in range(len(ground_truth_labels)):
        for field in metrics:
            if getattr(ground_truth_labels[i], field) == getattr(inspected_labels[i], field):
                metrics[field]['accuracy'] += 1
    for field in metrics:
        metrics[field]['accuracy'] /= float(len(ground_truth_labels))

    return metrics


def _convert_list_to_str(li):
    """Convert list to string with comma as delimiter, mainly used in converting `quality`."""
    return ','.join([str(x) for x in li])


def _convert_str_to_list(string):
    """Convert comma-separated string to list, mainly used in converting `quality`."""
    return [int(x) for x in string.split(',')]
