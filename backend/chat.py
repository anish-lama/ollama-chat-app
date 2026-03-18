import ollama

messages = []

print("Ollama Chat (type 'exit' to quit)\n")

while True:
    user_input = input("You:")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    messages.append({
        "role": "user",
        "content": user_input
    })

    response = ollama.chat(
        model="llama3",
        messages=messages
    )

    assistant_reply = response["message"]["content"]

    print(f"AI: {assistant_reply}\n")

    messages.append({
        "role": "assistant",
        "content": assistant_reply
    })