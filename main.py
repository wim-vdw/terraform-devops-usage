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


def print_devops_repositories():
    print(f'Azure DevOps repositories for organization {az_devops_organization}:')
    project = 'AzureFoundation'
    url = f'https://almsearch.dev.azure.com/{az_devops_organization}/{project}/_apis/search/codesearchresults?api-version=6.0-preview.1'
    headers = {
        'Content-Type': 'application/json',
    }
    basic = HTTPBasicAuth('', az_devops_pat)
    response = requests.post(url, auth=basic, headers=headers, data={'searchText': 'Dashboard', 'includeFacets': True})
    if response.ok and response.status_code == 200:
        print(response.json())
    else:
        print('Error for:', url)
        print(response.json())
        print(response.content)


def print_terraform_modules():
    print(f'Terraform Enterprise modules for organization {tfe_organization}:')
    url = f'https://{tfe_domain_name}/api/v2/organizations/{tfe_organization}/registry-modules'
    headers = {
        'Authorization': 'Bearer ' + tfe_token,
        'Content-Type': 'application/vnd.api+json',
    }
    while True:
        response = requests.get(url, headers=headers)
        if response.ok:
            for module in response.json()['data']:
                name = module['attributes']['name']
                provider = module['attributes']['provider']
                version = module['attributes']['version-statuses'][0]['version']
                search = f'tfe.azure.bnl-ms.myengie.com/{tfe_organization}/{name}/{provider}'
                print(name, provider, version, search)
            url = response.json()['links']['next']
            if not url:
                break
        else:
            print('Error for:', url)
            break


def print_terraform_workspaces():
    print(f'Terraform Enterprise workspaces for organization {tfe_organization}:')
    url = f'https://{tfe_domain_name}/api/v2/organizations/{tfe_organization}/workspaces'
    headers = {
        'Authorization': 'Bearer ' + tfe_token,
        'Content-Type': 'application/vnd.api+json',
    }
    while True:
        response = requests.get(url, headers=headers)
        if response.ok:
            for workspace in response.json()['data']:
                name = workspace['attributes']['name']
                workspace_id = workspace['id']
                print(name, workspace_id)
            url = response.json()['links']['next']
            if not url:
                break
        else:
            print('Error for:', url)
            break


def print_terraform_workspace_resources(workspace_id):
    print(f'Terraform Enterprise resources for workspace {workspace_id}:')
    url = f'https://{tfe_domain_name}/api/v2/workspaces/{workspace_id}/resources'
    headers = {
        'Authorization': 'Bearer ' + tfe_token,
        'Content-Type': 'application/vnd.api+json',
    }
    while True:
        response = requests.get(url, headers=headers)
        if response.ok:
            for resource in response.json()['data']:
                print(resource)
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
    print()
    print_terraform_workspaces()
    print()
    print_devops_repositories()
    print()
    print_terraform_workspace_resources('ws-hHbeMQKxPJvuLbUb')
