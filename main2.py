import os
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
                                domain_name=tfe_domain_name)
    modules = tf_client.get_modules()
    for module in modules:
        search_text = build_search_text(domain_name=tfe_domain_name,
                                        organization=tfe_organization,
                                        name=module['attributes']['name'],
                                        provider=module['attributes']['provider'])
        print(search_text)
        results = az_client.search_code(az_devops_project, search_text)
        for result in results['results']:
            if str(result['fileName']).lower().endswith('.tf'):
                print(result['repository'])
