import os
from helpers import AzureDevOpsClient, TerraformClient

az_devops_organization = os.environ.get('AZ_DEVOPS_ORGANIZATION')
az_devops_pat = os.environ.get('AZ_DEVOPS_PAT')
tfe_domain_name = os.environ.get('TFE_DOMAIN_NAME')
tfe_organization = os.environ.get('TFE_ORGANIZATION')
tfe_token = os.environ.get('TFE_TOKEN')

if __name__ == '__main__':
    az_client = AzureDevOpsClient(organization=az_devops_organization, pat_token=az_devops_pat)
    tf_client = TerraformClient(organization=tfe_organization, token=tfe_token, domain_name=tfe_domain_name)
    repos = az_client.get_projects()
    print(repos)
    code = az_client.get_file_content(project='AzureFoundation',
                                      repo_id='50bd7b13-fa67-4d28-8745-ab6ea6d3213f',
                                      file_path='/envs/dev/iris/dashboards.tf')
    print(code)
    search_results = az_client.search_code(project='AzureFoundation',
                                           search_text='tfe.azure.bnl-ms.myengie.com/engie-bnl-ms/portal-dashboard/azurerm')
    print(search_results)
    modules = tf_client.get_modules()
    for module in modules:
        print(module)
