API_URL = "https://llmwhisperer-api.us-central.unstract.com/api/v2" # No need to change it
API_KEY = "sr_slp55MUkpkeeHRSJipmylHDzHCBVZ_XWJi1U2KT4"# Your API key here you have to change it if it is expired

# Path to the file you want to process(chapter, pdf, docx, pptx, txt, etc.)
file_name = r"C:\RAG\05 Fundementals - String.pptx"

from unstract.llmwhisperer import LLMWhispererClientV2
from unstract.llmwhisperer.client_v2 import LLMWhispererClientException

client = LLMWhispererClientV2(base_url=API_URL, api_key=API_KEY)





whisper = client.whisper(
    file_path=file_name, 
    wait_for_completion=True,
    wait_timeout=200
)
print(whisper)




data = whisper['extraction']['result_text']
print(data)

# Save the extracted text to a file(you can change the path if you want)
with open(r"C:\RAG\05 Fundementals - String.txt", "w", encoding="utf-8") as f:
    f.write(data)

