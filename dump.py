#!/usr/bin/python
import urllib.request
import json

# fetches resource at URL, converts JSON response to useful Object
def make_request(base_url, additional_url, token, params):

    # Hit url, get raw response
    url = base_url + additional_url + "?token=" + token

    for param, value in params.items():
        url += "&" + param + "=" + value

    response = urllib.request.urlopen(url)

    # Convert raw response to usable JSON object
    response_as_string = response.read().decode('utf-8')
    obj = json.loads(response_as_string)
    return obj["response"]


GROUPME_API = "https://api.groupme.com/v3"
user_token = input()

response = make_request(GROUPME_API, "/groups/16492586/messages", user_token, {'limit': '100'})
messages = response["messages"]

for message in messages:
    if(message["text"] is None):
        # probably was an attachment, ie picture
        print("\n" + message["name"] +  " posted a picture:\n" + message["attachments"][0]["url"])
    else:
        print("\n" + message["name"] + ":\n" + message["text"])

before_id = messages[len(messages) - 1]["id"]

while(True):

    response = make_request(GROUPME_API, "/groups/16492586/messages", user_token, {'limit':'100', 'before_id':before_id})

    messages = response["messages"]


    for message in messages:
        if(message["text"] is None):
            # probably was an attachment, ie picture
            print("\n" + message["name"] + " posted a picture:\n" + message["attachments"][0]["url"])
        else:
            print("\n" + message["name"] + ":\n" + message["text"])

    before_id = messages[len(messages) - 1]["id"]
