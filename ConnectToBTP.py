import sys
import requests
import json
import logging
import time

logging.captureWarnings(True)

test_api_url = "https://6481e2fd-5b71-485d-994c-63bf74fd138a.abap-web.us10.hana.ondemand.com/sap/opu/odata4/sap/zblog/srvd/sap/zblog/0001/blog"
##https://6481e2fd-5b71-485d-994c-63bf74fd138a.abap-web.us10.hana.ondemand.com/ui#Shell-home

##
##    function to obtain a new OAuth 2.0 token from the authentication server
##
def get_new_token():
    auth_server_url = "https://78b24b89trial.authentication.us10.hana.ondemand.com/oauth/token"
    client_id       = 'sb-44b71cb0-2632-4d3d-978c-0513f03b9908!b255142|abap-trial-service-broker!b3132'
    client_secret   = 'e283e94e-9218-42a5-ad30-b8256ccd4df4$fgLE91-LSCkjarBFat0CQQzUM1hk1j7Ttj_tHuWF3pA='

    token_req_payload = {'grant_type': 'client_credentials'}
    #token_req_payload = {'grant_type': 'password'}


    token_response = requests.post(auth_server_url,
                                       data=token_req_payload, verify=False, allow_redirects=False,
                                   auth=(client_id, client_secret)
                                   #auth=('makra.consulting@gmail.com', 'y_2N83D#p$B4bA_')

    )

    if token_response.status_code != 200:
        print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
        sys.exit(1)

    print(token_response.text)
    tokens = json.loads(token_response.text)
    return tokens['access_token']

##
## 	obtain a token before calling the API for the first time
##
token = get_new_token()

##
##   call the API with the token
##
api_call_headers = {'Authorization': 'Bearer ' + token}
api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)

##
##
if api_call_response.status_code == 401:
    token = get_new_token()
else:
    print(api_call_response.text)

time.sleep(30)