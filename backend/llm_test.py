from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0
)

result = model.invoke(
    "Explain what a research paper is in two sentences."
)

print(result.content)