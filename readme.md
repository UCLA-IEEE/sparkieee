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

## Project Lead Setup

To comply with the bot's checkoff commands, your spreadsheet should have the following:
* A1:B3 can be blank, or contain whatever you want. It will not be read.
* Starting from the 4th row, the first two columns will contain the roster. Column A will contain the names and Column B will contain their emails.
* The first row, starting at C1, should contain the names of assignments
* The second row, starting at C2, should contain the deadline of the assignment in the cell directly above it
* The third row, starting at C3, will contain an equation that gives a percentage of members who have completed the assignment
* The bot will read from the first (leftmost) sheet by default, so make that the most up-to-date version.
* The bot will strip leading/trailing whitespaces, so don't worry too much about that!

#### Example Use Case ###
1. Create a new Google Sheets. Use the first (leftmost) sheet.
2. Add the roster (name/email) into the first two columns starting at cell A4. A1:B3 are left blank.
3. Ask the bot owner to add the spreadsheet id to the project dictionary in `creds.py`
4. Once the bot is deployed, we can run commands.
5. Run `.addassign OPS "Project 1" "10/21/2020` to add the new project.
6. Run `.checkoff OPS "Project 1" "Kathy Daniels"` to check Kathy off.
7. Run `.checkoff OPS "Project 1" "Lucas Wolter" "completed checkpoint 1"` to write a note for Lucas in the checkoff square instead.
8. Run `.status OPS "Jay Park"` to get a summary of the Jay's projects completion (or incompletion) status so far.
9. Run `.extend OPS "Project 1" "11/4/2020"` when you realize it's 1 day before the deadline and only 20% of members have completed the project.

## Acknowledgments

Special thanks to the following contributors:

* [Raj Piskala](https://github.com/RogueArt)