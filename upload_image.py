import base64
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv()

# Azure Blob Storage Configuration
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def upload_base64_image(base64_string: str, file_extension: str = "png") -> str:
    """Decodes a base64 string, uploads it as an image to Azure Blob Storage, and returns the blob URL."""
    try:
        # Decode base64 string to binary data
        image_data = base64.b64decode(base64_string)

        # Generate a unique file name
        file_name = f"{uuid.uuid4()}.{file_extension}"

        # Get blob client
        blob_client = container_client.get_blob_client(file_name)

        # Upload the image data to Azure Blob Storage
        blob_client.upload_blob(image_data, overwrite=True)

        # Generate and return the blob URL
        blob_url = blob_client.url
        return blob_url
    except Exception as e:
        raise RuntimeError(f"Failed to upload image: {e}")
