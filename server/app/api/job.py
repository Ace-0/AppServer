# coding=utf-8
"""Deal with job-related APIs."""
from flask_restplus import Namespace, Resource, reqparse

api = Namespace('jobs')


@api.route('/<int:job_id>')
class JobResource(Resource):
    """Deal with single job."""

    def get(self, job_id):
        """Retrieve a single job by id."""
        pass

    def put(self, job_id):
        """Edit a single job by id."""
        pass

    def delete(self, job_id):
        """Delete a single job by id."""
        pass


@api.route('/')
class JobsCollectionResource(Resource):
    """Deal with collection of jobs."""

    # The url must provide doctor_id argument
    parser = reqparse.RequestParser()
    parser.add_argument('doctor_id', required=True, help='Doctor id not provided!')

    def get(self):
        """List all jobs."""
        pass

    def post(self):
        """Create a job."""
        args = JobsCollection.parser.parse_args()
        pass
