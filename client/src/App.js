import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import GroupStudyChat from "./components/GroupStudyChat";

function App() {
  return (
    <Router>
      <div className="p-4">
        <nav>
          <Link to="/study-room" className="text-blue-500 hover:underline">
            Join Group Study
          </Link>
        </nav>
        <Routes>
          <Route path="/study-room" element={<GroupStudyChat />} />
          <Route path="/" element={<h1>Welcome to Group Study</h1>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;