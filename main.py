import os
import requests
from requests.auth import HTTPBasicAuth

az_devops_organization = os.environ.get('AZ_DEVOPS_ORGANIZATION')
az_devops_pat = os.environ.get('AZ_DEVOPS_PAT')
tfe_domain_name = os.environ.get('TFE_DOMAIN_NAME')
tfe_organization = os.environ.get('TFE_ORGANIZATION')
tfe_token = os.environ.get('TFE_TOKEN')


def print_devops_projects():
    print(f'Azure DevOps projects for organization {az_devops_organization}:')
    url = f'https://dev.azure.com/{az_devops_organization}/_apis/projects?api-version=7.2-preview.4'
    basic = HTTPBasicAuth('', az_devops_pat)
    response = requests.get(url, auth=basic)
    if response.ok and response.status_code == 200:
        for project in response.json()['value']:
            print(project['name'])
    else:
        print('Error for:', url)


def print_terraform_modules():
    print(f'Terraform Enterprise modules for organization {tfe_organization}:')
    url = f'https://{tfe_domain_name}/api/v2/organizations/{tfe_organization}/registry-modules'
    headers = {
        'Authorization': 'Bearer ' + tfe_token,
        'Content-Type': 'application/json',
    }
    while True:
        response = requests.get(url, headers=headers)
        if response.ok:
            for module in response.json()['data']:
                print(module['attributes']['name'], module['attributes']['version-statuses'][0]['version'])
            url = response.json()['links']['next']
            if not url:
                break
        else:
            print('Error for:', url)
            break


if __name__ == '__main__':
    print_devops_projects()
    print()
    print_terraform_modules()
