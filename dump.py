#!/usr/bin/python
import urllib.request
import json

GROUPME_API = "https://api.groupme.com/v3"

def main():
    user_token = input()

    # Get first 100 messages, print them, save id of the oldest message
    messages = get_starting_messages(user_token)
    for message in messages:
        print_message(message)
    before_id = messages[len(messages) - 1]["id"]

    # Loop through history, printing messages.
    while(True):
        messages = get_messages_before(user_token, before_id)
        for message in messages:
            print_message(message)
        before_id = messages[len(messages) - 1]["id"]


# Takes a json message object, prints it.
def print_message(message):
    if(message["text"] is None):
        # probably was an attachment, ie picture
        print("\n" + message["name"] + " posted a picture:\n"
                + message["attachments"][0]["url"])
    else:
        print("\n" + message["name"] + ":\n" + message["text"])


# Returns the 100 messages in a chat that come before the given id.
def get_messages_before(user_token, before_id):
    response = make_request(GROUPME_API, "/groups/16492586/messages",
            user_token, {'limit':'100', 'before_id':before_id})

    return response["messages"]

# Returns the first 100 messages in a chat
def get_starting_messages(user_token):
    response = make_request(GROUPME_API, "/groups/16492586/messages",
            user_token, {'limit':'100'})

    return response["messages"]


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


main()
