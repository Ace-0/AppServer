# coding=utf-8
"""Deal with label-related APIs."""
from flask_restplus import Namespace, Resource, reqparse

api = Namespace('labels')


@api.route('/<int:label_id>')
class LabelResource(Resource):
    """Deal with single label."""

    def get(self, label_id):
        """Retrieve a single label by id."""
        pass

    def put(self, label_id):
        """Edit a single label by id."""
        pass

    def delete(self, label_id):
        """Delete a single label by id."""
        pass


@api.route('/')
class LabelsCollectionResource(Resource):
    """Deal with collection of labels."""

    def post(self):
        """Create a label."""
        pass
