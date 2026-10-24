
import { useState } from "react";

function Results() {
  // Store the request ID entered by the user
  const [requestId, setRequestId] = useState("");

  // Store the analysis results to display
  const [result, setResult] = useState(null);

  // Store a message when a request is not found
  const [message, setMessage] = useState("");

  // Search for a request when the form is submitted
  function handleSearch(event) {
    // Prevent the page from refreshing
    event.preventDefault();

    // Check whether the entered ID matches our sample request
    if (requestId.trim().toUpperCase() === "REQ001") {
      // Display sample analysis results for REQ001
      setResult({
        request_id: "REQ001",
        location: "Dhemaji, Assam",
        extracted_text:
          "Flood affected families need food, drinking water and medicine.",
        language: "English",
        urgency_level: "High",
        urgency_score: 0.85,
        extracted_keywords: ["Food", "Drinking water", "Medicine"],
        saved_to_database: true,
      });

      // Clear any previous error message
      setMessage("");
    } else {
      // Clear old results if the ID is not found
      setResult(null);

      // Display a message for an unknown request ID
      setMessage("No request found. Please check the Request ID.");
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      {/* Display the page heading */}
      <h1 className="text-3xl font-bold">
        Relief Request Results
      </h1>

      {/* Explain what information this page displays */}
      <p className="mt-2 text-gray-600">
        View extracted text and relief request analysis.
      </p>

      {/* Form for searching using a Request ID */}
      <form onSubmit={handleSearch} className="mt-6 flex gap-3">
        <input
          type="text"
          placeholder="Enter request ID"
          value={requestId}
          // Update the ID when the user types
          onChange={(event) => setRequestId(event.target.value)}
          required
          className="flex-1 rounded border p-3"
        />

        {/* Button to search for the request */}
        <button
          type="submit"
          className="rounded bg-teal-700 px-5 text-white"
        >
          Search
        </button>
      </form>

      {/* Display a message if the request ID is not found */}
      {message && (
        <p role="status" className="mt-4 text-red-600">
          {message}
        </p>
      )}

      {/* Display the analysis results when a request is found */}
      {result && (
        <div className="mt-6 space-y-4 rounded-lg border bg-white p-6">
          {/* Display basic request information */}
          <h2 className="text-xl font-bold">Request Details</h2>

          <p>
            <strong>Request ID:</strong> {result.request_id}
          </p>

          <p>
            <strong>Location:</strong> {result.location}
          </p>

          {/* Display text extracted from the news image using OCR */}
          <div>
            <h3 className="font-bold">Extracted Text from Image</h3>

            <p className="mt-2 rounded bg-gray-100 p-3">
              {result.extracted_text}
            </p>

            {/* Display the detected language */}
            <p className="mt-1 text-sm text-gray-600">
              Detected Language: {result.language}
            </p>
          </div>

          {/* Display the needs and urgency identified by NLP */}
          <h3 className="text-lg font-bold">Analysis Summary</h3>

          <p>
            <strong>Urgency Level:</strong> {result.urgency_level}
          </p>

          <p>
            <strong>Urgency Score:</strong> {result.urgency_score}
          </p>

          {/* Display the list of identified relief needs */}
          <div>
            <strong>Extracted Needs:</strong>
            <ul className="mt-2 list-inside list-disc">
              {result.extracted_keywords.map((need, index) => (
                <li key={index}>{need}</li>
              ))}
            </ul>
          </div>

          {/* Display the sample database status */}
          <p>
            <strong>Saved to Database:</strong>{" "}
            {result.saved_to_database ? "Yes" : "No"}
          </p>

          {/* Clearly identify the current results as sample data */}
          <p className="text-sm text-gray-500">
            Demo results for frontend testing only.
          </p>
        </div>
      )}
    </div>
  );
}

export default Results;
