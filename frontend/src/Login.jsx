import { useState } from "react";

function Login({ setToken, setShowLogin}){
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async() => {
    const res = await fetch("https://ollama-chat-app-qxb4.onrender.com/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    console.log("STATUS:", res.status);

    const data = await res.json();
    console.log("DATA:", data);

    if(res.ok){
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      setToken(data.access_token);
    }
    else{
      alert("Login failed!!")
    }
  };

  return(
    <div>
        <h2>Login</h2>

        <input
          placeholder="Username"
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={handleLogin}>Login</button>

        <p>
            Don’t have an account?{" "}
            <button onClick={() => setShowLogin(false)}>Register</button>
        </p>
    </div>
  );
}



export default Login;