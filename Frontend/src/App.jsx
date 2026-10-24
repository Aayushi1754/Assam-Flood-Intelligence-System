import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import SubmitRequest from "./pages/SubmitRequest";
import Results from "./pages/Results";
import Operations from "./pages/Operations";

function App() {
  return (
    // Main layout of the website
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />

      {/* Display the page selected by the URL */}
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/submit-request" element={<SubmitRequest />} />
          <Route path="/results" element={<Results />} />
          <Route path="/operations" element={<Operations />} />
        </Routes>
      </div>

      <Footer />
    </div>
  );
}

export default App;
