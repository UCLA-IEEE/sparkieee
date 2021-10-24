import os

SPARKIEEE_TOKEN = os.getenv("SPARKIEEE_TOKEN")
LAB_CHANNEL_ID = 724325916154658867

PROJECTS = {
    'OPS': {
        'FULL_NAME': 'Open Project Space',
        'LEADS': {
            'Margot': 'mango#8254',
            'Preston': 'Preston#9607'
        },
        'SPREAD_ID': '1jEGSNFQPU8Wd_uUgfmHmXq8J9UD_Wc3Jn1aSGi3hqlk',
        'TREASURER_IND': 0
    },

    'MICROMOUSE': {
        'FULL_NAME': 'Micromouse',
        'LEADS': {
            'Tim J': 'TJ178#5214',
            'Dominic': 'dombonist#7938'
        },
        'SPREAD_ID': '14UHo1kvLdw1lgMTEvchIT6Lr2rPbaq1NFbwIhnBylfg',
        'TREASURER_IND': 1  
    },

    'AIRCOPTER': {
        'FULL_NAME': 'Aircopter',
        'LEADS': {
            'Alexis': 'Czerny Voron#9175',
            'Tim Z': 'timz#1019'
        },
        'SPREAD_ID': '1vFptmlPk-wnsytaCsTLGPkzSZ59MNYpWy7r7OSMRBGY',
        'TREASURER_IND': 2
    },

    'DAV': {
        'FULL_NAME': 'Digital Audio Visualizer',
        'LEADS': {
            'Andrew': 'stewe951#1615',
            'Achinthya': 'Achinthya#7343'
        },
        'SPREAD_ID': '1DVziROAKMz0fOuruWET839MWcHhAMzpf4PxwqTZNPnY',
        'TREASURER_IND': 3
    },

    'WRAP': {
        'FULL_NAME': 'Wireless, RF, and Analog Project',
        'LEADS': {
            'Tyler': 'tyler.4p#7755',
            'Vaibhav': 'Vaibhav Gupta#2284'
        },
        'SPREAD_ID': '1ao3AKzt0XpwfX0JXiM2vHZ8e0OfR45WhDdpY_dYoqOE',
        'TREASURER_IND': 4
    },

    'WORKSHOPS': {
        'FULL_NAME': 'Workshops',
        'LEADS': {
            'David': 'uh oh its david#7756',
            'Siddhant': 'Condolences#1271'
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

# Treasurer Deposit Sheet Constants
TREASURER_SHEET = '1Xvkvt62ZiDtIzMjjwH6mMLY5Icn5gADDfSEfnydIWRk'
PAY_DEPOSIT_COL = 2
RETURN_DEPOSIT_COL = 4
ASSIGNMENT_ROW = 2
TREASURER_PROJECT_COL_INDEX = 5

# Emojis
ROLE_CHANNEL_ID = 793585913916948482
REACT_MSG_ID = 793608149742780427
PRONOUN_MSG_ID = 887915744296329266
OPS_EMOJI = 793582628665294891
MM_EMOJI = 793582770705661984
AIR_EMOJI = 793582813919051836
DAV_EMOJI = 793582847549243442
WRAP_EMOJI = 793583125270888469
