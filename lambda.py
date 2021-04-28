import json
import os
import requests
import us

API_KEY = os.environ['G_API']

def last_name_key(key):
    return key['last_name']

def state_key(key):
    return key['state']
    
def str_to_bool(v):
    if not v:
        return False
    elif v.lower() in ("true", "false"):
        return True if v.lower()  == 'true' else False
    else:
        # Construct the body of the response object
        transaction_response = {}
        transaction_response['error'] = f'{v} is an invalid bool'
    
        # Construct http response object
        response_object = {}
        response_object['statusCode'] = 400
        response_object['headers'] = {}
        response_object['headers']['Content-Type'] = 'application/json'
        response_object['body'] = json.dumps(transaction_response)
        return response_object

def google_civic_api_call(state=''):
    
    # variable and parameters 
    roles = "headOfGovernment"
    endpoint = "representatives"
    levels = 'administrativeArea1'
    url = f"https://www.googleapis.com/civicinfo/v2/{endpoint}"

    params = {
        'key': API_KEY,
        'address': state,
        'levels': levels,
        'roles': roles
    }
    
    # call api and store json object 
    response = requests.get(url=url, params=params)
    response_json = response.json()
    
    # get gov name and return with state 
    state_gov = response_json['officials'][0]['name']
    state_gov_split = state_gov.split(' ')
    first_name = state_gov_split[0]
    last_name = state_gov_split[-1]
    return {
        'last_name': last_name,
        'first_name': first_name,
        'state': state
    }

def get_governors(states='', sort_by_last_name=False, sort_by_state=False):
    
    # seperate state abreviations into list 
    state_abv_list = states.split(',')
    
    # create list of governor info 
    list_of_governors = []
    for state_abv in state_abv_list:
        us_state = us.states.lookup(state_abv)
        if not us_state:
            raise ValueError(f'Incorrect state: {state_abv}')
        else:
            us_state_name = us_state.name
            list_of_governors.append(google_civic_api_call(state=us_state_name))
    
    # return results 
    if sort_by_last_name:
        list_of_governors.sort(key=last_name_key)
        return list_of_governors
    elif sort_by_state:
        list_of_governors.sort(key=state_key)
        return list_of_governors
    else:
        return list_of_governors


def lambda_handler(event, context):
    
    # get parameters from http
    queryStringParameters = event.get('queryStringParameters')
    
    # check if states recieved. if not, return error 
    list_of_states = queryStringParameters.get('states')
    if not list_of_states.strip():
        # Construct the body of the response object
        transaction_response = {}
        transaction_response['error'] = 'states not provided'
    
        # Construct http response object
        response_object = {}
        response_object['statusCode'] = 400
        response_object['headers'] = {}
        response_object['headers']['Content-Type'] = 'application/json'
        response_object['body'] = json.dumps(transaction_response)
        return response_object

    # get sort_by parameters 
    get_sort_by_last_name = queryStringParameters.get('sort_by_last_name')
    get_sort_by_state = queryStringParameters.get('sort_by_state')
    
    # check to see if they are bool
    sort_by_last_name = str_to_bool(get_sort_by_last_name)
    sort_by_state = str_to_bool(get_sort_by_state)
    
    if isinstance(sort_by_last_name, dict):
        return sort_by_last_name
    if isinstance(sort_by_state, dict):
        return sort_by_state
    if sort_by_last_name and sort_by_state:
        # Construct the body of the response object
        transaction_response = {}
        transaction_response['error'] = 'can only sort by one parameter'
    
        # Construct http response object
        response_object = {}
        response_object['statusCode'] = 400
        response_object['headers'] = {}
        response_object['headers']['Content-Type'] = 'application/json'
        response_object['body'] = json.dumps(transaction_response)
        return response_object


    list_of_governors = get_governors(states=list_of_states, sort_by_last_name=sort_by_last_name, sort_by_state=sort_by_state)

    # Construct the body of the response object
    transaction_response = {}
    transaction_response['governors_list'] = list_of_governors

    # Construct http response object
    response_object = {}
    response_object['statusCode'] = 200
    response_object['headers'] = {}
    response_object['headers']['Content-Type'] = 'application/json'
    response_object['body'] = json.dumps(transaction_response)
    
    return response_object