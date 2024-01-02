import http.client
import mimetypes
from codecs import encode
import requests
import json

class d8nClient:
    def __init__(self, api_key):
        self.API_key = api_key

    def from_local_file(self, path, project_id = None):
        conn = http.client.HTTPSConnection("d8n.host")
        dataList = []

        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'
        dataList.append(encode('--' + boundary))
        dataList.append(encode('Content-Disposition: form-data; name=file; filename={0}'.format(path)))

        fileType = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        dataList.append(encode('Content-Type: {}'.format(fileType)))
        dataList.append(encode(''))
    
        with open(path, 'rb') as f:
            dataList.append(f.read())

        dataList.append(encode('--'+boundary+'--'))
        dataList.append(encode(''))
        body = b'\r\n'.join(dataList)
        payload = body
        headers = {
            'API-KEY': self.API_key,
            'Content-type': 'multipart/form-data; boundary={}'.format(boundary),
        }
        
        if project_id is not None:
            headers['projectId']=project_id
            
        conn.request("POST", "/api/analysis", payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = (data.decode("utf-8"))
        return json.loads(data)

    def fetch_status(self, id):
        url = "https://d8n.host/api/get_status?id={0}".format(id)

        payload={}
        files={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload, files=files)

        return json.loads(response.content.decode('utf-8'))


    def get_completed(self, id):
        url = "https://d8n.host/api/completed?id={0}".format(id)

        payload={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return json.loads(response.content.decode('utf-8'))
    
    def download_entry(self, id, format = 'yolo'):
        url = "https://d8n.host/api/makesense?page=0".format(id)
        
        headers = {
            'API-KEY': self.API_key,
        }
        
        body = {
            'only_id':id,
            'format': format
        }
        
        response = requests.request("GET", url, headers=headers, data=body)

        return response.content