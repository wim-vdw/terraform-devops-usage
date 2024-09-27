import os
import hcl2

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
    result = []
    for workspace in workspaces:
        if workspace['attributes']['name'] != 'nothing will be skipped':
            tf_workspace = workspace['attributes']['name']
            working_dir = workspace['attributes']['working-directory']
            repo_url = workspace['attributes']['vcs-repo']['repository-http-url']
            repo_id = str(workspace['attributes']['vcs-repo']['identifier']).split('/')[-1]
            print(tf_workspace, '=>', repo_url, '=>', working_dir)
            files = az_client.get_files(az_devops_project, repo_id, scope_path=working_dir)
            if files:
                for file in files['value']:
                    if 'isFolder' not in file and str(file['path']).lower().endswith('tf'):
                        content = az_client.get_file_content(az_devops_project, repo_id, file['path'])
                        print(file['path'])
                        try:
                            content_parsed = hcl2.loads(content)
                            if 'terraform' in content_parsed:
                                tf_data = content_parsed['terraform']
                                print(file['path'])
                                for item in tf_data:
                                    if 'required_providers' in item:
                                        for provider in item['required_providers']:
                                            if 'azurerm' in provider:
                                                version = provider['azurerm'].get('version', 'VERSION-NOT-SPECIFIED')
                                                print(version)
                                                result.append((tf_workspace, repo_id, file['path'], version))
                        except Exception as e:
                            print("Error parsing file, please check manually")
            else:
                print('No files found!')
    for item in result:
        print(item)
