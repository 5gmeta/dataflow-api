#import requests
import json
from ast import literal_eval
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

def createKeycloakAuthorization (username, topic):

    # api-endpoint
    REALM = "<realm name>" #To be configured
    URL = "<Keycloak endpoint>/admin/realms/"+REALM #To be configured
    TOKEN_URL = URL+"/protocol/openid-connect/token"
    KAFKA_CLIENT = "<Kafka client>" #To be configured

    # Oauth2
    client_id = "<admin client>" #To be configured
    client_secret = "<client secret>" #To be configured

    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=TOKEN_URL, client_id=client_id, client_secret=client_secret)

    # Input

    kafka_client = KAFKA_CLIENT
    resource_name = "Topic:"+topic
    policy_name = username
    topic_permission_name = username+"-access-"+topic

    headers = {"Content-Type": "application/json"}

    # Get Kafka client ID
    r = oauth.get(url=URL+"/clients")
    print("Getting client id...")

    clients = r.json()
    kafka_client_id = ""
    kafka_client_exists = False

    for i in range(len(clients)):
        if clients[i]["clientId"] == kafka_client:
            kafka_client_id=clients[i]["id"]
            kafka_client_exists=True
            print("Success")
            break

    if not kafka_client_exists:
        print("Error: cannot find Kafka client")
        exit(1)

    # Get User id
    r = oauth.get(url=URL+"/users")
    print("Getting user id...")

    users = r.json()
    user_exists = False
    user_id = ""

    for i in range(len(users)):
        if users[i]["username"] == username:
            user_id=users[i]["id"]
            user_exists=True
            print("Success")
            break

    if not user_exists:
        print("Error: cannot find user")
        exit(1)

    # Create scopes dictionary
    r = oauth.get(url=URL+"/clients/"+kafka_client_id+"/authz/resource-server/scope")
    print("Get scopes id: ")
    print(r)
    print("\n")

    scopes = r.json()
    scopes_dict = {}

    for i in range(len(scopes)):
        name = scopes[i]["name"]
        id = scopes[i]["id"]
        scopes_dict[name]=id

    # Create resource
    data = json.dumps(
        {
            "name": resource_name,
            "displayName": "",
            "type": "Topic",
            "icon_uri": "",
            "scopes": [
                {
                    "name": "Read",
                    "id": scopes_dict["Read"],
                    "iconUri": ""
                },
                {
                    "name": "Delete",
                    "id": scopes_dict["Delete"],
                    "iconUri": ""
                },
                {
                    "name": "Describe",
                    "id": scopes_dict["Describe"],
                    "iconUri": ""
                }
            ],
            "ownerManagedAccess": False,
            "attributes": "{}"
        }
    )

    r = oauth.post(url=URL+"/clients/"+kafka_client_id+"/authz/resource-server/resource", headers=headers, data=data)
    print("Create resource: ")
    print(r)
    print("\n")

    resource_id = r.json()['_id']

    # Create policy
    # Check if policy already exists

    print("Create policy: ")

    r = oauth.get(url=URL+"/clients/"+kafka_client_id+"/authz/resource-server/policy")
    policies = r.json()
    policy_id=""
    policy_exists=False

    for i in range(len(policies)):
        if policies[i]["name"] == policy_name:
            policy_id=policies[i]["id"]
            policy_exists=True
            print("Policy already exists: "+policy_id)
            break

    if not policy_exists:
        data = json.dumps(
            {
                "users": [
                    user_id
                ],
                "logic": "POSITIVE",
                "name": policy_name,
                "description": ""
            }
        )

        r = oauth.post(url=URL+"/clients/"+kafka_client_id+"/authz/resource-server/policy/user", headers=headers, data=data)
        print(r)
        print("\n")
        policy_id = r.json()['id']

    # Create permission
    data = json.dumps(
        {
            "resources": [
                resource_id
            ],
            "policies": [
                policy_id
            ],
            "name": topic_permission_name,
            "description": "",
            "decisionStrategy": "UNANIMOUS"
        }
    )

    r = oauth.post(url=URL+"/clients/"+kafka_client_id+"/authz/resource-server/permission/resource", headers=headers, data=data)
    print("Create permission: ")
    print(r)
    print("\n")

    return "Authorization created."