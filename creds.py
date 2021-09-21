import os

SPARKIEEE_TOKEN = os.getenv("SPARKIEEE_TOKEN")
LAB_CHANNEL_ID = 724325916154658867

PROJECTS = {
    'OPS': {
        'FULL_NAME': 'Open Project Space',
        'LEADS': {
            'Margot Nguyen': 'mango#8254',
            'Preston Rooker': 'Preston#9607'
        },
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        'FB_GROUP': 'https://www.facebook.com/groups/ieeeops',
        'SPREAD_ID': '1fmcb5f__16A4G9rROlBHqBV-ceITsuybxnP33OaMWs8'
    },

    'MICROMOUSE': {
        'FULL_NAME': 'Micromouse',
        'LEADS': {
            'Tim Jacques': 'TJ178#5214',
            'Dominic Olson': 'dombonist#7938'
        },
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        'FB_GROUP': 'https://www.facebook.com/groups/910014872738486',
        'SPREAD_ID': '1keqQdjEdb9efmIOeeiWlTcpvCrLCxQy3B5O6uwUy1os'
    },

    'AIRCOPTER': {
        'FULL_NAME': 'Aircopter',
        'LEADS': {
            'Alexis Samoylov': 'Czerny Voron#9175',
            'Tim Zou': 'timz#1019'
        },
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        'FB_GROUP': 'https://www.facebook.com/groups/aircopter',
        'SPREAD_ID': '1eSxjNyX9znHYA2qRW5Oxiwf9v6Wck5YHYZmYRU_WjaE'
    },

    'DAV': {
        'FULL_NAME': 'Digital Audio Visualizer',
        'LEADS': {
            'Andrew Fantino': 'stewe951#1615',
            'Achinthya Poduval': 'Achinthya#7343'
        },
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        'FB_GROUP': 'https://www.facebook.com/groups/673094760079791',
        'SPREAD_ID': '1hdYvslAb1XKKFe767ztQMwTqxGLdmYhpwUtmbyVRA0s'
    },

    'WRAP': {
        'FULL_NAME': 'Wireless, RF, and Analog Project',
        'LEADS': {
            'Tyler Price': 'tyler.4p#7755',
            'Vaibhav Gupta': 'Vaibhav Gupta#2284'
        },
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        'FB_GROUP': 'https://www.facebook.com/groups/2609332906044188'
    },

    'WORKSHOPS': {
        'FULL_NAME': 'Workshops',
        'LEADS': {
            'David Kao': 'uh oh its david#7756',
            'Siddhant Gupta': 'Condolences#1271'
        },
        # TODO: Change with updated spreadsheets and facebook groups when they're established
        'FB_GROUP': 'https://www.facebook.com/groups/324536415200701'
    }
}

# Checkoff Spreadsheet consts
HEADER_ROWS = 3 # Project name, date, and completion %
PROJECT_COL_INDEX = 2 # Index of first col that contains projects
DATE_ROW_INDEX = 1 # Index of row that contains deadlines
PERCENT_ROW_INDEX = 2 # Index of row that contains percentages

# Lab Hour Spreadsheet consts
LAB_HOURS = '10TJAaKd2Dxtj7gU-SNE3uGYzNLZg-CuZbLXLcrNQhug'
FIRST_LH_ROW_INDEX = 1
FIRST_LH_COL_INDEX = 0
LAB_HOURS_START_TIME = 10 # 10 AM
NUM_DAYS_IN_TABLE = 6

# Emojis
ROLE_CHANNEL_ID = 793585913916948482
REACT_MSG_ID = 793608149742780427
PRONOUN_MSG_ID = 887915744296329266
OPS_EMOJI = 793582628665294891
MM_EMOJI = 793582770705661984
AIR_EMOJI = 793582813919051836
DAV_EMOJI = 793582847549243442
WRAP_EMOJI = 793583125270888469
