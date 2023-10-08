import os
import requests
from requests.auth import HTTPBasicAuth

organization = os.environ.get('AZ_DEVOPS_ORGANIZATION')
pat = os.environ.get('AZ_DEVOPS_PAT')


def print_devops_projects():
    print(f'Azure DevOps projects for organization {organization}:')
    url = f'https://dev.azure.com/{organization}/_apis/projects?api-version=7.2-preview.4'
    basic = HTTPBasicAuth('', pat)
    response = requests.get(url, auth=basic)
    if response.ok and response.status_code == 200:
        for project in response.json()['value']:
            print(project['name'])
    else:
        print('Error for:', url)


if __name__ == '__main__':
    print_devops_projects()
