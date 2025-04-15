import psutil
import json
import os
import time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ---------- GCP Setup ----------
def get_gcp_client():
    key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "credentials", "gcp_key.json"))
    
    with open(key_path) as f:
        creds_dict = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    service = build("compute", "v1", credentials=credentials)
    return service, creds_dict["project_id"]

# ---------- VM Creation ----------
def create_vm(instance_name, zone="asia-south1-c"):
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

    print(f"[🚀 {datetime.now()}] Creating VM: {instance_name} in zone: {zone}")

    try:
        result = compute.instances().insert(
            project=project_id,
            zone=zone,
            body=config
        ).execute()

        print(f"[✅ {datetime.now()}] VM creation response:\n{json.dumps(result, indent=2)}")
        return result

    except Exception as e:
        print(f"[❌ {datetime.now()}] Failed to create VM: {e}")
        return None

# ---------- Autoscaler ----------
def autoscaler_loop(threshold=15, cooldown=10):
    vm_counter = 0
    print(f"🚦 Starting autoscaler loop. Threshold: {threshold}% CPU")

    while True:
        cpu_usage = psutil.cpu_percent(interval=2)
        print(f"[DEBUG] CPU Usage: {cpu_usage:.2f}%")

        if cpu_usage > threshold:
            instance_name = f"chatbot-vm-{int(time.time())}"
            print(f"[🔥 High CPU: {cpu_usage:.2f}%] Creating VM: {instance_name}")
            create_vm(instance_name)
            vm_counter += 1
            print(f"[🛑 Cooling] Waiting {cooldown} seconds...\n")
            time.sleep(cooldown)

        time.sleep(5)

# ---------- Run ----------
if __name__ == "__main__":
    autoscaler_loop()
