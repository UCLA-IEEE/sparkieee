import os

SPARKIEEE_TOKEN = os.environ["SPARKIEEE_TOKEN"]
LAB_CHANNEL_ID = 724325916154658867

PROJECTS = {
    "OPS": {
        "FULL_NAME": "Open Project Space",
        "LEADS": {"Miriam": "Mr.Jellybean#7816", "Eli": "bruhticulou5#2475"},
    },
    "MICROMOUSE": {
        "FULL_NAME": "Micromouse",
        "LEADS": {"Megan": "aloe vera plants#4770", "Nathan N": "Chiertare#1463"},
    },
    "DAV": {
        "FULL_NAME": "Digital Design, Architecture, and Verification / Digital Audio Visualizer",
        "LEADS": {"Tim": "TJ178#5214", "Siddhant": "Condolences#1271"},
    },
    "WRAP": {
        "FULL_NAME": "Wireless, RF, and Analog Project",
        "LEADS": {"Nathan P": "pakuwulo#6005", "Ramtin": "Ramtin#8911"},
    },
    "PR": {
        "FULL_NAME": "Pocket Racers",
        "LEADS": {"Prem": "8BitRobot#3625", "Cameron": "cfiske#8209"},
    },
    "WORKSHOPS": {
        "FULL_NAME": "Workshops",
        "LEADS": {"Jessica": "Jessica Chang#5476", "Caden": "cdvs#2870"},
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        "FB_GROUP": "https://www.facebook.com/groups/324536415200701",
    },
}

# Checkoff Spreadsheet consts
HEADER_ROWS = 3  # Project name, date, and completion %
PROJECT_COL_INDEX = 2  # Index of first col that contains projects
DATE_ROW_INDEX = 1  # Index of row that contains deadlines
PERCENT_ROW_INDEX = 2  # Index of row that contains percentages

# Lab Hour Spreadsheet consts
LAB_HOURS = "1t1_Idot1QyOnKLlXEGa0BijAa6OalRwYeZ3byehvQPY"
FIRST_LH_ROW_INDEX = 1
FIRST_LH_COL_INDEX = 0
LAB_HOURS_START_TIME = 10  # 10 AM
NUM_DAYS_IN_TABLE = 6

# Treasurer Deposit Sheet Constants
TREASURER_SHEET = "1Xvkvt62ZiDtIzMjjwH6mMLY5Icn5gADDfSEfnydIWRk"
PAY_DEPOSIT_COL = 2
RETURN_DEPOSIT_COL = 4
ASSIGNMENT_ROW = 3
TREASURER_PROJECT_COL_INDEX = 5

# Emojis
ROLE_CHANNEL_ID = 793585913916948482
PROJECT_MSG_ID = 1029264585313767444
PRONOUN_MSG_ID = 1030022950109323334
OUTREACH_MSG_ID = 1030011251939618816
AMP_MSG_ID = 1059270992867905567
OPS_EMOJI = 793582628665294891
MM_EMOJI = 793582770705661984
AIR_EMOJI = 793582813919051836
DAV_EMOJI = 793582847549243442
WRAP_EMOJI = 793583125270888469
PR_EMOJI = 1025682364413784115
OUTREACH_EMOJI = 1029296526423506974
