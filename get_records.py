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
      self.buyDict = {}
      self.sellDict = {}
      self.returnedJson = {}
      self.todayDate = datetime.today().strftime('%Y-%m-%d')
  def getdata(self):
    post = requests.post(self.url,self.password, verify=False).json()
    self.returnedJson = post[0]
    return self.returnedJson
  def seperateValues(self):
      for key , value in self.returnedJson.items():
        if '_buy' in key:
          self.buyDict[key[0:3]] = float(value)
        elif '_sell' in key:
          self.sellDict[key[0:3]] = float(value)
      return [self.sellDict,self.buyDict]
    
    



if __name__ == "__main__":
  #get the data from the website.
  todays_records = GetCurrencies()
  record_data=todays_records.getdata()

  #upload the data to firebase
  cred = credentials.Certificate("exchange-dinar-key.json")
  firebase_admin.initialize_app(cred)
  db = firestore.client()
  db.collection(u'exchange-daily').document(str(todays_records.todayDate)).set({"anis":todays_records.seperateValues()})
