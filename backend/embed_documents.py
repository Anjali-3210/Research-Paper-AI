from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# 1. Load the research paper
loader = PyMuPDFLoader("data/paper.pdf")
documents = loader.load()

# 2. Split the paper into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print("Number of chunks:", len(chunks))

# 3. Create the embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# 4. Store chunks and embeddings in ChromaDB
vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db",
    collection_name="research_papers"
)

print("Vector store created successfully!")