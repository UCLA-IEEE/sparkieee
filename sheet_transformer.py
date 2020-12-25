from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build

class SheetTransformer:
    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            raise Exception('The token.pickle file either does not exist or is not valid.'
                            'Please generate a new one using generate_pickle.py'.)

        self.service = build('sheets', 'v4', credentials=creds)
        print('Sheet Transformer built successfully using token.pickle')

