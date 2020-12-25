from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build

# Project name, date, and completion %
HEADER_ROWS = 3

class SheetTransformer:
    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            raise Exception('The token.pickle file either does not exist or is not valid.'
                            'Please generate a new one using generate_pickle.py.')

        self.service = build('sheets', 'v4', credentials=creds).spreadsheets()
        print('Sheet Transformer built successfully using token.pickle')

    # try-except HttpError in next layer
    # todo: add lookup for specific users
    # todo: add lookback period parameter
    def lookup(self, spread_id, sheet_index=0, name=None):

        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        n_rows = sheet.get('properties').get('gridProperties').get('rowCount') if name else HEADER_ROWS
        n_cols = sheet.get('properties').get('gridProperties').get('columnCount')
        title = sheet.get('properties').get('title')
        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A1:{self.column_to_letter(n_cols)}{n_rows}').execute()
        values = result.get('values', [])
        if not values:
            raise Exception('Error, no values found.')

        summary = ''
        for i, project in enumerate(values[0]):
            if project == '':
                continue
            summary = summary + f'{project} (due {values[1][i]})\n'
        return summary

    # helper function to convert numerical column to letter column (Google Sheets format)
    def column_to_letter(self, column):
        temp = 0
        letter = ''
        while column > 0:
            temp = (column - 1) % 26
            letter = chr(int(temp) + 65) + letter
            column = (column - temp - 1) / 26
        return letter