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
    secret_name = "lb_stats_access2" #lb_stats_test
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

def questions(program,language,deployment):
    connection: Connection = get_db_connection()
    delimiter = '***'
    questions_fields=['id','name','question_label','type','data','data_other','required','constraint','relevant','choice_list','default','hint']
    questions_columns = questions_fields 
    choices_fields=['choice_id','choice_list','choice_label','value']
    choices_columns = choices_fields
    
    choices_columnsString = ""
    questions_columnsString = ""
    for c in choices_columns:
        choices_columnsString += 'c."' + c + '",'
    for c in questions_columns:
        questions_columnsString += '"' + c + '",'

    query = '''
                SELECT ''' + choices_columnsString.rstrip(",") + ''' 
                FROM uf_choices c
                JOIN uf_questions q
                ON c.choice_list = q.choice_list
                AND c.programid = q.programid
                WHERE q.programid = '%s' 
                AND q.language = '%s'
                AND q.deploymentnumber = %s
                ORDER by q."order",c."order";
 
                SELECT '%s';
            ''' % (program,language,deployment,delimiter) + '''
                SELECT ''' + questions_columnsString.rstrip(",") + '''
                FROM uf_questions
                WHERE programid = '%s' 
                AND language = '%s'
                AND deploymentnumber = %s
                ORDER BY "order";
            ''' % (program,language,deployment)

    sqlResult=connection.run(query)

    in_choices = True
    choiceLists = {}
    questions = []
    for row in sqlResult:
        if in_choices and row[0] == delimiter:
            in_choices = False
            continue
        elif in_choices:
            choice = {}
            for (enum,value) in enumerate(row):
                choice[choices_fields[enum]]=value
            list_name = choice.pop('choice_list')
            try:
                choiceLists[list_name].append(choice)
            except KeyError:
                choiceLists[list_name] = [choice]
        else:
            question = {}
            for (enum,value) in enumerate(row):
                question[questions_fields[enum]]=value
            choice_list_name = question.pop('choice_list')
            if choice_list_name != '':
                question['choices'] = choiceLists[choice_list_name]
            relevant = question.pop('relevant')
            if relevant != '' and relevant is not None:
                choiceList = choiceLists[relevant]
                choice = list(filter(lambda c:c['value']==question['name'],choiceList))
                choice[0].update(question)
            else:
                questions.append(question)
    return questions


def lambda_handler(event, context):
    #TODO: Error Handling!  
    #  For instance, if the choice_list in the uf_questions table doesn't have a match
    #  for the same programid in the uf_choices table, then the questions function
    #  above will throw a KeyError.  That shouldn't happen, but if it does, we need
    #  to return a 200 status code with some indication to the Vue App that something
    #  went wrong other than a network connection issue -- which is how Vue currently
    #  interprets all errors. 
    start = time.time_ns()

    # Parse out query string params
    program = event['queryStringParameters']['program']
    deployment = str(event['queryStringParameters']['deployment'])
    language = event['queryStringParameters']['language']

    # Get body of response object
    result = questions(program,language,deployment)

    #Return the response object
    return {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*","Content-Type":"application/json"},
    "body": json.dumps(result)
    }


if __name__ == '__main__':
    def test_main():

        submit_event = {'queryStringParameters': 
                        {'program': 'CARE-ETH-BOYS',
                        'deployment': 1,\
                        'language': 'aar'}
                        }
        print(lambda_handler(submit_event, None))
    
    test_main()
