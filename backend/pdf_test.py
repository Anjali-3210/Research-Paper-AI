from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyMuPDFLoader("data/paper.pdf")

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print("Number of chunks:", len(chunks))
print("\nFirst chunk:\n")
print(chunks[0].page_content)
print("\nFirst chunk metadata:\n")
print(chunks[0].metadata)

print("\nLast 200 characters of chunk 0:\n")
print(chunks[0].page_content[-200:])

print("\nFirst 200 characters of chunk 1:\n")
print(chunks[1].page_content[:200])