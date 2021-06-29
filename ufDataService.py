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
    secret_name = "lb_stats_access2"
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
def get_next_uuid(connection, program, deployment_number, language):
    MIN_SECONDS_FILTER = 5
    command = '''INSERT INTO uf_analysis (message_uuid,start_time)
                    SELECT message_uuid, NOW() FROM public.uf_messages
                    WHERE programid = :program and deploymentnumber = :deployment_number
                    and length_seconds >= :min_sec and language= :language and message_uuid NOT IN 
                        (SELECT message_uuid FROM uf_analysis 
                        WHERE submit_time IS NOT NULL 
                        OR start_time > (NOW() - 15 * interval '1 minute'))
                    LIMIT 1
                ON CONFLICT (message_uuid) DO UPDATE SET start_time=NOW()
                RETURNING message_uuid'''
    resp = connection.run(command,program=program,deployment_number=deployment_number,language=language,min_sec=MIN_SECONDS_FILTER)
    return resp[0][0]


def get_uuid_metadata(connection,uuid):
    resp = {}
    command =    '''SELECT region,district,communityname,groupname,listening_model
                    FROM public.uf_messages m
                    JOIN recipients r
                    ON m.recipientid = r.recipientid
                    WHERE message_uuid = :uuid'''
    sqlmeta=connection.run(command,uuid=uuid)[0]
    resp.update({"region":sqlmeta[0]})
    resp.update({"district":sqlmeta[1]})
    resp.update({"community":sqlmeta[2]})
    resp.update({"group":sqlmeta[3]})
    resp.update({"listening_model":sqlmeta[4]})
    return resp


def get_progress(connection,user_email,program,deployment_number,language):
    resp = {}
    command =    '''SELECT (analyst_email=:user) AS for_user, is_useless, count(*) 
                    FROM uf_analysis a
                    JOIN uf_messages m
                    ON a.message_uuid=m.message_uuid
                    WHERE m.programid=:program AND deploymentnumber=:deployment_number AND language=:language
                    AND submit_time IS NOT NULL
                    GROUP BY (analyst_email=:user),is_useless
                    order by (analyst_email=:user),is_useless'''
    sqlprogress=connection.run(command,user=user_email,program=program,deployment_number=deployment_number,language=language)
    if len(sqlprogress) != 0:
        resp.update({"others_feedback":sqlprogress[0][2]})
        resp.update({"others_recordings":(sqlprogress[0][2] + sqlprogress[1][2])}) # useless + not useless
        resp.update({"users_feedback":sqlprogress[2][2]})
        resp.update({"users_recordings":(sqlprogress[2][2] + sqlprogress[3][2])}) # useless + not useless
    return resp


def get_uf_data(user_email, program, deployment_number, language):
    all_data = {} 
    connection: Connection = get_db_connection()
    
    uuid = get_next_uuid(connection,program,deployment_number,language)
    all_data.update({"uuid":uuid})

    metadata=get_uuid_metadata(connection,uuid)
    all_data.update(metadata)
 
    progress=get_progress(connection,user_email,program,deployment_number,language)
    all_data.update(progress)

    # # Hardcoding this little dictionary until I know what database tables give us this info
    # program_to_uuid = {}
    # program_to_uuid.update({"CARE-ETH-GIRLS":"e6555298-baf5-4230-8226-f2783ed15649"})
    # program_to_uuid.update({"CARE-ETH-BOYS":"24fdd340-a6dc-453f-a94c-6260fdebdf9b"})

    #form the URL
    url = "https://downloads.amplio.org/" + program + "/deployment-" + deployment_number
    url += "/" + language + "/" + uuid + ".mp3"
    all_data.update({"url":url})

    connection.close
    return all_data    


def lambda_handler(event, context):
    start = time.time_ns()

    # Parse out query string params
    email = event['queryStringParameters']['email']
    program = event['queryStringParameters']['program']
    deployment = str(event['queryStringParameters']['deployment'])
    language = event['queryStringParameters']['language']
    # print('email:'+email)
    # print('program:'+program)
    # print('deployment:'+deployment)
    # print('language:'+language)
    
    # Get body of response object
    result = get_uf_data(email,program,deployment,language)

    #Return the response object
    return {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*","Content-Type":"application/json"},
    "body": json.dumps(result)
    }


if __name__ == '__main__':
    def test_main():
        submit_event = {'queryStringParameters': 
                        {'email':'cliff@amplio.org',
                        'program': 'CARE-ETH-GIRLS',
                        'deployment': 1,\
                        'language': 'aar'}
                        }
        print(lambda_handler(submit_event, None))

    test_main()
