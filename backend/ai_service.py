
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
        options={
            "temperature": 0,
            "num_predict": 500,
        },
        messages=[
            {
                "role": "system",
                "content": (
                    "You select container slots from a supplied JSON input. "
                    "Return one JSON object with a placements array. "
                    "Each item must contain integer fields container_ref "
                    "and slot_ref. Copy container_ref only from the "
                    "input containers array. Copy slot_ref only from "
                    "that container's candidate_slots array. "
                    "The input contains exactly five containers, whose "
                    "container_ref values are 0, 1, 2, 3, and 4. "
                    "Never use any other container_ref. "
                    "Never use a slot_ref that is not listed for that "
                    "container. Do not create extra placements. "
                    "Do not include explanations or markdown."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.message.content
