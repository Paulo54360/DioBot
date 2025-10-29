# Azure VM Diagnostics Workflow

This workflow collects diagnostic information from an Azure VM running Docker containers.

## Purpose

The `vm-diagnostics.yml` workflow is designed to help troubleshoot and monitor the state of:
- Cloud-init initialization status
- Docker service status  
- Running Docker containers
- Container logs (specifically for the n8n container)

## Prerequisites

Before using this workflow, you need to:

1. **Set up Azure credentials as a GitHub secret**:
   - Go to your repository Settings → Secrets and variables → Actions
   - Create a new secret named `AZURE_CREDENTIALS`
   - The value should be a JSON object with your Azure service principal credentials:
     ```json
     {
       "clientId": "<your-client-id>",
       "clientSecret": "<your-client-secret>",
       "subscriptionId": "<your-subscription-id>",
       "tenantId": "<your-tenant-id>"
     }
     ```

2. **Ensure Azure CLI access**:
   - Your service principal must have permissions to execute commands on the target VM
   - Required role: `Virtual Machine Contributor` or higher

## Usage

This is a manually triggered workflow. To run it:

1. Go to the **Actions** tab in your GitHub repository
2. Select **VM Diagnostics** from the workflows list
3. Click **Run workflow**
4. Fill in the required inputs:
   - **Resource Group**: The Azure resource group containing your VM (default: `projet-docker-rg`)
   - **VM Name**: The name of your virtual machine (default: `projet-docker-vm01`)
5. Click **Run workflow** to start the diagnostic collection

## Collected Information

The workflow collects the following diagnostics:

1. **cloud-init status**: Shows whether cloud-init has completed successfully
2. **cloud-init-output.log**: Last 300 lines of the cloud-init output log
3. **systemctl status docker**: Docker service status and recent logs
4. **docker ps -a**: List of all Docker containers (running and stopped)
5. **docker logs n8n**: Last 200 lines of logs from the n8n container
6. **VM IP Address**: Public IP address of the VM

## Output Filtering

The workflow automatically filters out Azure CLI noise messages including:
- "This is a sample script"
- "Optional parameters"
- "Enable succeeded"
- "[std" messages (stdout/stderr markers)

This ensures clean, readable diagnostic output.

## Troubleshooting

If the workflow fails:

- **Authentication errors**: Verify your `AZURE_CREDENTIALS` secret is correctly configured
- **VM not found**: Check that the resource group and VM name are correct
- **Empty output**: The VM may not be running, or the services may not be installed
- **Permission errors**: Ensure your service principal has the necessary permissions

## Example Output

When successful, you'll see output similar to:

```
📋 Collecte des diagnostics depuis la VM...

==========================================
== cloud-init status ==
==========================================
status: done

==========================================
== systemctl status docker ==
==========================================
● docker.service - Docker Application Container Engine
   Loaded: loaded
   Active: active (running)
...
```
