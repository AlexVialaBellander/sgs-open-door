import requests
import uuid
import json

from flask import Flask, request, render_template
from datetime import datetime, timedelta


app = Flask(__name__)

with open('keys.json', 'w+') as file:
    json.dump({}, file)
    
    
def fetch(key = None) -> None:
    with open('keys.json', 'r') as file:
        keys = json.load(file)
    if key:
        try:
            return True, keys[key]
        except KeyError as e:
            return False, f"Key {e} not found"
    else:
        return keys

def write(key, value) -> None:
    with open('keys.json', 'r+') as file:
        KEYS = json.load(file)
        try:
            with open('keys.json', 'w') as file:
                KEYS[key] = value
                json.dump(KEYS, file)
            return True
        except json.decoder.JSONDecodeError as e:
            return e
    

@app.route('/')
def index():
    key = '<dt class="yc-responsible">Ansvarig</dt>\n                <dd class="yc-responsible">'
    doc = requests.get('http://hemma.sgsstudentbostader.se/').text
    name_idx = int(doc.find(key) + len(key))
    name_idx_end = int(doc[name_idx:].find('</dd>'))
    name = doc[name_idx: name_idx + name_idx_end]
    return render_template('index.html', name=name)

@app.route('/admin')
def admin():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    return render_template('login.html', email=email)
  
@app.route('/generate')
@app.route('/generate/<int:duration>')
def generate(duration = 60):
    id = str(uuid.uuid4())
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delta = timedelta(minutes=duration)
    check = write(id, [now, delta.days, delta.seconds])
    if check:
        return str(id)
    else:
        return str(check)

@app.route('/keys')
def keys():
     return str(fetch())

@app.route('/open/<id>')
def validate(id):
    success, msg = fetch(id)
    if success:
        creation_timestamp = msg[0]
        delta_days = msg[1]
        delta_seconds = msg[2]
        # if creation timestamp + time delta is less than current timestamp
        if datetime.now() < datetime.strptime(creation_timestamp, "%Y-%m-%d %H:%M:%S") + timedelta(days=delta_days, seconds=delta_seconds):
            response = open_door()
            return response.text
        else:
            return "Key has expired"
    else:
        return str(msg)









doors = ['Viktor Rydbergsgatan', 'Richertsgatan']

def open_door():

  cookies = {
      'ASP.NET_SessionId': 'BAE6F59E14FE24520506FD82',
  }

  headers = {
      'Accept': '*/*',
      'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
      'Connection': 'keep-alive',
      'DNT': '1',
      'Origin': 'http://hemma.sgsstudentbostader.se',
      'Referer': 'http://hemma.sgsstudentbostader.se/DoorControl/Fullscreen',
      'X-Requested-With': 'XMLHttpRequest',
  }

  data = {
      'epName': 'Richertsgatan',
  }

  response = requests.post(
    'http://hemma.sgsstudentbostader.se/DoorControl/PerformUnlock', 
    cookies=cookies, 
    headers=headers, 
    data=data, 
    verify=False)
  return response
  
  