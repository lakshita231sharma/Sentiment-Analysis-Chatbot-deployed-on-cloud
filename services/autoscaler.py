import psutil
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials
def get_gcp_client():
    # Build full absolute path to credentials file
    key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credentials", "gcp_key.json"))
    
    with open(key_path) as f:
        creds_dict = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    service = build("compute", "v1", credentials=credentials)
    return service, creds_dict["project_id"]

# Function to create a new VM
def create_vm(instance_name, zone="us-central1-a"):
    compute, project_id = get_gcp_client()

    config = {
        "name": instance_name,
        "machineType": f"zones/{zone}/machineTypes/e2-micro",
        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": "projects/debian-cloud/global/images/family/debian-11"
                }
            }
        ],
        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}]
            }
        ],
        "serviceAccounts": [
    {
        "email": "chatbot-autoscaler@assign-454218.iam.gserviceaccount.com",
        "scopes": ["https://www.googleapis.com/auth/cloud-platform"]
    }
]

    }

    print(f"Creating VM: {instance_name}")
    print(f"Using project: {project_id}, zone: {zone}")
    
    operation = compute.instances().insert(
        project=project_id,
        zone=zone,
        body=config
    ).execute()

    return operation
