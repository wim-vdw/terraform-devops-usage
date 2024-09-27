import requests
from requests.auth import HTTPBasicAuth


class AzureDevOpsClient:
    def __init__(self, organization, pat_token):
        self.organization = organization
        self.pat_token = pat_token
        self.base_url = f'https://dev.azure.com/{organization}/'
        self.base_url_alm_search = f'https://almsearch.dev.azure.com/{organization}/'
        self.auth = HTTPBasicAuth('', pat_token)

    def get_projects(self):
        url = self.base_url + '_apis/projects'
        params = {
            'api-version': '7.2-preview.4',
        }
        response = requests.get(url, auth=self.auth, params=params)
        if response.ok and response.status_code == 200:
            return response.json()
        else:
            return None

    def get_file_content(self, project, repo_id, file_path):
        url = self.base_url + f'{project}/_apis/git/repositories/{repo_id}/items'
        params = {
            'api-version': '7.1',
            'path': file_path,
        }
        response = requests.get(url, auth=self.auth, params=params)
        if response.ok and response.status_code == 200:
            return response.text
        else:
            return None

    def get_files(self, project, repo_id, scope_path='/'):
        url = self.base_url + f'{project}/_apis/git/repositories/{repo_id}/items'
        params = {
            'api-version': '7.1',
            'recursionLevel': 'Full',
            'includeContent': False,
            'scopePath': scope_path,
        }
        response = requests.get(url, auth=self.auth, params=params)
        if response.ok and response.status_code == 200:
            return response.json()
        else:
            return None

    def search_code(self, project, search_text):
        url = self.base_url_alm_search + f'{project}/_apis/search/codesearchresults?api-version=7.2-preview.1'
        response = requests.post(url, auth=self.auth, json={'searchText': search_text,
                                                            'includeFacets': True,
                                                            'includeSnippet': True,
                                                            '$Top': 1000})
        if response.ok and response.status_code == 200:
            return response.json()
        else:
            return None


class TerraformClient:
    def __init__(self, organization, token, domain_name, verify=True):
        self.organization = organization
        self.token = token
        self.domain_name = domain_name
        self.verify = verify
        self.base_url = f'https://{domain_name}/api/v2/'
        self.headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/vnd.api+json',
        }

    def get_modules(self):
        modules = []
        url = self.base_url + f'organizations/{self.organization}/registry-modules'
        while True:
            response = requests.get(url, headers=self.headers, verify=self.verify)
            if response.ok:
                result = response.json()
                modules.extend(result['data'])
                url = result['links']['next']
                if not url:
                    break
            else:
                break
        return modules

    def get_workspaces(self):
        workspaces = []
        url = self.base_url + f'organizations/{self.organization}/workspaces'
        while True:
            response = requests.get(url, headers=self.headers, verify=self.verify)
            if response.ok:
                result = response.json()
                workspaces.extend(result['data'])
                url = result['links']['next']
                if not url:
                    break
            else:
                break
        return workspaces

    @staticmethod
    def build_search_text(domain_name, organization, name, provider):
        return f'{domain_name}/{organization}/{name}/{provider}'
