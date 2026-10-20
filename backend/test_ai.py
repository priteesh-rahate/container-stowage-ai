
from backend.ai_service import ask_local_ai


if __name__ == "__main__":
    print("Testing local AI...")
    answer = ask_local_ai(
        "Explain the purpose of a container stowage plan in two sentences."
    )
    print("\nQwen response:")
    print(answer)
