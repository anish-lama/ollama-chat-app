const input = document.getElementById("message")

input.addEventListener("keydown", function(event){

    if(event.key === "Enter" && !event.shiftKey){
        event.preventDefault()
        sendMessage()
    }

})


async function sendMessage(){

    const message = input.value.trim()

    if(!message) return

    const chatBox = document.getElementById("chat-box")

    chatBox.innerHTML += `
        <div class="message user">
            ${message}
        </div>
    `

    input.value = ""

    chatBox.innerHTML += `
        <div class="message ai typing" id="typing">
            AI is typing...
        </div>
    `

    chatBox.scrollTop = chatBox.scrollHeight

    const response = await fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            message:message
        })
    })

    const data = await response.json()

    document.getElementById("typing").remove()

    chatBox.innerHTML += `
        <div class="message ai">
            ${data.response}
        </div>
    `

    chatBox.scrollTop = chatBox.scrollHeight
}