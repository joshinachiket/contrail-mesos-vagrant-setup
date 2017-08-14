import requests
import json
import yaml

with open('config.yaml', 'r') as config:
  url_file = yaml.load(config)

url = url_file["vms"]["url"]

print ("Marathon is up at url: " + url)

payload = "{\n  \"id\": \"mongo5\",\n  \"cmd\" : \"ping 1.1.1.1\",\n  \"cpus\": 0.3,\n  \"mem\": 256,\n  \"disk\": 0,\n  \"instances\": 1,\n  \"container\": {\n    \"type\": \"MESOS\",\n    \"volumes\": [],\n    \"docker\": {\n      \"image\": \"alpine\",\n      \"forcePullImage\": true\n    }\n  },\n  \"ipAddress\": {\n    \"networkName\": \"contrail-cni-plugin\",\n    \"labels\": {\n      \"networks\": \"blue-network\",\n      \"network-subnets\": \"5.5.5.0/24\",\n      \"project-name\": \"default-project\",\n      \"domain-name\": \"default-domain\"\n    }\n  }\n}"

headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

# response = requests.request("POST", url, data=payload, headers=headers)

values = json.loads(response.text)

try:
   if str(values['message']):
     print("***Task Scheduling failed with ERROR - " + str(values['message']))
except:
   print("***Task has been Scheduled wit ID - " + str(values['id']))
