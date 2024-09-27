# Azure DevOps and Terraform Enterprise Integration

## Introduction

This Python program automates the process of retrieving and analyzing Terraform files used to manage Azure resources
within an Azure DevOps environment. It integrates with both Azure DevOps and Terraform Enterprise to extract information
about workspaces, repositories, and required provider versions (specifically `azurerm`).

The script connects to Azure DevOps and Terraform Enterprise using API clients, processes the Terraform configurations
from repositories, and identifies Azure-specific provider versions used in the Terraform code.
