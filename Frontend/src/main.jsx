import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./index.css";

// Find the root HTML element and render the React application
createRoot(document.getElementById("root")).render(
  <StrictMode>
    {/* Enable navigation between pages */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);

