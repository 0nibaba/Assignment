from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from io import BytesIO
import logging

AZURE_STORAGE_ACCOUNT_NAME = "astrapiaapitask"
AZURE_STORAGE_ACCOUNT_KEY = "QllBgiNI1HKSWelVbZlMSHZNgj+nqdn1yG08NRgV34Wl82y6IAXqNGpw4KGHfgb9IKN31hUBwMAt+AStHXIkkw=="
AZURE_STORAGE_CONTAINER_NAME = "container1"

app = FastAPI()

blob_service_client = BlobServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=AZURE_STORAGE_ACCOUNT_KEY
)

container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)


def is_text_file(file: UploadFile):
    return file.content_type == 'text/plain' and file.filename.endswith('.txt')


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not is_text_file(file):
        raise HTTPException(status_code=400, detail="Only text files (.txt) are allowed.")
    
    try:
        file_contents = await file.read()
        blob_client = container_client.get_blob_client(file.filename)
        
        blob_client.upload_blob(file_contents, overwrite=True)
        
        return {"message": f"Text file '{file.filename}' uploaded successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")


# Initialize logging
logging.basicConfig(level=logging.INFO)

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    logging.info(f"Received request to download file: {file_name}")
    
    # Check if the file name has a ".txt" extension
    if not file_name.endswith(".txt"):
        logging.error(f"Invalid file extension for {file_name}")
        raise HTTPException(status_code=400, detail="Only text files (.txt) can be downloaded.")
    
    try:
        # Get the blob client for the file
        blob_client = container_client.get_blob_client(file_name)
        logging.info(f"Attempting to download file '{file_name}' from Azure Blob Storage.")
        
        # Check if the blob exists
        blob_exists = blob_client.exists()
        if not blob_exists:
            logging.error(f"File '{file_name}' not found in the container.")
            raise HTTPException(status_code=404, detail=f"File '{file_name}' not found in the container.")
        
        # Download the file data
        try:
            download_stream = blob_client.download_blob()
            file_data = download_stream.readall()
            logging.info(f"Downloaded {len(file_data)} bytes of data from the file '{file_name}'")
        except Exception as e:
            logging.error(f"Error occurred while downloading the blob: {e}")
            raise HTTPException(status_code=500, detail=f"Error downloading file '{file_name}': {e}")

        # Create a BytesIO object to send the file as a response
        response = BytesIO(file_data)
        response.seek(0)  # Move to the beginning of the file
        
        logging.info(f"Successfully downloaded file: {file_name}")
        
        # Return the file as a StreamingResponse with a 'text/plain' media type
        return StreamingResponse(response, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename={file_name}"})
    
    except Exception as e:
        logging.error(f"Error in downloading file '{file_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
