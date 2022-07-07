import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import pytz


alger_timezone = pytz.timezone('Africa/Algiers')





class GetCurrencies():
  
  def __init__(self):
      self.password = {'afous': 'moh!12!'}
      self.url = 'http://www.forexalgerie.com/connect/updateExchange.php'
  
  def getdata(self):
    post = requests.post(self.url,self.password, verify=False).json()
    post_json = post[0]
    return post_json
  
  



if __name__ == "__main__":

  
  
  #get the data from the website.
  todays_records = GetCurrencies()
  record_data=todays_records.getdata()
  
  
  
  record_date = record_data['create_date_time']
  document_name = record_data['record_no']
  
  buy_price ={}
  sell_price ={}
  #seprate the buy and sell values to different dictionaries.
  for key , value in record_data.items():
    if '_buy' in key:
      buy_price[key[0:3]] = float(value)
    elif '_sell' in key:
      sell_price[key[0:3]] = float(value)
  #TODO : add time and date in the document.
  convert_toTimeOBj= datetime.strptime(record_date, '%d-%m-%Y %H:%M:%S')
  record_data.update({'create_date_time': convert_toTimeOBj})
  #TODO :convert the time to algerian time.
  today = datetime.today().strftime('%Y-%m-%d')

  #upload the data to firebase
  cred = credentials.Certificate("exchange-dinar-key.json")
  firebase_admin.initialize_app(cred)
  db = firestore.client()
  db.collection(u'exchange-daily').document(str(today)).collection(u'prices').document('sell').set(sell_price)
  db.collection(u'exchange-daily').document(str(today)).collection(u'prices').document('buy').set(buy_price)
