# coding=utf-8
"""Deal with image-related APIs."""
from flask_restplus import Namespace, Resource

api = Namespace('images')


@api.route('/<int:image_id>')
class ImageResource(Resource):
    """Deal with single image."""

    def get(self, image_id):
        """Retrieve a single image by id."""
        pass

    def put(self, image_id):
        """Edit a single image by id."""
        pass

    def delete(self, image_id):
        """Delete a single image by id."""
        pass


@api.route('/')
class ImagesCollectionResource(Resource):
    """Deal with collection of images."""

    def get(self):
        """List all images."""
        pass

    def post(self):
        """Create an image."""
        pass
