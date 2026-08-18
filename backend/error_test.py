def call_ai():
    try:
        raise Exception("429 RESOURCE_EXHAUSTED")

    except Exception as error:
        print("\nAI service error:")
        print(error)
        return "The AI service is temporarily unavailable. Please try again later."


result = call_ai()

print("\nResult:")
print(result)