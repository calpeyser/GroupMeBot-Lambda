import json
import logging
import os
from datetime import date

from google.oauth2 import service_account
import googleapiclient.discovery
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SPREADSHEET_ID = "<>"

def get_sheets_service():
	scopes = ['https://www.googleapis.com/auth/spreadsheets']
	service_account_file = '/var/task/key.json'
	credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
	sheets = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)
	return sheets.spreadsheets().values()

def parse_text(text):
	if text[:text.find(' ')] != 'QUOTE':
		return None
	return text[len('QUOTE '):].split("~")

def post_to_groupme(quote, author):
	data = {
		'bot_id': '<>',
		'text': "Gotcha bro.  Quote: %s, Author: %s" % (quote, author)
	}
	r = requests.post("https://api.groupme.com/v3/bots/post", data=data)

def lambda_handler(event, context):
	name = json.loads(event['body'])['name']
	text = json.loads(event['body'])['text']
	logger.info(name + " " + text)
	quote = parse_text(text)
	if quote:
		sheets_api = get_sheets_service()
		sheets_api.append(spreadsheetId=SPREADSHEET_ID, range="A:C", body={"range": "A:C", "values": [[str(date.today()), quote[0], quote[1]]]}, valueInputOption="USER_ENTERED").execute()	
		post_to_groupme(quote[0], quote[1])
	return {
		'statusCode': 200,
		'headers': { 'Content-Type': 'application/json' },
		'body': json.dumps({})
	}
