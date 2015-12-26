#!/usr/bin/python
import urllib.request
import datetime
import json

GROUPME_API = "https://api.groupme.com/v3"

def main():
    user_token = input("Please enter your GroupMe API Token: ")

    # Select group
    group = select_group(user_token)
    group_id = group["group_id"]

    # Get first 100 messages, print them, save id of the oldest message
    messages = get_starting_messages(user_token, group_id)
    for message in messages:
        print_message(message)
    before_id = messages[len(messages) - 1]["id"]

    # Loop through history, printing messages.
    while(True):
        messages = get_messages_before(user_token, group_id, before_id)
        for message in messages:
            print_message(message)
        before_id = messages[len(messages) - 1]["id"]


# Takes a json message object, prints it.
def print_message(message):
    date = str(datetime.datetime.fromtimestamp(int(message["created_at"])))
    if(message["text"] is None):
        # probably was an attachment, ie picture
        print("\n" + date + " - " + message["name"] + " posted a picture:\n"
                + message["attachments"][0]["url"])
    else:
        print("\n" + date + " - " + message["name"] + ":\n" + message["text"])


# Returns the 100 messages in a chat that come before the given id.
def get_messages_before(user_token, group_id, before_id):
    response = make_request(GROUPME_API, "/groups/" + group_id + "/messages",
            user_token, {'limit':'100', 'before_id':before_id})

    return response["messages"]


# Returns the first 100 messages in a chat
def get_starting_messages(user_token, group_id):
    response = make_request(GROUPME_API, "/groups/" + group_id + "/messages",
            user_token, {'limit':'100'})

    return response["messages"]


# lists user's groups, asks for user to select a specific group, returns it.
def select_group(user_token):
    # Get list of groups
    groups = make_request(GROUPME_API, "/groups", user_token, {})
    names = [group["name"] for group in groups]

    # print groups for user to select
    for i in range(len(names)):
        print("[" + str(i) + "] " + names[i])
    selected_index = int(
		input("Please enter the number of your selected group: "))

    # return selected group
    return groups[selected_index]


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
