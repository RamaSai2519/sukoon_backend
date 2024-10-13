from configs import CONFIG as config
import re
import json
from boto3 import Session as AWSSession
from botocore.client import Config
from botocore.exceptions import ClientError
from requests_aws4auth import AWS4Auth
from gql import gql
from gql.client import Client
from gql.transport.requests import RequestsHTTPTransport

class GQLClient:
    @staticmethod
    def instance():
        if "_instance" not in GQLClient.__dict__:
            GQLClient._instance = GQLClient()
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Api-Key": config.APPSYNC_API_KEY,
            }

            aws = AWSSession(region_name=config.AWS_DEFAULT_REGION)
            credentials = aws.get_credentials().get_frozen_credentials()

            auth=AWS4Auth(
                credentials.access_key,
                credentials.secret_key,
                aws.region_name,
                "appsync",
                session_token=credentials.token,
            )

            GQLClient.transport = RequestsHTTPTransport(
                url=config.APPSYNC_ENDPOINT, headers=headers, auth=auth
            )
            GQLClient.client = Client(
                transport=GQLClient.transport,
                fetch_schema_from_transport=False,
            )
            print("Returning the first singleton call of client")
            return GQLClient._instance
        
        else:
            print("Returning the second singleton call of client")
            return GQLClient._instance
        
def get_gql_instance():
    return GQLClient.instance()

def execute_gql_call(client, query, params):
    return client.execute(gql(query), variable_values=json.dumps(params))


def call_graphql(query, params, message):
    client = get_gql_instance().client
    formatted_query = None

    try:
        formatted_query = re.sub(" +", "", str(query).replace("\n", ""))
        resp = execute_gql_call(client, query, params)
        print(f"{message} executed with the following query {formatted_query}")

    except Exception as e:
        _q = formatted_query or query
        print(f" {message} failed. The exception raised is {repr(e)} {e}: and params: {params}. The query is {_q}")
        return False
    
    return resp


