import axios from "axios";

// Set the address of the FastAPI backend
const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Send a relief request to the backend
export async function submitReliefRequest(location, text) {
  const response = await API.post("/analyze-flood", {
    location: location,
    text: text,
  });

  // Return the response received from FastAPI
  return response.data;
}
