import json
import time
import traceback
from typing import Optional

import boto3 as boto3
import pg8000.native
from botocore.exceptions import ClientError
from pg8000 import Connection, Cursor

MINIMUM_SECONDS_FILTER = 5   # filters out any UF messages of less than this # of seconds
MAXIMUM_MINUTES_CHECKOUT = 5  # re-issues the same UUID after this many minutes if the form hasn't yet been submitted

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

def get_submissions_list(connection, program, deployment_number, language, email, timezoneOffset):    
    command = '''SELECT a.message_uuid, date_trunc('second',submit_time AT TIME ZONE INTERVAL ' '''+timezoneOffset+''' '),is_useless 
                    FROM uf_messages m 
                    JOIN uf_analysis a ON m.message_uuid = a.message_uuid
                    WHERE programid = :program and deploymentnumber = :deployment_number
                    and length_seconds >= :min_sec and language = :language  
                    and submit_time IS NOT NULL and analyst_email = :email
                    ORDER BY submit_time DESC'''
    sqlSubmissions = connection.run(command,program=program,deployment_number=deployment_number,language=language,email=email,timezoneOffset=timezoneOffset,min_sec=MINIMUM_SECONDS_FILTER)
    submissions = []
    for s in sqlSubmissions:
        submission = {}
        submission['uuid']=s[0]
        submission['submissionTime']=s[1]
        submission['feedback']='no' if s[2] else 'yes'
        submissions.append(submission)
    return submissions

def to_array(text):
    arr = []
    return arr

def get_submission(connection,uuid):
    MAX_RESPONSES = 30
    columns = []
    sql = 'SELECT "is_useless", '
    for r in range(1,MAX_RESPONSES +1 ):
        column = 'resp_' + ('0'+str(r) if r<10 else str(r))
        columns.append(column)
        sql += '"' + column + '",'
        column += '_o'
        columns.append(column)
        sql += '"' + column + '",'
    sql = sql.rstrip(",") + " FROM uf_analysis WHERE message_uuid = '" + uuid + "'"
    sqlResult=connection.run(sql)
    submission = {}
    submission['uuid'] = uuid
    submission['useless'] = sqlResult[0][0]
    responses = {}
    for r in range(1,MAX_RESPONSES*2):
        value = sqlResult[0][r]
        # convert the text into array, even if array size is 1, in case its a checkbox multi-select (when js needs an array)
        # if value == None or value == '':
            # value = []
        # elif r % 2 == 1: #no need to convert the text fields for "_o"/other 
            # value = value.split(";")
        responses[columns[r-1]] = value
    submission['responses'] = responses
    return submission

    

def get_next_uuid(connection, program, deployment_number, language):
    command = '''INSERT INTO uf_analysis (message_uuid,start_time)
                    SELECT message_uuid, NOW() FROM public.uf_messages
                    WHERE programid = :program and deploymentnumber = :deployment_number
                    and length_seconds >= :min_sec and language= :language and message_uuid NOT IN 
                        (SELECT message_uuid FROM uf_analysis 
                        WHERE submit_time IS NOT NULL 
                        OR start_time > (NOW() - :max_min * interval '1 minute'))
                    LIMIT 1
                ON CONFLICT (message_uuid) DO UPDATE SET start_time=NOW()
                RETURNING message_uuid'''
    resp = connection.run(command,program=program,deployment_number=deployment_number,language=language,min_sec=MINIMUM_SECONDS_FILTER,max_min=MAXIMUM_MINUTES_CHECKOUT)
    return resp


def get_uuid_metadata(connection,uuid):
    audioMetadata = {}
    command =    '''SELECT title,region,district,communityname,groupname,listening_model
                    FROM uf_messages m
                    JOIN recipients r
                    ON m.recipientid = r.recipientid
                    LEFT JOIN contentmetadata2 c
                    ON m.relation = c.contentid
                    WHERE message_uuid = :uuid'''

    sqlmeta=connection.run(command,uuid=uuid)[0]
    audioMetadata.update({"title":sqlmeta[0]})
    audioMetadata.update({"region":sqlmeta[1]})
    audioMetadata.update({"district":sqlmeta[2]})
    audioMetadata.update({"community":sqlmeta[3]})
    audioMetadata.update({"group":sqlmeta[4]})
    audioMetadata.update({"listening_model":sqlmeta[5]})
    #audioMetadata = {'audioMetadata':audioMetadata}
    return audioMetadata

def num_from_array(array):
    if len(array) == 0:
        return 0
    else:
        return array[0][3]


def get_progress(connection,user_email,program,deployment_number,language):
    progress = {}
    command =    '''SELECT (submit_time IS NULL), (analyst_email=:user), is_useless, count(*) 
                    FROM uf_messages m
                    LEFT JOIN uf_analysis a
                    ON a.message_uuid=m.message_uuid
                    WHERE m.programid=:program AND deploymentnumber=:deployment_number AND language=:language
                    AND length_seconds >= :min_length
                    GROUP BY (submit_time IS NULL),(analyst_email=:user),is_useless
                    ORDER BY (submit_time IS NULL),(analyst_email=:user),is_useless'''
    sqlprogress=connection.run(command,user=user_email,program=program,deployment_number=deployment_number,language=language,min_length=MINIMUM_SECONDS_FILTER)
    other_feedback = num_from_array(list(filter(lambda r:r[1]==False and r[2]==False,sqlprogress)))
    other_useless = num_from_array(list(filter(lambda r:r[1]==False and r[2]==True,sqlprogress)))
    user_feedback = num_from_array(list(filter(lambda r:r[1]==True and r[2]==False,sqlprogress)))
    user_useless = num_from_array(list(filter(lambda r:r[1]==True and r[2]==True,sqlprogress)))
    not_analyzed = num_from_array(list(filter(lambda r:r[0]==True,sqlprogress)))
    
    user_recordings = user_feedback + user_useless
    other_recordings = other_feedback + other_useless
    all_recordings = user_recordings + other_recordings + not_analyzed
    
    progress.update({"others_feedback":other_feedback})
    progress.update({"others_recordings":other_recordings})
    progress.update({"users_feedback":user_feedback})
    progress.update({"users_recordings":user_recordings})
    progress.update({'totalReceivedMessages':all_recordings})
    return progress


def get_uf_data(connection, user_email, program, deployment_number, language, uuid):
    all_data = {"audioMetadata":{},"progress":{}} 
    url = "" #empty string means no more messages available to process
    
    if uuid is None:
        sqlResponse = get_next_uuid(connection,program,deployment_number,language)
        if len(sqlResponse) > 0:
            uuid = sqlResponse[0][0]
    else:
        all_data["audioMetadata"].update({"submission":get_submission(connection,uuid)})
    # check if there are any uf_messages to process for this program/deployment/language
    if uuid is not None:
        metadata=get_uuid_metadata(connection,uuid)
        metadata.update({"uuid":uuid})
        all_data["audioMetadata"].update(metadata)
        #form the URL
        url = "https://downloads.amplio.org/" + program + "/deployment-" + deployment_number
        url += "/" + language + "/" + uuid + ".mp3"    
    all_data["audioMetadata"].update({"url":url}) #empty string url means no more messages to process
    progress=get_progress(connection,user_email,program,deployment_number,language)
    all_data["progress"].update(progress)


    connection.close
    return all_data    


def lambda_handler(event, context):
    start = time.time_ns()
    uuid = None

    # Parse out query string params
    email = event['queryStringParameters']['email']
    program = event['queryStringParameters']['program']
    deployment = str(event['queryStringParameters']['deployment'])
    language = event['queryStringParameters']['language']
    if 'uuid' in event['queryStringParameters']:
        uuid = event['queryStringParameters']['uuid']
    if 'timezoneOffset' in event['queryStringParameters']:
        timezoneOffset = event['queryStringParameters']['timezoneOffset']

    connection: Connection = get_db_connection()

    if uuid == 'all':
        result = get_submissions_list(connection, program, deployment, language, email, timezoneOffset)
    else:
        # Get body of response object
        result = get_uf_data(connection, email,program,deployment,language, uuid)

    #Return the response object
    return {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*","Content-Type":"application/json"},
    "body": json.dumps(result,default=str)
    }


if __name__ == '__main__':
    def test_main():
        submit_event1a = {'queryStringParameters': 
                        {'email':'Abdu.Yimam@care.org',
                        'program': 'CARE-ETH-BOYS',
                        'deployment': 1,
                        'language': 'aar'}
                        }
        submit_event1b = {'queryStringParameters': 
                        {'email':'cliff@amplio.org',
                        'program': 'CARE-ETH-GIRLS',
                        'deployment': 1,
                        'language': 'aar'}
                        }
        submit_event2 = {'queryStringParameters': 
                        {'email':'cliff@amplio.org',
                        'program': 'CARE-ETH-GIRLS',
                        'deployment': 1,
                        'language': 'aar',
                        'uuid': '9c06d847-1baa-5bbe-829d-c3a24bdc827e'}
                        }
        submit_event3 = {'queryStringParameters': 
                        {'email':'Abdu.Yimam@care.org',
                        'program': 'CARE-ETH-BOYS',
                        'deployment': 1,
                        'language': 'aar',
                        'uuid': 'all',
                        'timezoneOffset': '-420 minutes'}
                        }
        submit_event3b = {'queryStringParameters': 
                        {'email':'cliff@amplio.org',
                        'program': 'CARE-ETH-BOYS',
                        'deployment': 1,
                        'language': 'aar',
                        'uuid': 'all',
                        'timezoneOffset': '-420 minutes'}
                        }
        print(lambda_handler(submit_event3b, None))
        
    test_main()
