import time
import os

from fastapi import FastAPI, File, UploadFile
from dotenv import load_dotenv

from io import BytesIO

load_dotenv()

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
endpoint = os.getenv("AZURE_ENDPOINT")

app = FastAPI()

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

@app.post("/ocrZeImage/")
async def ocrZeImage(file: bytes = File()):
    all_txt = ""
    read_response = computervision_client.read_in_stream(BytesIO(file),  raw=True)
    read_operation_location = read_response.headers["Operation-Location"]

    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Append the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                all_txt += line.text + "\n"


    return {"ocred_text": all_txt}