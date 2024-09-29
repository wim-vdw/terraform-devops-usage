import os
import hcl2
import tabulate
import urllib.parse
from helpers import AzureDevOpsClient, TerraformClient

az_devops_organization = os.environ.get('AZ_DEVOPS_ORGANIZATION')
az_devops_pat = os.environ.get('AZ_DEVOPS_PAT')
az_devops_project = os.environ.get('AZ_DEVOPS_PROJECT')
tfe_domain_name = os.environ.get('TFE_DOMAIN_NAME')
tfe_organization = os.environ.get('TFE_ORGANIZATION')
tfe_token = os.environ.get('TFE_TOKEN')
output_file_tf_workspaces = os.environ.get('OUTPUT_FILE_TF_WORKSPACES')
output_file_tf_modules = os.environ.get('OUTPUT_FILE_TF_MODULES')


def get_azurerm_version_details_in_repo(repo_id, repo_url, working_dir):
    result = []
    az_client = AzureDevOpsClient(organization=az_devops_organization,
                                  pat_token=az_devops_pat)
    files = az_client.get_files(project=az_devops_project, repo_id=repo_id, scope_path=working_dir)
    if files:
        for file in files['value']:
            if 'isFolder' not in file and str(file['path']).lower().endswith('tf'):
                file_path = str(file['path'])
                content = az_client.get_file_content(az_devops_project, repo_id, file_path)
                print(file_path)
                file_path_full = repo_url + '?path=' + file_path
                try:
                    content_parsed = hcl2.loads(content)
                    if 'terraform' in content_parsed:
                        tf_data = content_parsed['terraform']
                        for item in tf_data:
                            if 'required_providers' in item:
                                for provider in item['required_providers']:
                                    if 'azurerm' in provider:
                                        version = provider['azurerm'].get('version', None)
                                        print(version)
                                        result.append({
                                            'repo_id': repo_id,
                                            'file_path': file_path,
                                            'file_path_full': file_path_full,
                                            'version': version,
                                        })
                except Exception as e:
                    print("Error parsing file, please check manually.")
    else:
        print('No files found!')
    return result


def scan_all_workspaces():
    result = {}
    tf_client = TerraformClient(organization=tfe_organization,
                                token=tfe_token,
                                domain_name=tfe_domain_name,
                                verify=False)
    workspaces = tf_client.get_workspaces()
    for workspace in workspaces:
        tf_workspace_name = str(workspace['attributes']['name'])
        working_dir = workspace['attributes']['working-directory']
        repo_url = workspace['attributes']['vcs-repo']['repository-http-url']
        repo_id = str(workspace['attributes']['vcs-repo']['identifier']).split('/')[-1]
        print(tf_workspace_name, '=>', repo_url, '=>', working_dir)
        azurerm_version_details = get_azurerm_version_details_in_repo(repo_id=repo_id,
                                                                      repo_url=repo_url,
                                                                      working_dir=working_dir)
        result[tf_workspace_name] = azurerm_version_details
    return result


def scan_all_modules():
    result = {}
    tf_client = TerraformClient(organization=tfe_organization,
                                token=tfe_token,
                                domain_name=tfe_domain_name,
                                verify=False)
    tf_modules = tf_client.get_modules()
    for tf_module in tf_modules:
        tf_module_name = str(tf_module['attributes']['name'])
        working_dir = '/'
        repo_url = tf_module['attributes']['vcs-repo']['repository-http-url']
        repo_id = str(tf_module['attributes']['vcs-repo']['identifier']).split('/')[-1]
        print(tf_module_name, '=>', repo_url, '=>', working_dir)
        repo_details = get_azurerm_version_details_in_repo(repo_id=repo_id,
                                                           repo_url=repo_url,
                                                           working_dir=working_dir)
        result[tf_module_name] = repo_details
    return result


def generate_markdown_link(link, description):
    encoded_url = urllib.parse.quote(link, safe=":/?&=")
    return f'[{description}]({encoded_url})'


def generate_list_from_dict(data):
    result = []
    for name in sorted(data):
        for item in data[name]:
            markdown_link = generate_markdown_link(item['file_path_full'], item['file_path'])
            repo_id = item['repo_id']
            version = item['version']
            if not version:
                version = '⚠️ Not found ⚠️'
            result.append([name, repo_id, markdown_link, version])
    return result


def generate_markdown_table(headers, data, table_format='github'):
    return tabulate.tabulate(tabular_data=data, headers=headers, tablefmt=table_format)


def generate_report_terraform_workspaces():
    tf_workspaces = scan_all_workspaces()
    table_data = generate_list_from_dict(tf_workspaces)
    table_headers = ['Terraform workspace', 'GIT repo', 'File', 'AzureRM version']
    markdown_table = generate_markdown_table(headers=table_headers, data=table_data)
    markdown_report = '# Azure provider version in Terraform workspaces\n' + markdown_table
    with open(output_file_tf_workspaces, 'w') as f:
        f.write(markdown_report)


def generate_report_terraform_modules():
    tf_modules = scan_all_modules()
    table_data = generate_list_from_dict(tf_modules)
    table_headers = ['Terraform module', 'GIT repo', 'File', 'AzureRM version']
    markdown_table = generate_markdown_table(headers=table_headers, data=table_data)
    markdown_report = '# Azure provider version in Terraform modules\n' + markdown_table
    with open(output_file_tf_modules, 'w') as f:
        f.write(markdown_report)


if __name__ == '__main__':
    generate_report_terraform_modules()
    generate_report_terraform_workspaces()
