import { useState } from "react";

function Register({ setShowLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async () => {

    const res = await fetch("https://ollama-chat-app-qxb4.onrender.com/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

  
    const data = await res.json();

    if (res.ok) {
      alert("User created! Now login.");
      setShowLogin(true);  
    } else {
      alert(data.detail || "Registration failed");
    }
  };

  return (
    <div>
      <h2>Register</h2>

      <input
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={handleRegister}>Register</button>

      <p>
        Already have an account?{" "}
        <button onClick={() => setShowLogin(true)}>Login</button>
      </p>
    </div>
  );
}

export default Register;