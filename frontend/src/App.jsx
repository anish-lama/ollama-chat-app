import { useEffect, useState } from "react";
import "./App.css";
import Login from "./Login";
import Chat from "./Chat";
import Register from "./Register";

function App(){
  const [token, setToken] = useState(null);
  const [showLogin, setShowLogin] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("token");
    if (saved) setToken(saved);
  }, []);

  return (
    <div>
      {token ? (
        <Chat token={token} setToken={setToken}/>
      ) : showLogin ? (
        <Login setToken={setToken} setShowLogin={setShowLogin} />
      ) : (
        <Register setShowLogin={setShowLogin} />
      )}
    </div>
  );
}

export default App;
