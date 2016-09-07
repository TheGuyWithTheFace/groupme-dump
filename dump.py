#!/usr/bin/python
import urllib.request
import datetime
import json
import os
import time

GROUPME_API = "https://api.groupme.com/v3"
output_file_name = ""
output_file = 0 # just declaring here so it can be used later
image_count = 0
message_count = 0

def main():
    global output_file
    global output_file_name
    global dump_type

    user_token = input("Please enter your GroupMe API Token: ")

    # Choose whether dumping direct messages or group chats.
    dump_type = input("Enter \"dm\" to dump a direct message log or \"group\" to dump a group chat: ")
    
    # if something other than "dm" or "group" is typed, asks again
    while(dump_type != "dm") and (dump_type != "group"):
        dump_type = input("Invalid entry. Please choose \"dm\" or \"group\".: ")
    if(dump_type == "dm"):
        # Select which dm to dump
        group = select_dm(user_token)
        group_id = str(group["other_user"]["id"])
    elif(dump_type == "group"):
        # Select group
        group = select_group(user_token)
        group_id = group["group_id"]

    output_file_name = input("Please enter an unused name for the output file: ")

    # trim name if necessary
    if(output_file_name.endswith(".txt")):
        output_file_name = output_file_name[:-4]

    # setup output folder and file
    os.makedirs(output_file_name + "-pictures") # where we'll put attachments
    # specified what encoding to use so Windows users can use it
    output_file = open(output_file_name + ".txt", "w", -1, "utf-8")

    print("dumping...")
    start_time = time.time()

    # Get first set of messages, print them, save id of the oldest message
    messages = get_starting_messages(user_token, group_id)
    for message in messages:
        print_message(message)
    before_id = messages[len(messages) - 1]["id"]

    try:
        # Loop through history, printing messages.
        while(True):
            messages = get_messages_before(user_token, group_id, before_id)
            for message in messages:
                print_message(message)
            before_id = messages[len(messages) - 1]["id"]
    except urllib.error.HTTPError:
        elapsed = time.time() - start_time
        print("Downloaded " + str(message_count) + " messages and " +
                str(image_count) + " images in "
                + str(elapsed) + " seconds")


# Takes a json message object, prints it.
def print_message(message):
    global message_count
    global image_count

    date = str(datetime.datetime.fromtimestamp(int(message["created_at"])))
    if(message["text"] is None):
        # probably was an attachment, ie picture
        output_file.write("\n" + date + " - " + message["name"] + " posted a picture:\n"
                + message["attachments"][0]["url"])
    else:
        output_file.write("\n" + date + " - " + message["name"] + ":\n" + message["text"])
        message_count += 1

    # Save any attached pictures
    if(message["attachments"] is not None):
        for attachment in message["attachments"]:
            if(attachment["type"] == "image"):
                url = attachment["url"]
                # Sometimes an image isn't avaliable for some reason
                try:
                    response = urllib.request.urlopen(url)
                    image_count += 1
                except urllib.error.HTTPError:
                    print("ERROR: image at " + url + " could not be retrieved")
                    break
                # we shouldn't just *assume* it's a .png, but oh well
                f = open(output_file_name + "-pictures/" + date + ".png", "wb")
                f.write(response.read())
                f.close()


# Returns the 100 messages in a chat that come before the given id if dumping group
# Returns only 20 messages if dumping DMs
def get_messages_before(user_token, group_id, before_id):
    if (dump_type == "group"):
        response = make_request(GROUPME_API, "/groups/" + group_id + "/messages",
            user_token, {'limit':'100', 'before_id':before_id})
    
        return response["messages"]
    
    else:
        response = make_request(GROUPME_API, "/direct_messages",
            user_token, {'other_user_id':group_id, 'before_id':before_id})

        return response["direct_messages"]


# Returns the first 100 messages in a chat if group
# Returns first 20 for DMs
def get_starting_messages(user_token, group_id):
    if (dump_type == "group"):
        response = make_request(GROUPME_API, "/groups/" + group_id + "/messages",
            user_token, {'limit':'100'})

        return response["messages"]

    else:
        response = make_request(GROUPME_API, "/direct_messages",
            user_token, {'other_user_id':group_id})

        return response["direct_messages"]


# lists user's groups, asks for user to select a specific group, returns it.
def select_group(user_token):
    # Get list of groups
    groups = make_request(GROUPME_API, "/groups", user_token, {'per_page' : '100'})
    names = [group["name"] for group in groups]

    # print groups for user to select
    for i in range(len(names)):
        print("[" + str(i) + "] " + names[i])
    selected_index = int(
        input("Please enter the number of your selected group: "))

    # absolutely useless to the user and probably confusing to boot,
    #but it's useful to me. fuck the users.
    print("GroupId: " + groups[selected_index]["id"])

    # return selected group
    return groups[selected_index]

# lists user's chats, asks for user to select a specific person, returns it.
def select_dm(user_token):
    # Get list of DMs
    groups = make_request(GROUPME_API, "/chats", user_token, {'per_page' : '20'})
    names = [group["other_user"]["name"] for group in groups]

    # print names for user to select
    for i in range(len(names)):
        print("[" + str(i) + "] " + str(names[i]))
    selected_index = int(
        input("Please enter the number of the person whose DMs you'd like to copy: "))

    # return selected person's DMs
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
