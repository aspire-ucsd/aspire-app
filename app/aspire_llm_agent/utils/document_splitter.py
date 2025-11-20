import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

async def split_docs(document:Document, extra_params:dict={}):
    tiktoken.encoding_for_model('gpt-3.5-turbo')
    tokenizer = tiktoken.get_encoding('cl100k_base')

    # create the length function
    def tiktoken_len(text):
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)

    splits = RecursiveCharacterTextSplitter(
        chunk_size=512*2 - 1, 
        chunk_overlap=256, 
        length_function=tiktoken_len, 
        separators=["\n\n", "\n", " ", ""],
        keep_separator=False
    ).split_documents([document])

    return splits