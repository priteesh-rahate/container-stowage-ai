
import ollama


MODEL_NAME = "qwen2.5:7b"


def ask_local_ai(prompt: str) -> str:
    """Send a prompt to the locally running Ollama model."""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant for a container vessel "
                    "stowage planning system. Give clear, concise "
                    "answers. Never claim that a stowage plan is "
                    "physically valid unless the Python placement "
                    "engine has validated it."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.message.content

def propose_container_placements(prompt: str) -> str:
    """Ask the local AI to propose container placement decisions."""

    response = ollama.chat(
        model=MODEL_NAME,
        format="json",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI assistant for container vessel "
                    "stowage planning. Propose placements only using "
                    "the candidate slots provided by the user. "
                    "Return valid JSON only. Do not invent slot IDs. "
                    "Do not claim physical vessel safety or stability "
                    "has been verified."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.message.content