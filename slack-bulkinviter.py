#! /usr/bin/env python3

import sys
import os
import logging
import time
import argparse
from slack import WebClient


# Initiate the parser
parser = argparse.ArgumentParser()

# add long and short argument
parser.add_argument("-c", "--channel", required=True, metavar="CHANNEL NAME", help="Channel name to add members. REQUIRED.")
parser.add_argument("-b", "--bots", action='store_true', help="Include bots in channel. default: not included.")
parser.add_argument("-a", "--apps", action='store_true', help="Include apps in channel. default: not included.")
parser.add_argument("--sleep", type=int, metavar="SECONDS", default=2, help="Adjust sleep time between pagination calls. default: 2 seconds")
parser.add_argument("-s", "--split", metavar="INT", type=int, default=10, help="Split invite list into less than 1000 users. If your invite list is greater than 10000 users adjust this to split into less than 1000 chunks (as a divisor). default: 10")
parser.add_argument("-v", "--verbose", action='store_true', help="Verbose output. Useful inworkspaces with large number of users or conversations.")

# Only allow one toargument. Not required as default SLACK_API_TOKEN variable can be set and neither is then required
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument("-k", "--token", metavar="TOKEN STRING", help="Slack App OAuth access token string. Required if environment variable SLACK_API_TOKEN or --tokenvar is not set.")
group.add_argument("--tokenenv", metavar="TOKEN ENV VAR", default="SLACK_API_TOKEN", help="Environment variable name that contains the Slack OAuth API Token. default: SLACK_API_TOKEN")

# read arguments from the command line
args = parser.parse_args()

if args.verbose:
    # Setup logging using f-string formatting
    # lmgging.basicConfig(stream=sys.stderr, level=logging.INFO, format="{processName:<12} {message} ({filename}:{lineno})", style="{")
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="{message} ({filename}:{lineno})", style="{")


def find_channel(response):
    """
    Iterate over the response channels list to determine if we
    matched our channel
    """

    channels = None
    channels = [d for d in response["channels"] if d['name'] == args.channel]
    # for d in response["channels"]:
    #   if d['name'] == args.channel:
    #       channels = [d]

    # if not len(channels):
    if not channels:
        logging.info(f'\U0001F5DE  Did not find channel {args.channel} on page {response["response_metadata"]["next_cursor"]}')
        return()

    assert len(channels) == 1

    print(f'\N{bottle with popping cork} Found {len(channels)} channel matching {args.channel} with name of {channels[0]["name"]} and channel ID {channels[0]["id"]}')
    channel_id = channels[0]['id']

    return channel_id


def should_invite(user):
    """
    Detemine if the current user needs to be invited
    """
    return ((not user['deleted'])
            and (not user['is_restricted'])
            and (not user['is_ultra_restricted'])
            and (args.bots or not user['is_bot'])
            and (args.apps or not user['is_app_user'])
            and (user['id'] != "USLACKBOT")
            )


def split_list(alist, wanted_parts=args.split):
    """
    Split a list into a number of "parts". This is used to make sure
    to split into less than 1000 items due to API limits. Default is a
    divisor of 10 which will split 10000 users into 10 lists of 1000.
    Can be set from --split|-s at runtime.
    """
    length = len(alist)
    return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
            for i in range(wanted_parts)]


# Get token from commandline or environment variable
if args.token:
    token = args.token
else:
    token = os.environ.get(args.tokenenv)

if args.verbose:
    logging.info(f'\U0001F30E  Verbose logging enabled {args.verbose}. Settings:')
    logging.info(f'  Token ENV Variable --tokenenv: {args.tokenenv}')
    logging.info(f'  Token String       --token:    {args.token}')
    logging.info(f'  Channel            --channel:  {args.channel}')
    logging.info(f'  Sleep secondsi     --sleep:    {args.sleep}')
    logging.info(f'  Spliti             --split:    {args.split}')
    logging.info(f'  Invite bots?       --bots:     {args.bots}')
    logging.info(f'  Invite apps?i      --apps:     {args.apps}')
    logging.info(f'  Token:                         {token}')

try:
    assert token
except AssertionError:
    print('\U0001F6D1  No OAuth Token passed via --token, envronment variable SLACK_API_TOKEN or --tokenenv')
    sys.exit(1)
else:
    client = WebClient(token)

count = 0

print(f'\N{stopwatch}  Starting search for channel named {args.channel}. This can take a while if the workspace has a lot of channels...')

# Get channel id from name
response = client.conversations_list(types="public_channel, private_channel", exclude_archived="true", limit=200)

# Use pagination to make sure all channels are checked using limits
while response["response_metadata"]['next_cursor']:
    count += 1
    next_page = response["response_metadata"]['next_cursor']
    logging.info(f'\U0001F5DE  Conversation list cursor count {count} at index {next_page} and returned {len(response["channels"])} channels')
    channel_id = find_channel(response)
    if channel_id:
        break
    else:
        time.sleep(args.sleep)
        response = client.conversations_list(types="public_channel, private_channel", exclude_archived="true", cursor=next_page, limit=200)

if not channel_id:

    print(f'\U0001F6D1  Channel {args.channel} was not found.')
    sys.exit(1)

print('\N{stopwatch}  Grabbing the complete list of all users. This can take a while in large organizations...')

# Get all of the users in the workspace which includes deleted and deactivated users
# The API doesn't have a way to exclude deleted or deactivated users at this time
count = 0
response = client.users_list(limit=200)

users_all = set(u['id'] for u in response['members'] if should_invite(u))

while response["response_metadata"]['next_cursor']:
    count += 1
    next_page = response["response_metadata"]['next_cursor']
    logging.info(f'\U0001F5DE  User list cursor is at count {count} and index {next_page} and returned {len(response["members"])} users')
    users_all |= set(u['id'] for u in response['members'] if should_invite(u))
    time.sleep(args.sleep)
    response = client.users_list(cursor=next_page, limit=200)

print(f'\N{chequered flag}  Number of total users (active, deleted & deactivated) is in workspace: {len(users_all)}')
print(f'\N{stopwatch}  Grabbing members already in {args.channel}...')

# Filter out people already in the channel
count = 0
response = client.conversations_members(channel=channel_id, limit=200)

users_already_in = set(response["members"])

while response["response_metadata"]['next_cursor']:
    count += 1
    next_page = response["response_metadata"]['next_cursor']
    logging.info(f'\U0001F5DE  Channel member user list cursor is at count {count} and index {next_page} and returned {len(response["members"])}')
    users_already_in |= set(response["members"])
    time.sleep(args.sleep)
    response = client.conversations_members(channel=channel_id, cursor=next_page, limit=200)

print(f'\N{chequered flag}  Number of users already in channel {args.channel} is: {len(users_already_in)}')

users_to_invite = users_all.difference(users_already_in)

print(f'\N{chequered flag}  Number of users to invite to channel {args.channel} is: {len(users_to_invite)}')

# Invite all users to slack channel
if users_to_invite:
    if len(users_to_invite) > 999:
        logging.info('\U0001F5DE  Number of users is > 999 - chunking invites')
        users_to_invite = split_list(list(users_to_invite), args.split)
    else:
        user_invite_chunk = users_to_invite
    try:
        count = 1
        for user_invite_chunk in users_to_invite:
            logging.info(f'\U0001F5DE  Length of invite chunk #{count}: {len(user_invite_chunk)}')
            print(f'\U0001F39F  Inviting {len(user_invite_chunk)} users in chunk #{count} to channel {args.channel}...')
            client.conversations_invite(channel=channel_id, users=user_invite_chunk)
            time.sleep(args.sleep)
            count += 1
    except Error as e:
        print("Error: " + e.args[0])
else:
    print("\N{chequered flag}  All users are already in the channel - nothing to do.")

print("\N{chequered flag}  Done!")
