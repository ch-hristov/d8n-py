import requests

url = "https://engisense.com/api/analysis"

payload={}
files=[
  ('file',('0.jpg',open("./large.jpg",'rb'),'image/jpeg'))
]
headers = {
  'API-KEY': 'MY-API-KEY'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)