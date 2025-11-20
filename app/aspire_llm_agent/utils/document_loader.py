from langchain_core.documents import Document
import requests
import magic
import fitz



async def download_file(url: str, canvas_api_token: str):
    if "drive.google.com" in url:
        return await get_document_from_drive_link(drive_link=url)
    elif "instructure.com" in url:  
        return await download_from_canvas(url, canvas_api_token)
    else:
        return await download_from_generic_url(url)


async def extract_google_drive_file_id(url: str) -> str:
    if 'd/' in url:
        return url.split('d/')[1].split('/')[0]
    elif 'id=' in url:
        return url.split('id=')[1]
    else:
        raise ValueError("Invalid Google Drive URL format")


async def get_document_from_drive_link(drive_link: str) -> Document:
    file_id = await extract_google_drive_file_id(url=drive_link)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    response = requests.get(download_url)
    response.raise_for_status()
    return await process_response(response=response, url=drive_link)


async def download_from_canvas(url: str, canvas_api_token: str):
    headers = {
        'Authorization': f'Bearer {canvas_api_token}',
        'Content-Type': 'application/json'
    }
    url = 'https://ucsd-dev.instructure.com/api/v1/files/258'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return await process_response(response=response, url=url)


async def download_from_generic_url(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return await process_response(response=response, url=url)


async def process_response(response, url):
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')

        if content_type and 'text' in content_type:
            return Document(page_content=response.text, metadata={"source": url})

        elif content_type == 'application/pdf':
            pdf_text = await extract_text_from_pdf(response.content)
            return Document(page_content=pdf_text, metadata={"source": url})
        
        elif content_type == 'application/octet-stream':
            file_type = magic.from_buffer(response.content, mime=True)
            
            if 'pdf' in file_type:
                pdf_text = await extract_text_from_pdf(response.content)
                return Document(page_content=pdf_text, metadata={"source": url})
            elif 'text' in file_type:
                return Document(page_content=response.text, metadata={"source": url})
            else:
                print("Unknown file type.")
                return None

    return None


async def extract_text_from_pdf(pdf_content: bytes) -> str:
    pdf_text = ""
    with fitz.open(stream=pdf_content, filetype="pdf") as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            pdf_text += page.get_text()
    return pdf_text


async def get_files_from_url(location: str, extra_params:dict={}):
    canvas_api_token = extra_params.get("canvas_api_key")
    try:
        file_content = await download_file(location, canvas_api_token)

        if file_content:
            return file_content

    except Exception as e:
        print(f"Failed to download file from {location}: {e}")
    
    return None
