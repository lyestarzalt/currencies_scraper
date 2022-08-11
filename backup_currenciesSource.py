import pandas as pd
import requests

anis = requests.get(
    'https://www.devise-dz.com/square-port-said-alger/').content
df_list = pd.read_html(anis)

euro_usd = df_list[0]
rest_currencies = df_list[1]
rest_currencies.rename(
    columns={0: 'Devises', 1: 'Achat', 2: 'Vente'}, inplace=True)
euro_usd.set_index('Devises')
rest_currencies.set_index('Devises')
merged_currencies = pd.concat([rest_currencies, euro_usd])

merged_currencies['Achat'] = merged_currencies['Achat'].str.replace(',', '.')
merged_currencies['Achat'] = merged_currencies['Achat'].str.strip(' DA')
merged_currencies['Vente'] = merged_currencies['Vente'].str.replace(',', '.')
merged_currencies['Vente'] = merged_currencies['Vente'].str.strip(' DA')


anis = merged_currencies['Devises'].to_list()

devise = []
for i in anis:
    result = i[i.find('(')+1:i.find(')')]
    if result == '€':
        result = result.replace('€', 'EUR')
    if result == '$':
        result = result.replace('$', 'USD')
    if result == '£':
        result = result.replace('£', 'GBP')
    if result == 'EAD':
        result = result.replace('EAD', 'aed')
    devise.append(result.lower())

merged_currencies['Vente'] = pd.to_numeric(merged_currencies['Vente'])
merged_currencies['Achat'] = pd.to_numeric(merged_currencies['Achat'])

""" Vente = 0 """

merged_currencies['Devises'] = devise
merged_currencies.set_index('Devises', inplace=True)
merged_currencies.rename(
    columns={'Achat': 1, 'Vente': 0}, inplace=True)
""" jsonformat = merged_currencies.to_json()
print(jsonformat)
 """
dictt = merged_currencies.to_dict()
finallist = [dictt[0], dictt[1]]
