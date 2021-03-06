# -*- coding: utf-8 -*-

import requests
import os
import json
import logging
import sys

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)


#base_url = "http://127.0.0.1:8001"

# env variable
namespace = os.getenv("res_namespace", "default")
base_url = os.getenv("base_url", "https://192.168.99.108:8443")
mytoken = os.getenv("mytoken", "eyJhbGciOiJSUzI1NiIsImtpZCI6IkxqMjFzMlpoQnA2S3haUzdFTXU2UUQ2cVREejhQdm9CdE5RUVFpNmZVRlkifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJyb2JvdC10b2tlbi12cnY4bSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJyb2JvdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjZhNDIxOGY1LTdhZTgtNDQ5ZS05NmUxLTQwNTI1ZjNjODE3MiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTpyb2JvdCJ9.bsirEsoBixTRmkgnw0tWx-GSXTqKxvRqjZIID9Q4YAg_ZFvik1rupcWQnZY2qmjBpqDBBEKgPmlUpWfeeU3z-E3KdIwRAfqAnI9ee0Qdq98rp1zXTHpxEFxSL1m8s5JYAHt6LQru3-ov5529WAmhak06wc8mJLqWQANDGoVMIaWgaU2mnPtBXoZHYBTCkpr8lqNmIPwrv3NBcgJsMG39hA_ufA9TRjzaNrjCEuDE_sxa4CJQH_QtW5Eu1K3Cm5dASU1mcNUxX6O49ljOnEwEQsahw03a1FoGNkRidNH9Q--jFAVGgPkXdGO2Q7syFgtwYy7JpWzVlzxhf2NkI7gOgQ")
mytoken = mytoken.rstrip()
headers = {'Authorization': 'Bearer {}'.format(mytoken)}

# This is the function that searches for and kills Pods by searching for them by label
def api_return(url):
   r=requests.get(url, headers=headers, verify=False)
   t=json.loads(r.content)
   return t

def kill_pods(labels):
    # We receive labels in the form of a list
    for label in labels:
        url = "{}/api/v1/namespaces/{}/pods?labelSelector={}".format(
            base_url, namespace, label)
        #r = requests.get(url, headers=headers, verify=False)
        # Make the request to the endpoint to retreive the Pods
        #response = r.json()
        response = api_return(url)
        # Extract the Pod name from the list
        pods = [p['metadata']['name'] for p in response['items']]
        # For each Pod, issue an HTTP DELETE request
        for p in pods:
            url = "{}/api/v1/namespaces/{}/pods/{}".format(
                base_url, namespace, p)
            r = requests.delete(url, headers=headers, verify=False)
            if r.status_code == 200:
                log.info("{} was deleted successfully".format(p))
            else:
                log.error("Could not delete {}".format(p))


# This function is used to extract the Pod labels from the configmonitor resource.
# It takes the configmap name as the argument and uses it to search for configmonitors
# that have the configmap name in its spec
def getPodLabels(configmap):
    url = "{}/apis/demo.com/v1/namespaces/{}/configmonitors".format(
        base_url, namespace)
    #r = requests.get(url,headers=headers, verify=False)
    # Issue the HTTP request to the appropriate endpoint
    #response = r.json()
    response = api_return(url)
    # Extract the podSelector part from each object in the response
    pod_labels_json = [i['spec']['podSelector']
                       for i in response['items'] if i['spec']['configmap'] == "flaskapp-config"]
    result = [list(l.keys())[0] + "=" + l[list(l.keys())[0]]
              for l in pod_labels_json]
    # The result is a list of labels
    return result

# This is the main function that watches the API for changes


def event_loop():
    log.info("Starting the service")
    url = '{}/api/v1/namespaces/{}/configmaps?watch=true"'.format(
        base_url, namespace)
    #r = requests.get(url, headers=headers, verify=False, stream=True)
    r = api_return(url)
    # We issue the request to the API endpoint and keep the conenction open
    for line in r.iter_lines():
        obj = json.loads(line)
        # We examine the type part of the object to see if it is MODIFIED
        event_type = obj['type']
        # and we extract the configmap name because we'll need it later
        configmap_name = obj["object"]["metadata"]["name"]
        if event_type == "MODIFIED":
            log.info("Modification detected")
            # If the type is MODIFIED then we extract the pod labels by using the getPodLabels function
            # passing the configmap name as a parameter
            labels = getPodLabels(configmap_name)
            # Once we have the labels, we can use them to find and kill the Pods by calling the
            # kill_pods function
            kill_pods(labels)

event_loop()

