function ResultCard({ result }) {
  // Show a message if no analysis result is available
  if (!result) {
    return null;
  }

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-xl font-bold">
        Relief Request Analysis
      </h2>

      <p>
        <strong>Request ID:</strong>{" "}
        {result.request_id || "Not available"}
      </p>

      <p>
        <strong>Location:</strong>{" "}
        {result.location || "Not available"}
      </p>

      <p>
        <strong>Urgency:</strong>{" "}
        {result.urgency_level || "Not available"}
      </p>

      <p>
        <strong>Urgency Score:</strong>{" "}
        {result.urgency_score ?? "Not available"}
      </p>

      <div className="mt-3">
        <strong>Extracted Keywords:</strong>
        {Array.isArray(result.extracted_keywords) &&
        result.extracted_keywords.length > 0 ? (
          <ul className="mt-2 list-inside list-disc">
            {result.extracted_keywords.map((keyword, index) => (
              <li key={`${keyword}-${index}`}>{keyword}</li>
            ))}
          </ul>
        ) : (
          <p>No keywords available.</p>
        )}
      </div>
    </div>
  );
}

export default ResultCard;
