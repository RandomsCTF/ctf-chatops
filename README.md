# Slack /slash Integrations

Custom integrations created and used by RandomsCTFTeam for use during CTF challenges and other fun activities.

Each integration exists in it's own subdirectory and must be run individually. You *can* however run them all simultaneously, if you so choose.

Be sure to check the README for each integration as they all have different 'quirks' to them.

Each /slash integration will need a corresponding /slash configuration within Slack as well as a PUSH notification method for sending results back to Slack. While the /slash command natively prints the `return` to the initiating user, the method used by these integrations is to dump the command result into specified channel for all to see.

You'll need to obtain /slash integration specifics such as token and PUSH URL and put them in the `config.py` of each integration directory.

## Contributing

Contributions are welcome and encouraged. We've had very little time for testing and optimizing these, even from a security standpoint. That is half the reason we're open-sourcing it, to allow others to use and improve upon it.

## License

GPLv3 (See `LICENSE` for more info)

## Author

Eric Capuano (r4z0rb4ck) of RandomsCTFTeam

## Setup
```
git clone https://github.com/RandomsCTF/ctf-chatops.git
virtualenv ctf-chatops
pushd ctf-chatops
source Scripts/Activate
Scripts/pip install -r requirements.txt
```

## Note

Some of the code in this project has been adapted from the following:

- [jpmens.net](http://jpmens.net/2015/05/02/where-are-your-slack-team-members-at-the-moment/)
