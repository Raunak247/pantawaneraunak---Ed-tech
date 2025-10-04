import React, { useState, useEffect } from "react";
import io from "socket.io-client";

const socket = io("http://localhost:3000");

const GroupStudyChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [username, setUsername] = useState("");
  const [isUsernameSet, setIsUsernameSet] = useState(false);

  useEffect(() => {
    socket.on("connect", () => {
      console.log("Connected to server:", socket.id);
    });
    socket.on("chatMessage", (msg) => {
      console.log("Received message:", msg);
      setMessages((prev) => [...prev, msg]);
    });

    return () => {
      socket.off("connect");
      socket.off("chatMessage");
    };
  }, []);

  const handleSetUsername = () => {
    if (username.trim()) {
      setIsUsernameSet(true);
    }
  };

  const sendMessage = () => {
    if (input.trim() && isUsernameSet) {
      const message = {
        user: username,
        text: input,
        timestamp: new Date().toISOString()
      };
      console.log("Sending message:", message);
      socket.emit("chatMessage", message);
      setInput("");
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto bg-gray-100 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Group Study Room</h2>
      {!isUsernameSet ? (
        <div className="mb-4">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="border p-2 mr-2 rounded"
            placeholder="Enter your username"
            onKeyPress={(e) => e.key === "Enter" && handleSetUsername()}
          />
          <button
            onClick={handleSetUsername}
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
          >
            Join Chat
          </button>
        </div>
      ) : (
        <>
          <div className="h-64 overflow-y-scroll border p-2 bg-white mb-2">
            {messages.map((msg, index) => (
              <div key={index} className="mb-2">
                <span className="font-semibold">{msg.user}</span>: {msg.text}
                <span className="text-gray-500 text-sm ml-2">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
          <div className="flex">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 border p-2 rounded-l"
              placeholder="Type a message..."
              onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            />
            <button
              onClick={sendMessage}
              className="bg-blue-500 text-white p-2 rounded-r hover:bg-blue-600"
            >
              Send
            </button>
          </div>
        </>
      )}
      <link
        href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
        rel="stylesheet"
      />
    </div>
  );
};

export default GroupStudyChat;