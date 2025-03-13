import http.client
from io import BytesIO
import mimetypes
from codecs import encode
import os
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
    task_list: list[str]

    @staticmethod
    def from_dict(obj: Any) -> 'd8nResult':
        _id = str(obj.get("id"))
        _status = str(obj.get("status"))
        _api_version = str(obj.get("api_version"))
        _help = str(obj.get("help"))
        _task_list = obj.get("task_list")
        return d8nResult(_id, _status, _api_version, _help, _task_list)

class d8nClient:
    def __init__(self, api_key, api_url="https://engisense.com"):
        """_summary_

        Args:
            api_key (_type_): The API key provided to you by engisense
        """
        if not api_url.startswith(("http://", "https://")):
            api_url = "http://" + api_url  # Default to HTTP for localhost
        self._url = api_url.rstrip("/")  # Remove trailing slashes
        self.API_key = api_key

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
           if 'Finished' in status or 'Failed' in status:
               return data
               break
           if timer.finished.isSet():
               raise Exception("Timeout :/")
           
           time.sleep(1)
        return None

    def from_local_file(self, file_path, project_id="default"):
        """
        Sends an image or PDF file to the API for analysis.

        Args:
            file_path (str): Path to the image or PDF file.
            project_id (str, optional): Optional parameter to group documents into a project.

        Returns:
            dict: API response as a dictionary.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError(f"File is empty: {file_path}")

        print(f"Uploading file {file_path}, Size: {file_size} bytes")

        url = f"{self._url}/api/analysis"
        file_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        headers = {
            "API-KEY": self.API_key
        }

        data = {}
        if project_id:
            data["project_id"] = project_id

        # ✅ Open file in binary mode and send correctly
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, file_type)}
            response = requests.post(url, headers=headers, files=files)

        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
    def fetch_status(self, id:str) -> d8nResult:
        url = "{0}/api/get_document_status?id={1}".format(self._url,id)

        payload={}
        files={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload, files=files)
        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(str(response.status_code))
        return d8nResult.from_dict(json.loads(response.content.decode('utf-8')))

    def get_completed(self, id: str):
        """_summary_

        Args:
            id (str): The id of the request for which to get the bounding boxes

        Returns:
            d8nCompleteResult: The list of predicted bounding boxes, their types and coordinates
        """
        url = "{0}/api/completed?id={1}&page=0".format(self._url,id)
        payload={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = response.json()

        return [d8nCompleteResult.from_dict(x) for x in data]
    
    def get_line_image(self, id: str) -> Image.Image:
        """Returns a rendering of the detected lines

        Args:
            id (str): The id of the request

        Returns:
            PIL.Image: A PIL.Image rendering the detected lines
        """
        url = "{0}/api/get_lines?id={1}".format(self._url,id)
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
        url = "{0}/api/get_symbols?id={1}".format(self._url,id)
        payload={}
        headers = {
            'API-KEY': self.API_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        bytesIO = BytesIO(response.content)
        bytesIO.seek(0)
        return Image.open(bytesIO)

    def download_entry(self, id, format = 'yolo'):
        url = "{0}/api/completed?id={1}".format(self._url,id)
        
        headers = {
            'API-KEY': self.API_key,
        }
        
        body = {
            'only_id':id,
            'format': format
        }
        
        response = requests.request("GET", url, headers=headers, data=body)

        return response.content