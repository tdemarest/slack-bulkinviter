#! /usr/bin/env python3
import sys
import argparse
import time
from slacker import Slacker, Error

# Initiate the parser
parser = argparse.ArgumentParser()

# add long and short argument
parser.add_argument("-c", "--channel", required=True, metavar="<Channel Name>", help="Set channel name to add members")
parser.add_argument("-k", "--apikey", metavar="'API Key Text String'", help="API Key string")
parser.add_argument("-f", "--apifile", metavar="<filename>", help="Path to API Key file - only required is not using --apikey|-k")
parser.add_argument("-b", "--bots", action='store_true', help="Include bots in channel")
parser.add_argument("-a", "--apps", action='store_true', help="Include apps in channel")

# read arguments from the command line
args = parser.parse_args()
if args.apikey is None and args.apifile is None:
    parser.error("You must pass an API Text String using --apikey or path to an API Key File using --apifile")

if args.apikey:
    slack = Slacker(args.apikey)
else:
    # Load API key from apikey.txt
    try:
        with open(args.apifile) as f:
            api_key = f.read().strip()
            assert api_key
    except IOError:
        print("Cannot find API Key file {}, or other reading error".format(args.apifile))
        sys.exit(1)
    except AssertionError:
        print("Empty API key")
        sys.exit(1)
    else:
        slack = Slacker(api_key)

# Get channel id from name
response = slack.conversations.list()
channels = [d for d in response.body['channels'] if d['name'] == args.channel]
if not len(channels):
    print("Cannot find channel")
    sys.exit(1)
assert len(channels) == 1
channel_id = channels[0]['id']

# Get users list
response = slack.users.list()

def should_invite(user):
    return ((not user['deleted'])
        and (not user['is_restricted'])
        and (not user['is_ultra_restricted'])
        and (args.bots or not user['is_bot'])
        and (args.apps or not user['is_app_user'])
        and (user['id'] != "USLACKBOT")
    )
users_all = set(u['id'] for u in response.body['members'] if should_invite(u))

# Filter out people already in the channel
response = slack.conversations.members(channel=channel_id, limit=1000)
users_already_in = set(response.body['members'])

users_to_invite = users_all.difference(users_already_in)

# Invite all users to slack channel
if users_to_invite:
    print("Inviting {} users to {}".format(len(users_to_invite), args.channel))
    try:
        slack.conversations.invite(channel_id, users=list(users_to_invite))
        print("Done")
    except Error as e:
        print("Error: " + e.args[0])
else:
    print("All users are already in the channel")
