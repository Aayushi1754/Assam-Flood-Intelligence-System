import { useState } from "react";

function Operations() {
  // Store the selected scheduling algorithm
  const [algorithm, setAlgorithm] = useState("Priority");

  // Control when scheduling results are displayed
  const [showResults, setShowResults] = useState(false);

  // Store resource allocation form details
  const [requestId, setRequestId] = useState("");
  const [resource, setResource] = useState("Food");
  const [quantity, setQuantity] = useState("");

  // Store the allocation status message
  const [message, setMessage] = useState("");

  // Display sample scheduling results
  function handleSchedule() {
    setShowResults(true);
  }

  // Handle resource allocation form submission
  function handleAllocation(event) {
    event.preventDefault();

    // Show a message for the frontend demonstration
    setMessage(
      `${quantity} unit(s) of ${resource} prepared for request ${requestId}.`
    );
  }

  return (
    <div className="mx-auto max-w-4xl p-8">
      {/* Page heading */}
      <h1 className="text-3xl font-bold">Relief Operations</h1>

      <p className="mt-2 text-gray-600">
        Schedule relief requests and manage resources.
      </p>

      {/* Scheduling section */}
      <div className="mt-8 rounded-lg border bg-white p-6">
        <h2 className="text-xl font-bold">Request Scheduling</h2>

        <p className="mt-2 text-gray-600">
          Choose an algorithm to prioritize relief requests.
        </p>

        {/* Select the scheduling algorithm */}
        <label className="mt-4 block font-medium">
          Scheduling Algorithm
        </label>

        <select
          value={algorithm}
          onChange={(event) => setAlgorithm(event.target.value)}
          className="mt-2 w-full rounded border p-3"
        >
          <option value="Priority">Priority Scheduling</option>
          <option value="FCFS">First Come, First Served (FCFS)</option>
          <option value="Round Robin">Round Robin</option>
        </select>

        {/* Show scheduling results */}
        <button
          onClick={handleSchedule}
          className="mt-4 rounded bg-teal-700 px-5 py-3 text-white"
        >
          Schedule Requests
        </button>
      </div>

      {/* Display sample scheduling metrics */}
      {showResults && (
        <div className="mt-6 rounded-lg border bg-white p-6">
          <h2 className="text-xl font-bold">Scheduling Results</h2>

          <p className="mt-3">
            <strong>Selected Algorithm:</strong> {algorithm}
          </p>

          <p className="mt-3">
            <strong>Average Waiting Time:</strong> 4.5 units
          </p>

          <p className="mt-3">
            <strong>Average Response Time:</strong> 2.0 units
          </p>

          <p className="mt-3 text-sm text-gray-500">
            These are sample values for frontend demonstration.
          </p>
        </div>
      )}

      {/* Resource allocation section */}
      <div className="mt-6 rounded-lg border bg-white p-6">
        <h2 className="text-xl font-bold">Resource Allocation</h2>

        <p className="mt-2 text-gray-600">
          Enter the details of the resource to allocate.
        </p>

        {/* Form for resource allocation */}
        <form onSubmit={handleAllocation} className="mt-4 space-y-4">
          <input
            type="text"
            placeholder="Request ID"
            value={requestId}
            onChange={(event) => setRequestId(event.target.value)}
            required
            className="w-full rounded border p-3"
          />

          {/* Choose the type of resource */}
          <label className="block font-medium">Resource</label>

          <select
            value={resource}
            onChange={(event) => setResource(event.target.value)}
            className="w-full rounded border p-3"
          >
            <option value="Food">Food</option>
            <option value="Water">Water</option>
            <option value="Medical">Medical Supplies</option>
            <option value="Rescue">Rescue</option>
            <option value="Shelter">Shelter</option>
          </select>

          {/* Enter the quantity to allocate */}
          <input
            type="number"
            placeholder="Quantity"
            min="1"
            step="1"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
            required
            className="w-full rounded border p-3"
          />

          {/* Submit the allocation form */}
          <button
            type="submit"
            className="rounded bg-teal-700 px-5 py-3 text-white"
          >
            Allocate Resource
          </button>
        </form>

        {/* Display the allocation confirmation message */}
        {message && <p className="mt-4 text-teal-700">{message}</p>}
      </div>
    </div>
  );
}

export default Operations;
