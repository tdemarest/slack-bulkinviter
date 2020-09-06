# slack-bulkinviter

Python script to bulk invite **all** users in a slack team to a specific channel.
While there are a number of ways to do this with small teams (see below), this
script uses the official Slack Python client and latest features for pagination
ensuring that one user to tens of thousands of users can easily be bulk
invited to a channel.

Updated to use the new Conversations API and the [official Python slackclient](
https://github.com/slackapi/python-slackclient) now that
[slacker](https://github.com/os/slacker) has been archived and no longer supported.

Basic usage:

* Python 3.x is required.
* Install the [python-slackclient](https://github.com/slackapi/python-slackclient)
library via `pip`
* :warning: Legacy Slack API tokens have been deprecated. Create a [Slack App](https://api.slack.com/apps)
for your workspace.
* Add an App OAuth token for the app you just create. More details on this can be
found at [Create and regenerate API tokens](https://get.slack.help/hc/en-us/articles/215770388-Creating-and-regenerating-API-tokens).
* Set the OAuth Scope using just the `User Token Scope`. These are the minimum
scope permisisons required for this script:

Permission | Description
-----------| -----------
channels:read | View basic information about public channels in the workspace
channels:write | Manage the user’s public channels and create new ones on the user’s behalf
groups:read | View basic information about the user’s private channels
users:read | View people in the workspace

* Install or reinstall the app once the OAuth scope has been defined or updated.
* :no_entry: Using a file for the token has been deprecated. Use the `--token`
option or set or pass the OAuth token as an environment variable to the script.
* Execute the script, passing the name of the channel where all users will be
invited, such as:

```shell
./slack-bulkinviter.py --token MyOAuthToken --channel mychannel
```

or by passing the OAuth token as an environemnt variable:

```shell
env SLACK_API_TOKEN=my-slack-app-oauth-token ./slack-bulkinviter.py --channel mychannel
```

* Sit back and let it do its work. Large workspaces can take a long time to process.
Using the `--verbose` option is recommended in workspaces with more than 1000
users or channels.

## Script Options

Option | Descriptions
------ | ------------
`--help` | Help on using the script.
`--channel` | The channel to add the user to. Required.
`--token` | The Slack OAuth Token (string) for the user app required for the workspace. Required if the `$SLACK_API_TOKEN` environment variable is not set.
`--tokenenv` | The environment variable name that contains the Slack OAuth API Token. default: SLACK_API_TOKEN
`--bots` | Include bot users in the channel. Excluded by default.
`--apps` | Include apps in the channel. Excluded by default.
`--sleep` | Number of seconds to sleep between pagination calls. Default is as low as is reasaonable. default: 2 seconds
`--split` | List split divisor used to chunk large lists into smaller chunks. This is required if the invite list exceeds 1000 users. If the invite list is greater than 10,0000 use `--split` to increase the divisor until `Users = Total Invited Users / Split` is less than 1000. Defaults to **10** which is good for up to 10,000 invites.
`--verbose` | Output more info about what is happening. Useful for workspaces with large number of conversations or users.

## Alternatives to this script

### UI: Channel Add Members

As of today using the UI option for a channel "add people to" `+` option allows
pasting over 2000 email addresses. This option either didn't exist or wouldn't
allow more than 100 people in the past. it may be likely that there is no limit
on this but it's been tested by me for just under 3000 email addresses.

### `/who` Cut and Paste

The `/who` command in a channel will return the first 99 users. For small
organizations this may be sufficient. Type `/who` in the most populated channel,
usually `#general` then copy the list of users and use as the input to `/invite`
in the channel you want to invite everyone.

### Channel Tools

Add [Channel Tools](https://www.channeltools.io/) to your workspace. Depends on the users
from one channel that is used as the basis for the invites for the target channel.

### Other

See [StackExchange](https://webapps.stackexchange.com/questions/100820/how-do-i-invite-all-team-members-to-a-new-slack-channel/123420#123420)
has some solutions as well. Make sure to read all of the comments.

## Run from Docker

Docker instructions courtesy of [@markshust](https://github.com/markshust)
(modified slightly to use the env variable for the OAuth token).

Create a new directory named "slack-bulkinviter", then once in that directory, copied the raw file there:

```shell
mkdir slack-bulkinviter && cd $_
curl -O https://raw.githubusercontent.com/robby-dermody/slack-bulkinviter/master/slack-bulkinviter.py
```

Create a file named `Dockerfile` with the following contents:

```text
FROM python:3.8.2-buster

RUN pip install --no-cache-dir slacker

COPY slack-bulkinviter.py .
```

Build the docker image with:

`docker build -t slack-bulkinviter .`

At this point you should be all set, and can run the script like so:

```shell
docker run --env SLACK_API_TOKEN=my-own-slack-oath-token -it --rm \
slack-bulkinviter python slack-bulkinviter.py --channel your-channel
```
