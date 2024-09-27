import os
from os.path import split

from helpers import AzureDevOpsClient, TerraformClient

az_devops_organization = os.environ.get('AZ_DEVOPS_ORGANIZATION')
az_devops_pat = os.environ.get('AZ_DEVOPS_PAT')
az_devops_project = os.environ.get('AZ_DEVOPS_PROJECT')
tfe_domain_name = os.environ.get('TFE_DOMAIN_NAME')
tfe_organization = os.environ.get('TFE_ORGANIZATION')
tfe_token = os.environ.get('TFE_TOKEN')


def build_search_text(domain_name, organization, name, provider):
    return f'{domain_name}/{organization}/{name}/{provider}'


if __name__ == '__main__':
    az_client = AzureDevOpsClient(organization=az_devops_organization,
                                  pat_token=az_devops_pat)
    tf_client = TerraformClient(organization=tfe_organization,
                                token=tfe_token,
                                domain_name=tfe_domain_name,
                                verify=False)
    workspaces = tf_client.get_workspaces()
    for workspace in workspaces:
        if workspace['attributes']['name'] == 'Squad-SAP-Int':
            tf_workspace= workspace['attributes']['name']
            working_dir = workspace['attributes']['working-directory']
            repo_url = workspace['attributes']['vcs-repo']['repository-http-url']
            repo_id = str(workspace['attributes']['vcs-repo']['identifier']).split('/')[-1]
            path = workspace['attributes']['working-directory']
            files = az_client.get_files(az_devops_project, repo_id, scope_path=path)
            if files:
                print(files['count'])
                for file in files['value']:
                    print(file)
            else:
                print('No files found!')
