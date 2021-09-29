import json
import time
import traceback
from typing import Optional

import boto3 as boto3
import pg8000.native
from botocore.exceptions import ClientError
from pg8000 import Connection, Cursor


########################################################################################################################
# Get a database connection

def _get_secret() -> dict:
    # Name of the secrets in secrets manager.
    secret_name = "lb_stats_test" #lb_stats_access2
    region_name = "us-west-2"

    result = None

    start = time.time()

    # Create a Secrets Manager client
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
    except Exception as e:
        print('    Exception getting session client: {}, elapsed: {}'.format(str(e), time.time() - start))
        raise e

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            result = json.loads(secret)
        # else:
        # Our secrets are text, so we don't need this.
        #     decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        #     result = decoded_binary_secret

    # Your code goes here.
    return result


_db_connection: Optional[Connection] = None


def get_db_connection() -> Connection:
    global _db_connection
    if _db_connection is None:
        secret = _get_secret()

        parms = {'database': 'dashboard', 'user': secret['username'], 'password': secret['password'],
                 'host': secret['host'], 'port': secret['port']}

        _db_connection = pg8000.native.Connection(**parms)
    return _db_connection


########################################################################################################################

# noinspection SqlNoDataSourceInspection,SqlResolve
def update_db(command):
    connection: Connection = get_db_connection()
    resp = connection.run(command) 
    connection.close
    return resp
 
def sql_from_body(body): 
    submit_responses = body['responses']
    set_clause = 'SET is_useless=' + str(body['useless']) + ','
    set_clause += "submit_time=NOW(),analyst_email='" + body['user_email'].lower() + "',"
    for key in submit_responses:
        value = submit_responses[key]
        if isinstance(value,list) and len(value)>0:
            value_one_str = ';'.join(value).replace("'",'"') # change ' to " for postgresql 
            set_clause += key + "='" + value_one_str+ "'," 
        elif not isinstance(value,list):
            set_clause += key + "='" + str(value).replace("'",'"') + "',"  # replace to change ' to " for postgresql
    command = 'UPDATE uf_analysis ' + set_clause.rstrip(",") + " WHERE message_uuid = '" + body['uuid'] +"'"
    return command

def lambda_handler(event, context):
    start = time.time_ns()

    # Get body of response object
    bodystring = event['body']
    body = json.loads(bodystring)    
    command = sql_from_body(body)
    update_db(command)

    #Return the response object
    return {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*","Content-Type":"application/json"}
    }


if __name__ == '__main__':
    def test_main():
        event_text = '{"body":{"uuid":"626c01b2-78a1-5233-99e9-7efa07478b99","user_email":"cliff@amplio.org","useless":true,"responses":{"transcription":"transcription goes here","resp_01":"endorsement","resp_02":"maybe","resp_03":"breastfeeding","resp_04":[],"resp_05":["myths"],"resp_06":[],"resp_07":[],"resp_08":["nofood","nutrition","latching","colostrum"],"resp_09":["guidance"],"resp_10":"more here","resp_11":[],"resp_12":[],"resp_13":[],"resp_14":[],"resp_15":[],"resp_16":[],"resp_17":[],"resp_18":[],"resp_19":[],"resp_20":[]}}}'
        event = json.loads(event_text)
        
        lambda_handler(event, None)

    test_main()
