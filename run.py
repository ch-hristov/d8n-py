 # Example Usage
import zipfile
from d8n.d8nClient import d8nClient

api_key = 'mark_viewport'
client = d8nClient(api_key)
result_id = client.from_local_file('/Users/christosavovchristov/symbol-api/d8n-js/test.jpeg')

print(result_id)
# Fetch the status of your request
status = client.fetch_status(result_id)

# Once the status is completed, download the resulting json data or image.
# The data is in x, y, w, h format, normalized to original the image size.
# Where x, y = top left corner of each bounding box, and w, h are width and height of the box
# Learn more about the format 
# zip_file = client.download_entry(id)
# save_file = './file.zip'
            
# with zipfile.ZipFile(save_file, 'w') as zip:
#   zip.writestr('file.zip',zip_file)