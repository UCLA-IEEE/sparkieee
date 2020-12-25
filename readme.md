# SparkIEEE

## Installation

Make sure you have Python (v3.9.1 in this case) and pip installed. Run the following command to install [discord.py](https://github.com/Rapptz/discord.py):

`pip3 install discord.py --user`

Run the following command to install the Google Client library:

`pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

Follow the directions under Step 1 in the Google Sheets API Python Quickstart Guide [here](https://developers.google.com/sheets/api/quickstart/python) to generate a `credentials.json` file. Drag it into the root directory.

To generate a pickle file that allows the bot access to your account to read/write to Google Sheets, run the `bot.py` script. 

`python3 bot.py`

To generate a new one, just delete the existing `token.pickle` file and rerun the script. It will prompt you to login to your Google account and give the corresponding permissions.

To create the Discord bot account, use the Discord developer portal to generate a Bot account. Under the 'OAuth2' menu, give the account a 'bot' scope and 'Administrator' privileges, then use the generated URL to invite the bot to the server.

## Testing 

To deploy the bot locally, insert your Bot Token in `creds.py` and run `bot.py`:

`python3 bot.py`

Once the bot is connected to the server successfully, you will see the following message printed in your terminal:

`SparkIEEE has logged in as [Bot Name]`