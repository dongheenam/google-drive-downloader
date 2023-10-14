from __future__ import print_function

import argparse
import io
import os.path
import re

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]
OUTPUT_DIR = "output/"


def parse_URL(url: str):
    """Parses a google drive URL and returns the file id"""
    file_id_pattern = r"/d/([a-zA-Z0-9_-]+)"
    match = re.search(file_id_pattern, url)
    if match:
        file_id = match.group(1)
        return file_id
    else:
        raise ValueError("Invalid URL")


def get_meta(file_id, service):
    """Query the name of the file and its mimetype
    Args:
        file_id: ID of the file to query
        service: google API Service object
    Returns : Tuple containing the name and mimetype of the file
    """
    try:
        # pylint: disable=maybe-no-member
        meta = service.files().get(fileId=file_id).execute()
        name = meta["name"]
        mime_type = meta["mimeType"]
        return name, mime_type
    except HttpError as error:
        print(f"HTTP error occurred while fetching meta: {error}")


def download_file(file_id, service):
    """Downloads a file
    Args:
        file_id: ID of the file to download
        service: google API Service object
    Returns : FileIO object containing the file
    """
    try:
        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

    except HttpError as error:
        print(f"HTTP error occurred while downloading file: {error}")
        file = None

    return file


def export_file(file_id, mime_type, service):
    """Export a Google Drive file (Docs, Slides, ...) as an Office Document
    Args:
        file_id: ID of the file to download
        mime_type: mimetype of the source file
        service: google API Service object
    Returns : FileIO object containing the file
    """
    MIME_TYPE_WORD_PREFIX = "application/vnd.openxmlformats-officedocument"
    MIME_TYPE_INDEX = {
        "document": "wordprocessingml.document",
        "spreadsheet": "spreadsheetml.sheet",
        "presentation": "presentationml.presentation",
    }
    document_type = mime_type.split(".")[-1]
    request_mime_type = f"{MIME_TYPE_WORD_PREFIX}.{MIME_TYPE_INDEX[document_type]}"

    try:
        # pylint: disable=maybe-no-member
        request = service.files().export_media(
            fileId=file_id, mimeType=request_mime_type
        )
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()

    except HttpError as error:
        print(f"HTTP error occurred while downloading file: {error}")
        file = None

    return file


def get_file_extension(mime_type):
    """Returns the file extension for a given mimetype
    Args:
        mime_type: mimetype of the file
    Returns : File extension
    """
    if mime_type == "application/vnd.google-apps.document":
        return ".docx"
    elif mime_type == "application/vnd.google-apps.spreadsheet":
        return ".xlsx"
    elif mime_type == "application/vnd.google-apps.presentation":
        return ".pptx"
    else:
        return ""


def save_file(bytes: io.BytesIO, filename: str):
    """Saves a file to disk
    Args:
        bytes: bytesIO object
        filename: filename to save to
    """
    bytes.seek(0)
    with open(os.path.join(OUTPUT_DIR, filename), "wb") as f:
        f.write(bytes.getbuffer())


def init():
    """
    initialize the google drive api
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # create drive api client
    service = build("drive", "v3", credentials=creds)

    return service


def parse_args():
    parser = argparse.ArgumentParser(description="Download a file from google drive")
    parser.add_argument("url", help="URL of the file to download")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    file_id = parse_URL(args.url)

    service = init()
    name, mime_type = get_meta(file_id, service)

    file_media = None
    if mime_type.startswith("application/vnd.google-apps"):
        file_media = export_file(file_id, mime_type, service)
        extension = get_file_extension(mime_type)
        name = name + extension
    else:
        file_media = download_file(parse_URL(args.url), service)
    if file_media is not None:
        print(f"Downloaded {name}!")
        save_file(file_media, name)
    else:
        print("Failed to download file with id {file_id}...")
