import http.client
from io import BytesIO
import mimetypes
from codecs import encode
from threading import Timer
import time
import requests
import json
from typing import Any
from dataclasses import dataclass
from PIL import Image

@dataclass
class d8nCompleteResult:
    prediction_id: str
    _class: str
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    type: str
    # segment: List[int]
    text: str

    @staticmethod
    def from_dict(obj: Any) -> 'd8nCompleteResult':
        _prediction_id = str(obj.get("prediction_id"))
        __class = str(obj.get('_class'))
        _x1 = float(obj.get("x1"))
        _y1 = float(obj.get("y1"))
        _x2 = float(obj.get("x2"))
        _y2 = float(obj.get("y2"))
        _confidence = float(obj.get("confidence"))
        _type = str(obj.get("type"))
        # _segment = [.from_dict(y) for y in obj.get("segment")]
        _text =str(obj.get("text"))
        return d8nCompleteResult(_prediction_id, __class, _x1, _y1, _x2, _y2, _confidence, _type, _text)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)

@dataclass
class d8nResult:
    id: str
    status: str
    api_version: str
    help: str

    @staticmethod
    def from_dict(obj: Any) -> 'd8nResult':
        _id = str(obj.get("id"))
        _status = str(obj.get("status"))
        _api_version = str(obj.get("api_version"))
        _help = str(obj.get("help"))
        return d8nResult(_id, _status, _api_version, _help)

class d8nClient:
    def __init__(self, api_key):
        """_summary_

        Args:
            api_key (_type_): The API key provided to you by engisense
        """
        self.API_key = api_key
        self._url = 'engisense.com'


    def wait_till_completed(self, id, timeout = 15, print_debug_info = False):
        """_summary_

        Args:
            id (_type_): The id of the request
            timeout (int, optional): The time to wait before raising an exception. Defaults to 10.

        Raises:
            Exception: If the request didn't complete by this time we will raise an exception
        """
        timer = Timer(timeout, lambda: 'ok')
        timer.start()

        while True:
           data = self.fetch_status(id)
           status =  data.status
           if print_debug_info:
               print("Current task: {0}".format(status))
           if 'Completed' in status or 'Failed' in status:
               break
           if timer.finished.isSet():
               raise Exception("Timeout :/")
           
           time.sleep(1)

    def from_local_file(self, path, project_id = None):
        """_summary_

        Args:
            path (_type_): The path to the image or pdf file you want to analyse
            project_id (_type_, optional): Optional parameter to group documents into a single project. Defaults to None.

        Returns:
            _type_: Returns 
        """
        conn = http.client.HTTPSConnection(self._url)
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
            
        conn.request("POST", "/api/analysis", payload, headers)
        res = conn.getresponse()
        data = res.read()
        data = (data.decode("utf-8"))
        return d8nResult.from_dict(json.loads(data))

    def fetch_status(self, id:str) -> d8nResult:
        url = "https://{0}/api/get_status?id={1}".format(self._url,id)

        payload={}
        files={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload, files=files)
        if response.status_code < 200 and response.status_code >= 300:
            raise Exception(str(response.status_code))
        return d8nResult.from_dict(json.loads(response.content.decode('utf-8')))

    def get_completed(self, id: str):
        """_summary_

        Args:
            id (str): The id of the request for which to get the bounding boxes

        Returns:
            d8nCompleteResult: The list of predicted bounding boxes, their types and coordinates
        """
        url = "https://{0}/api/completed?id={1}".format(self._url,id)
        payload={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        data = json.loads(response.content.decode('utf-8'))

        return [d8nCompleteResult.from_dict(x) for x in data]
    
    def get_line_image(self, id: str) -> Image.Image:
        """Returns a rendering of the detected lines

        Args:
            id (str): The id of the request

        Returns:
            PIL.Image: A PIL.Image rendering the detected lines
        """
        url = "https://{0}/api/get_lines?id={1}".format(self._url,id)
        payload={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        bytesIO = BytesIO(response.content)
        bytesIO.seek(0)
        return Image.open(bytesIO)
    

    def get_symbol_image(self, id: str) -> Image.Image:
        """Returns a rendering of the detected symbols

        Args:
            id (str): The id of the request

        Returns:
            PIL.Image: A PIL.Image rendering the detected symbols
        """
        url = "https://{0}/api/get_symbols?id={1}".format(self._url,id)
        payload={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        bytesIO = BytesIO(response.content)
        bytesIO.seek(0)
        return Image.open(bytesIO)

    def download_entry(self, id, format = 'yolo'):
        url = "https://{0}/api/completed?id={1}".format(self._url,id)
        
        headers = {
            'API-KEY': self.API_key,
        }
        
        body = {
            'only_id':id,
            'format': format
        }
        
        response = requests.request("GET", url, headers=headers, data=body)

        return response.content