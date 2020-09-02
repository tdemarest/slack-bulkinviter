# slack-bulkinviter

Super quick and dirty Python script to bulk invite ALL users in a slack team to a specific channel. We need to do this regulary with [Counterparty](http://www.counterparty.io) when we create a new channel that everyone should be in, or move things around. Now using the new Conversations API.

To use:
* Install the [slacker](https://github.com/os/slacker) library via `pip`
* [Get an API key](https://get.slack.help/hc/en-us/articles/215770388-Creating-and-regenerating-API-tokens)
* Optionally, if not using `--apikey`, create a file in the same directory as `slack-bulkinviter.py` containing your API key and pass the filename to the argument `--apikey` or `-k`
* Execute the script, passing the name of the channel where all users will be invited, such as `./slack-bulkinviter.py --channel mychannel --apikey myapistring`
* Sit back and let it do its work

## Run from Docker

Docker instructions courtesy of [@markshust](https://github.com/markshusthttps://github.com/markshust).

Create a new directory named "slack-bulkinviter", then once in that directory, copied the raw file there:

```shell
mkdir slack-bulkinviter && cd $_
curl -O https://raw.githubusercontent.com/robby-dermody/slack-bulkinviter/master/slack-bulkinviter.py
```

Place your `apikey.txt` file in this same directory with the contents of your API key.

Create a file named `Dockerfile` with the following contents:

```text
FROM python:3.8.2-buster

RUN pip install --no-cache-dir slacker

COPY slack-bulkinviter.py .
COPY apikey.txt .
```

Build the docker image with:

`docker build -t slack-bulkinviter .`

At this point you should be all set, and can run the script like so:

`docker run -it --rm slack-bulkinviter python slack-bulkinviter.py your-channel`

