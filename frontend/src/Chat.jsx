import { useState } from "react";

function Chat({ token, setToken }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

const handleSend = async () => {
  if (!input.trim()) return;

  const userMessage = input;

  setMessages(prev => [...prev, { role: "You", text: userMessage }]);
  setInput("");

  // 🔥 CHANGE: let instead of const
  let response = await fetch("https://ollama-chat-app-qxb4.onrender.com/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ message: userMessage })
  });

  // 🔥 HANDLE 401
  if (response.status === 401) {
    console.log("Access token expired, trying refresh...");

    const refreshRes = await fetch("https://ollama-chat-app-qxb4.onrender.com/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        refresh_token: localStorage.getItem("refresh_token")
      })
    });

    const refreshData = await refreshRes.json();

    if (refreshRes.ok) {
      // ✅ save new token
      localStorage.setItem("access_token", refreshData.access_token);
      setToken(refreshData.access_token);

      console.log("New access token received");

      // 🔥 IMPORTANT: reassign SAME response
      response = await fetch("https://ollama-chat-app-qxb4.onrender.com/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${refreshData.access_token}`
        },
        body: JSON.stringify({ message: userMessage })
      });

    } else {
      alert("Session expired. Please login again.");
      localStorage.clear();
      setToken(null);
      return;
    }
  }

  const data = await response.json();

    setMessages(prev => [
      ...prev,
      { role: "AI", text: data.response }
    ]);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");   
    localStorage.removeItem("refresh_token");  
    setToken(null);
  };

  return (
    <div className="app">

      <button onClick={handleLogout}>Logout</button>

      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div>{msg.text}</div>
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter"){
              handleSend();
            }
          }}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default Chat;