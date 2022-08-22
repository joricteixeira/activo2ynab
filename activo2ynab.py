import pandas
import requests
import sys
import re
import pprint
import json 

def parse_activo(file_name):
    df = pandas.read_excel(file_name)

    # extract card number
    card_number = re.search('\d+', df.columns[0]).group(0)

    # drop first 6 rows
    df.drop([0,1,2,3,4,5], inplace=True)

    # set columns
    df.columns = ['drop', 'date', 'payee_name', 'amount']
    df.drop(columns=['drop'], inplace=True) 
    df['account_id'] = config['card_map'][card_number]['account_id']
    df['memo'] = 'activo2ynab'

    df.set_index('date',inplace=True)
    df['date'] = df.index.strftime('%Y-%m-%d')

    # convert amount to YNAB 'milliunits'
    df['amount'] = df['amount']*1000

    # activo credit card shows inflow as negative an vice-versa
    # make inflow positive and outflow negative if it is a credit card 
    if config['card_map'][card_number]['credit_card']:
        df['amount'] = df['amount']*(-1)
    df['amount'] = df['amount'].astype(int)

    # prepping json body
    transactions = df.to_dict('records')

    # to prevent duplicate imports and to aid matching with existing transactions
    for t in transactions:
        t['import_id'] = f"ACTIVO2YNAB:{t['amount']}:{t['date']}:1"

    request_body = {'transactions': transactions}
    response = requests.post(f"https://api.youneedabudget.com/v1/budgets/{config['budget_id']}/transactions", headers={'Authorization': f"Bearer {config['api_token']}"}, json=request_body)

    print("Status Code", response.status_code)
    pprint("Response Content", response.content)


def get_config():
    with open('config.json', "r") as f:
        return json.load(f)

config = get_config()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Please provide the .xlsx file name")
    else:
        parse_activo(sys.argv[1], config)