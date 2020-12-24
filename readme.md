# SparkIEEE

## Installation

Make sure you have Python (v3.9.1 in this case) and pip installed. Run the following command to install [discord.py](https://github.com/Rapptz/discord.py):

`pip3 install discord.py --user`

To create the Discord bot account, use the Discord developer portal to generate a Bot account. Under the 'OAuth2' menu, give the account a 'bot' scope and 'Administrator' privileges, then use the generated URL to invite the bot to the server.

To deploy the bot locally, insert your Bot Token in `creds.py` and run `bot.py`:

`python3 bot.py`

Once the bot is connected to the server successfully, you will see the following message printed in your terminal:

`SparkIEEE is ready!`