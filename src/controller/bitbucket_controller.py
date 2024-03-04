# controller/bitbucket_controller.py
import os
import subprocess
from flask_restx import Namespace, Resource, reqparse
from src.service.bitbucket_service import BitbucketService

api = Namespace('bitbucket', description='Bitbucket operations')

parser = reqparse.RequestParser()
parser.add_argument('bitbucketserverurl', type=str, required=True, help='Bitbucket Server URL')
parser.add_argument('bitbucketcloudurl', type=str, required=True, help='Bitbucket Cloud URL')
parser.add_argument('username', type=str, required=True, help='Bitbucket Server username')
parser.add_argument('password', type=str, required=True, help='Bitbucket Server password')
parser.add_argument('cloudworkspace', type=str, required=True, help='Bitbucket Cloud workspace')
parser.add_argument('cloudauthusername', type=str, required=True, help='Bitbucket Cloud username')
parser.add_argument('cloudauthpassword', type=str, required=True, help='Bitbucket Cloud password')

@api.route('/projects')
class BitbucketProjects(Resource):
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        bitbucket_server_url = args['bitbucketserverurl']
        bitbucket_cloud_url = args['bitbucketcloudurl']
        server_username = args['username']
        server_password = args['password']
        cloud_workspace = args['cloudworkspace']
        cloud_username = args['cloudauthusername']
        cloud_password = args['cloudauthpassword']

        # Create an instance of BitbucketService
        bitbucket_service = BitbucketService(
            bitbucket_server_url, bitbucket_cloud_url,
            server_username, server_password,
            cloud_workspace, cloud_username, cloud_password
        )

        # Verify authentication before migrating
        auth_verification_result, status_code = bitbucket_service.verify_auth_details()
        if status_code != 200:
            return auth_verification_result, status_code

        # Use the service layer to fetch projects from Bitbucket Server
        source_projects = bitbucket_service.get_bitbucket_projects()

        # Iterate over server projects and create them in Bitbucket Cloud
        for project in source_projects:
            project_key = project['key']
            project_name = project['name']
            project_description = project.get('description', '')

            # Create the project in Bitbucket Cloud
            response = bitbucket_service.create_bitbucket_project(project_key, project_name, project_description)

            # Fetch repositories for the project from Bitbucket Server
            source_repositories = bitbucket_service.get_repositories_for_project(project_key)

            for repository in source_repositories:
                repository_name = repository['name']
                repository_description = repository.get('description', '')
                public = repository['public']

                # Create the repository in Bitbucket Cloud
                response = bitbucket_service.create_bitbucket_repository(project_key, repository_name, repository_description, public)
                # print(response)

                # fetch all the repos branches it's metadata from source and push it to bitbucket cloud
                response = bitbucket_service.create_and_push_repository(project_key, repository_name, project_name)
