# service/bitbucket_service.py
import os
import subprocess
import requests
from src.util.bitbucket_util import BitbucketUtil

class BitbucketService:
    def __init__(self, bitbucket_server_url, bitbucket_cloud_url,
                 server_username, server_password,
                 cloud_workspace, cloud_username, cloud_password):

        self.bitbucket_server_url = bitbucket_server_url
        self.bitbucket_cloud_url = bitbucket_cloud_url
        self.cloud_username = cloud_username
        self.server_username = server_username
        self.server_password = server_password
        self.cloud_password = cloud_password
        self.cloud_workspace = cloud_workspace
        self.bitbucket_server_util = BitbucketUtil(bitbucket_server_url, auth=(server_username, server_password))
        self.bitbucket_cloud_util = BitbucketUtil(bitbucket_cloud_url, auth=(cloud_username, cloud_password))

        self.cloud_workspace = cloud_workspace

    def verify_authentication(self, url, username, password):
        try:
            auth_details = {'auth': (username, password)}
            response = requests.get(url, **auth_details)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            print(f"Authentication failed. HTTP Error: {e}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed. An error occurred: {e}")
            return False
        except Exception as ex:
            return ex

    def verify_auth_details(self):
        verify_src = self.verify_authentication(self.bitbucket_server_url, self.server_username, self.server_password)
        verify_dest = self.verify_authentication(self.bitbucket_cloud_url, self.cloud_username, self.cloud_password)

        if not verify_src:
            return "Invalid credentials for source", 401
        if not verify_dest:
            return "Invalid credentials for destination", 401

        return "Authentication successful", 200

    def get_bitbucket_projects(self):
        # Fetch projects from Bitbucket Server using the BitbucketUtil
        endpoint = "rest/api/1.0/projects"
        response = self.bitbucket_server_util.get(endpoint)

        if response.status_code == 200:
            projects_data = response.json()
            return projects_data['values']
        else:
            raise Exception(f'Failed to fetch projects from Bitbucket Server. Status code: {response.status_code}')
    
    def get_repositories_for_project(self, project_key):
        # Fetch repositories for a specific project from Bitbucket Server using the BitbucketUtil
        endpoint = f"rest/api/1.0/projects/{project_key}/repos"
        response = self.bitbucket_server_util.get(endpoint)

        if response.status_code == 200:
            repositories_data = response.json()
            repositories = repositories_data['values']

            # print(f"Repositories for project {project_key} - {repositories}")
            return repositories
        else:
            raise Exception(f'Failed to fetch repositories for project {project_key}. Status code: {response.status_code}')

    def create_bitbucket_project(self, project_key, project_name, project_description=''):
        # Check if the project already exists in Bitbucket Cloud
        if self.project_exists_in_cloud(project_key):
            return f"Project with key {project_key} already exists in Bitbucket Cloud. Skipping creation."

        # Create the project in Bitbucket Cloud
        cloud_project_data = {
            'key': project_key,
            'name': project_name,
            'description': project_description
        }
        cloud_response = self.bitbucket_cloud_util.post(f'/2.0/workspaces/{self.cloud_workspace}/projects', json=cloud_project_data)

        if cloud_response.status_code == 201:
            return f"Project with key {project_key} successfully created in Bitbucket Cloud."
        else:
            raise Exception(f'Failed to create project in Bitbucket Cloud. Status code: {cloud_response.status_code}')

    def create_bitbucket_repository(self, project_key, repository_name, repository_description='', public=True):
        # Create the repository in Bitbucket Cloud
        cloud_repository_data = {
            'scm': 'git',
            'is_private': not public,
            'project': {'key': project_key},
            'description': repository_description
        }

        cloud_response = self.bitbucket_cloud_util.post(f'/2.0/repositories/{self.cloud_workspace}/{repository_name}', json=cloud_repository_data)

        if cloud_response.status_code == 201:
            return f"Repository {repository_name} successfully created in Bitbucket Cloud.",cloud_response.status_code

    def project_exists_in_cloud(self, project_key):
        # Check if the project already exists in Bitbucket Cloud
        cloud_projects = self.bitbucket_cloud_util.get(f'/2.0/workspaces/{self.cloud_workspace}/projects').json()
        existing_project_keys = [proj['key'] for proj in cloud_projects['values']]
        return project_key in existing_project_keys
        

    def create_and_push_repository(self, project_key, repository_name, project_name):
        # print(project_name)
        repo_name = repository_name
        local_repo_path = f'./{project_name}/{repo_name}'
        if not os.path.exists(local_repo_path):
            os.makedirs(local_repo_path)

        # Clone the repository from the source Bitbucket instance
        clone_url = f'{self.bitbucket_server_url}/scm/{project_key}/{repository_name}.git'
        subprocess.run(['git', 'clone', clone_url, local_repo_path])

        # Add remote for Bitbucket Cloud
        cloud_remote_url = f'https://{self.cloud_username}:{self.cloud_password}@bitbucket.org/{self.cloud_workspace}/{repository_name}.git'
        print(cloud_remote_url)
        subprocess.run(['git', 'remote', 'add', 'cloud', cloud_remote_url], cwd=local_repo_path)

        # Fetch and push branches to Bitbucket Cloud
        subprocess.run(['git', 'fetch', '--all'], cwd=local_repo_path)
        branches = subprocess.run(['git', 'branch', '--list', '--all'], cwd=local_repo_path, capture_output=True, text=True).stdout.split('\n')
        for branch in branches:
            branch = branch.strip('* ').split('/')[-1]
            if branch and branch != 'HEAD':
                print(f'Pushing branch: {branch}')
                subprocess.run(['git', 'checkout', branch], cwd=local_repo_path)
                subprocess.run(['git', 'pull', 'origin', branch], cwd=local_repo_path)
                subprocess.run(['git', 'push', 'cloud', f'{branch}:{branch}'], cwd=local_repo_path)
