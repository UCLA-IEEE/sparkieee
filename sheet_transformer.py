from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle. https://developers.google.com/sheets/api/guides/authorizing
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Project name, date, and completion %
HEADER_ROWS = 3

class SheetTransformer:
    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds).spreadsheets()
        print('Sheet Transformer built successfully using token.pickle')

    # todo: add lookback period parameter
    def lookup(self, spread_id, name=None, sheet_index=0):
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

        member_row = None
        if name:
            for r in values:
                if r[0].upper().strip() == name.upper().strip():
                    member_row = r
                    break
            if member_row == None:
                raise Exception(f'Error, project member {name} not found.')

        summary = ''
        for i, project in enumerate(values[0]):
            if project == '':
                continue
            member_status = ''
            if member_row:
                member_status = ': ❌' if i >= len(member_row) or member_row[i] == '' else f': {member_row[i].strip()}'
                if member_status == ': x':
                    member_status = ': ✅'

            summary = summary + f'{project} (due {values[1][i]}){member_status}\n'
        return summary

    def checkoff(self, spread_id, assignment, name, val='y', sheet_index=0):
        spread_info = self.service.get(spreadsheetId=spread_id).execute()
        sheet = spread_info.get('sheets')[sheet_index]
        n_rows = sheet.get('properties').get('gridProperties').get('rowCount')
        n_cols = sheet.get('properties').get('gridProperties').get('columnCount')
        title = sheet.get('properties').get('title')
        result = self.service.values().get(spreadsheetId=spread_id,
                                           range=f'{title}!A1:{self.column_to_letter(n_cols)}{n_rows}').execute()
        values = result.get('values', [])
        if not values:
            raise Exception('Error, no values found.')

        old_val = ''
        member_row = None
        for row, r in enumerate(values):
            if r[0].upper().strip() == name.upper().strip():
                member_row = row + 1
        if member_row == None:
            raise Exception(f'Error, project member **{name}** not found.')

        assignment_col = None
        for col, a in enumerate(values[0]):
            if a.upper().strip() == assignment.upper().strip():
                if col < len(values[member_row]):
                    old_val = values[member_row - 1][col]
                assignment_col = self.column_to_letter(col + 1)
                break
        if assignment_col == None:
            raise Exception(f'Error, assignment **{assignment}** not found.')

        res = self.service.values().update(spreadsheetId=spread_id,
                                     valueInputOption='RAW',
                                     range=f'{title}!{assignment_col}{member_row}:{assignment_col}{member_row}',
                                     body={
                                         'range': f'{title}!{assignment_col}{member_row}:{assignment_col}{member_row}',
                                         'values': [[val]],
                                     }).execute()

        return old_val


    # helper function to convert numerical column to letter column (Google Sheets format)
    def column_to_letter(self, column):
        temp = 0
        letter = ''
        while column > 0:
            temp = (column - 1) % 26
            letter = chr(int(temp) + 65) + letter
            column = (column - temp - 1) / 26
        return letter