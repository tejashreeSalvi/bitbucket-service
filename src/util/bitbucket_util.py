# util/bitbucket_util.py
import requests

class BitbucketUtil:
    def __init__(self, base_url, auth=None, auth_token=None):
        self.base_url = base_url
        self.auth = auth
        self.auth_token = auth_token

    def get(self, endpoint, params=None):
        # logic for making a GET request
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, auth=self.auth, params=params, headers={'Authorization': f'Bearer {self.auth_token}'})
        return response

    def post(self, endpoint, json=None):
        # logic for making a POST request
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, auth=self.auth, json=json, headers={'Authorization': f'Bearer {self.auth_token}'})
        return response
