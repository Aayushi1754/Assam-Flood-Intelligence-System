import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

const API_BASE = "http://127.0.0.1:8000";

const ALGORITHMS = ["FCFS", "Round Robin", "Priority"];

function Results() {
  const navigation = useLocation();

  // Read the result passed from SubmitRequest.jsx
  const submittedResult = navigation.state?.result;

  const [requestId, setRequestId] = useState("");
  const [result, setResult] = useState(submittedResult || null);
  const [message, setMessage] = useState("");

  // Scheduling comparison state
  const [comparison, setComparison] = useState([]);
  const [comparisonLoading, setComparisonLoading] = useState(true);
  const [comparisonError, setComparisonError] = useState("");

  // Fetch scheduling results for all three algorithms
  useEffect(() => {
    let cancelled = false;

   async function fetchComparison() {
  setComparisonLoading(true);
  setComparisonError("");

  const results = await Promise.all(
    ALGORITHMS.map(async (algorithm) => {
      try {
        const url =
          `${API_BASE}/schedule-saved?algorithm=` +
          encodeURIComponent(algorithm);

        const response = await fetch(url,{method:"POST"});

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        return {
          algorithm,
          ...data,
          loadError: null,
        };
      } catch (error) {
        console.error(
          `Failed to load ${algorithm} scheduling results:`,
          error
        );

        return {
          algorithm,
          loadError: error.message,
        };
      }
    })
  );

  if (!cancelled) {
    setComparison(results);

    const failures = results.filter((item) => item.loadError);

    if (failures.length > 0) {
      setComparisonError(
        "Failed to load: " +
          failures
            .map((item) => `${item.algorithm} (${item.loadError})`)
            .join(", ")
      );
    }

    setComparisonLoading(false);
  }
}

    fetchComparison();

    return () => {
      cancelled = true;
    };
  }, []);

  // Existing demo search
  function handleSearch(event) {
    event.preventDefault();

    if (requestId.trim().toUpperCase() === "REQ001") {
      setResult({
        request_id: "REQ001",
        location: "Dhemaji, Assam",
        extracted_text:
          "Flood affected families need food, drinking water and medicine.",
        language: "English",
        urgency_level: "High",
        urgency_score: 0.85,
        extracted_keywords: [
          "Food",
          "Drinking water",
          "Medicine",
        ],
        saved_to_database: true,
      });

      setMessage("");
    } else {
      setResult(null);
      setMessage(
        "No matching demo request found. Submit a new request to view its analysis."
      );
    }
  }

  // Safely display existing backend results
  const extractedText =
    result?.extracted_text ?? result?.text ?? "";

  const urgency =
    result?.urgency_level ?? result?.urgency ?? "Not provided";

  const needs = Array.isArray(result?.extracted_keywords)
    ? result.extracted_keywords
    : Array.isArray(result?.resource_suggestions)
      ? result.resource_suggestions
      : result?.need
        ? [result.need]
        : [];

  // Find the best algorithm for each metric
  const bestWaitingTime = comparison.reduce(
    (best, item) => {
      const value = Number(item.average_waiting_time);

      if (!Number.isFinite(value)) return best;

      return best === null || value < best ? value : best;
    },
    null
  );

  const bestResponseTime = comparison.reduce(
    (best, item) => {
      const value = Number(item.average_response_time);

      if (!Number.isFinite(value)) return best;

      return best === null || value < best ? value : best;
    },
    null
  );

  function formatMetric(value) {
    if (value == null || !Number.isFinite(Number(value))) {
      return "—";
    }

    return Number(value).toFixed(2);
  }

  return (
    <div className="mx-auto max-w-[1600px] p-4 md:p-8">
      <h1 className="text-3xl font-bold text-gray-900">
        Relief Request Results
      </h1>

      <p className="mt-2 text-gray-600">
        View relief request analysis and compare flood-relief
        scheduling algorithms.
      </p>

      <form
        onSubmit={handleSearch}
        className="mt-6 flex max-w-xl gap-3"
      >
        <input
          type="text"
          placeholder="Enter demo request ID (REQ001)"
          value={requestId}
          onChange={(event) => setRequestId(event.target.value)}
          required
          className="min-w-0 flex-1 rounded-lg border p-3"
        />

        <button
          type="submit"
          className="rounded-lg bg-teal-700 px-5 text-white hover:bg-teal-800"
        >
          Search
        </button>
      </form>

      {message && (
        <p role="status" className="mt-4 text-red-600">
          {message}
        </p>
      )}

      {/* Two-column layout */}
      <div className="mt-8 grid grid-cols-1 items-start gap-6 lg:grid-cols-2">

        {/* LEFT: Existing relief request results */}
        <section className="min-w-0">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-800">
              Relief Request Analysis
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Extracted information and request details
            </p>
          </div>

          {result ? (
            <div className="space-y-4 rounded-xl border bg-white p-5 shadow-sm md:p-6">
              <h3 className="text-xl font-bold">
                Request Details
              </h3>

              <p className="break-words">
                <strong>Request ID:</strong>{" "}
                {result.request_id ?? "Not provided"}
              </p>

              <p className="break-words">
                <strong>Location:</strong>{" "}
                {result.location ?? "Not provided"}
              </p>

              {result.filename && (
                <p className="break-words">
                  <strong>Image:</strong> {result.filename}
                </p>
              )}

              <div>
                <h3 className="font-bold">
                  Extracted Text from Image
                </h3>

                <p className="mt-2 whitespace-pre-wrap break-words rounded-lg bg-gray-100 p-3">
                  {extractedText ||
                    "No extracted text available."}
                </p>
              </div>

              <h3 className="text-lg font-bold">
                Analysis Summary
              </h3>

              <p>
                <strong>Urgency Level:</strong>{" "}
                <span
                  className={`rounded-full px-3 py-1 text-sm font-semibold ${
                    urgency.toLowerCase() === "high" ||
                    urgency.toLowerCase() === "critical"
                      ? "bg-red-100 text-red-700"
                      : urgency.toLowerCase() === "medium"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-green-100 text-green-700"
                  }`}
                >
                  {urgency}
                </span>
              </p>

              {result.urgency_score != null && (
                <p>
                  <strong>Urgency Score:</strong>{" "}
                  {result.urgency_score}
                </p>
              )}

              {result.people_affected != null && (
                <p>
                  <strong>People Affected:</strong>{" "}
                  {result.people_affected}
                </p>
              )}

              <div>
                <strong>Identified Relief Needs:</strong>

                {needs.length > 0 ? (
                  <ul className="mt-2 list-inside list-disc space-y-1">
                    {needs.map((need, index) => (
                      <li key={index} className="break-words">
                        {typeof need === "string"
                          ? need
                          : need?.resource ??
                            need?.name ??
                            JSON.stringify(need)}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-gray-600">
                    No relief needs were returned by the backend.
                  </p>
                )}
              </div>

              <p>
                <strong>Saved to Database:</strong>{" "}
                {result.saved_to_database === true
                  ? "Yes"
                  : result.saved_to_database === false
                    ? "No"
                    : "Not confirmed"}
              </p>

              {result.message && (
                <p className="text-sm text-gray-600">
                  {result.message}
                </p>
              )}
            </div>
          ) : (
            <div className="rounded-xl border bg-white p-6 text-gray-600 shadow-sm">
              Submit a relief request or search for the demo
              request REQ001 to view the analysis.
            </div>
          )}
        </section>

        {/* RIGHT: Scheduling comparison matrix */}
        <section className="min-w-0">
          <div className="mb-4">
            <h2 className="text-2xl font-bold text-gray-800">
              Scheduling Comparison
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Compare FCFS, Round Robin, and Priority scheduling
              for flood-relief requests.
            </p>
          </div>

          <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
            <div className="border-b bg-teal-800 p-5 text-white">
              <h3 className="text-lg font-bold">
                Algorithm Performance Matrix
              </h3>

              <p className="mt-1 text-sm text-teal-100">
                Lower waiting and response times indicate better
                performance for these metrics.
              </p>
            </div>

            {comparisonLoading ? (
              <div
                className="p-8 text-center text-gray-600"
                role="status"
              >
                Loading scheduling comparison...
              </div>
            ) : comparisonError ? (
              <div className="p-5">
                <p className="text-sm text-red-600">
                  {comparisonError}
                </p>

                <button
                  type="button"
                  onClick={() => window.location.reload()}
                  className="mt-3 rounded-lg bg-teal-700 px-4 py-2 text-white hover:bg-teal-800"
                >
                  Retry
                </button>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[440px] text-left text-sm">
                    <thead className="bg-gray-100 text-gray-700">
                      <tr>
                        <th className="px-4 py-3 font-bold">
                          Algorithm
                        </th>

                        <th className="px-4 py-3 font-bold">
                          Avg. Waiting Time
                        </th>

                        <th className="px-4 py-3 font-bold">
                          Avg. Response Time
                        </th>

                        <th className="px-4 py-3 font-bold">
                          Requests Scheduled
                        </th>
                      </tr>
                    </thead>

                  <tbody className="divide-y">
  {comparison
    .filter((item) => !item.loadError)
    .map((item) => {
      const waiting = Number(item.average_waiting_time);
      const response = Number(item.average_response_time);  const isBestWaiting =
    Number.isFinite(waiting) &&
    item.average_waiting_time != null &&
    bestWaitingTime !== null &&
    waiting === bestWaitingTime;

  const isBestResponse =
    Number.isFinite(response) &&
    item.average_response_time != null &&
    bestResponseTime !== null &&
    response === bestResponseTime;

  return (
    <tr
      key={item.algorithm}
      className="hover:bg-gray-50"
    >
      <td className="whitespace-nowrap px-4 py-4 font-semibold">
        {item.algorithm}
      </td>

      <td
        className={`whitespace-nowrap px-4 py-4 ${
          isBestWaiting
            ? "font-bold text-green-700"
            : ""
        }`}
      >
        {formatMetric(item.average_waiting_time)}
        {isBestWaiting && (
          <span className="ml-1">★</span>
        )}
      </td>

      <td
        className={`whitespace-nowrap px-4 py-4 ${
          isBestResponse
            ? "font-bold text-green-700"
            : ""
        }`}
      >
        {formatMetric(item.average_response_time)}
        {isBestResponse && (
          <span className="ml-1">★</span>
        )}
      </td>

      <td className="whitespace-nowrap px-4 py-4">
        {item.total_requests ??
          item.scheduled_requests?.length ??
          "—"}
      </td>
    </tr>
  );
})}

{comparison.every((item) => item.loadError) && (
<tr>
<td
colSpan={4}
className="px-4 py-6 text-center text-gray-500"
>
No scheduling results are available.
</td>
</tr>
)}

</tbody>
                  </table>
                </div>

                <div className="grid grid-cols-1 gap-4 border-t bg-gray-50 p-5 sm:grid-cols-2">
                  <div className="rounded-lg border bg-white p-4">
                    <p className="text-sm text-gray-500">
                      Lowest Average Waiting Time
                    </p>

                    <p className="mt-2 text-xl font-bold text-green-700">
                      {bestWaitingTime === null
                        ? "Not available"
                        : comparison.find(
                            (item) =>
                              Number(item.average_waiting_time) ===
                              bestWaitingTime
                          )?.algorithm ?? "Not available"}
                    </p>

                    {bestWaitingTime !== null && (
                      <p className="mt-1 text-sm text-gray-600">
                        {formatMetric(bestWaitingTime)}
                      </p>
                    )}
                  </div>

                  <div className="rounded-lg border bg-white p-4">
                    <p className="text-sm text-gray-500">
                      Lowest Average Response Time
                    </p>

                    <p className="mt-2 text-xl font-bold text-green-700">
                      {bestResponseTime === null
                        ? "Not available"
                        : comparison.find(
                            (item) =>
                              Number(item.average_response_time) ===
                              bestResponseTime
                          )?.algorithm ?? "Not available"}
                    </p>

                    {bestResponseTime !== null && (
                      <p className="mt-1 text-sm text-gray-600">
                        {formatMetric(bestResponseTime)}
                      </p>
                    )}
                  </div>
                </div>

                <div className="border-t p-5">
                  <h3 className="font-bold text-gray-800">
                    Performance Interpretation
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-gray-600">
                    FCFS processes requests in arrival order.
                    Round Robin distributes processing time across
                    requests, while Priority scheduling considers
                    request urgency. The matrix compares their
                    measured waiting and response times using your
                    backend results.
                  </p>

                  <p className="mt-2 text-xs text-gray-500">
                    ★ indicates the lowest measured value for that
                    metric among the algorithms returned.
                  </p>
                </div>
              </>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Results;