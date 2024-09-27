import os
import hcl2
import tabulate
import urllib.parse
from collections import defaultdict
from helpers import AzureDevOpsClient, TerraformClient

az_devops_organization = os.environ.get('AZ_DEVOPS_ORGANIZATION')
az_devops_pat = os.environ.get('AZ_DEVOPS_PAT')
az_devops_project = os.environ.get('AZ_DEVOPS_PROJECT')
tfe_domain_name = os.environ.get('TFE_DOMAIN_NAME')
tfe_organization = os.environ.get('TFE_ORGANIZATION')
tfe_token = os.environ.get('TFE_TOKEN')
output_file = os.environ.get('OUTPUT_FILE')


def scan_all_workspaces():
    az_client = AzureDevOpsClient(organization=az_devops_organization,
                                  pat_token=az_devops_pat)
    tf_client = TerraformClient(organization=tfe_organization,
                                token=tfe_token,
                                domain_name=tfe_domain_name,
                                verify=False)
    workspaces = tf_client.get_workspaces()
    result = defaultdict(list)
    for workspace in workspaces:
        tf_workspace = str(workspace['attributes']['name'])
        working_dir = workspace['attributes']['working-directory']
        repo_url = workspace['attributes']['vcs-repo']['repository-http-url']
        repo_id = str(workspace['attributes']['vcs-repo']['identifier']).split('/')[-1]
        print(tf_workspace, '=>', repo_url, '=>', working_dir)
        if tf_workspace.endswith('Int'):
            files = az_client.get_files(az_devops_project, repo_id, scope_path=working_dir)
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
                                                result[tf_workspace].append({
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


def generate_markdown_link(link, description):
    encoded_url = urllib.parse.quote(link, safe=":/?&=")
    return f'[{description}]({encoded_url})'


def generate_list_from_dict(dict_workspace_results):
    result = []
    for workspace in sorted(dict_workspace_results):
        for item in dict_workspace_results[workspace]:
            markdown_link = generate_markdown_link(item['file_path_full'], item['file_path'])
            repo_id = item['repo_id']
            version = item['version']
            if not version:
                version = '⚠️ Not found ⚠️'
            result.append([workspace, repo_id, markdown_link, version])
    return result


def generate_markdown_table(table_headers, table_data, table_format='github'):
    return tabulate.tabulate(table_data, headers=table_headers, tablefmt=table_format)


if __name__ == '__main__':
    all_workspaces = scan_all_workspaces()
    list_result = generate_list_from_dict(all_workspaces)
    headers = ['TFE workspace', 'GIT repo', 'File', 'AzureRM version']
    data = generate_markdown_table(headers, list_result)
    output = '# Azure provider version in TFE workspaces\n' + data
    with open(output_file, 'w') as f:
        f.write(output)
