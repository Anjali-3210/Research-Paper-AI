from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research assistant. Answer in simple language."),
    ("human", "What is the main contribution of this research paper?")
])

messages = prompt.invoke({
    "topic": "machine learning"
})

result = model.invoke(messages)

print(result.content)