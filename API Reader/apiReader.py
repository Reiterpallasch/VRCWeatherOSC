import requests

APIKEY = '50cabeab33746df4aef02f0a7ffb1778'
zip ='38017'
cCode = 'US'

#Testing Responses
response = requests.get("https://api.openweathermap.org/data/2.5/weather?zip="+zip+","+cCode+"&appid="+APIKEY+"&units=imperial")
print(response.json())
respJson = response.json()
tempurature = respJson['weather']
print(tempurature[0]['description'])
sky = tempurature[0]['description']
last4 = sky[len(sky)-4:len(sky)]
print(last4)