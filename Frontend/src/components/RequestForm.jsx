import { useState } from "react";

// Form for entering a flood relief request
function RequestForm({ onSubmit }) {
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    // Send the entered details to the parent component
    if (onSubmit) {
      onSubmit({ location, description });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block mb-1 font-medium">
          Affected Location
        </label>
        <input
          type="text"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          placeholder="e.g. Dhemaji, Assam"
          required
          className="w-full rounded-lg border p-3"
        />
      </div>

      <div>
        <label className="block mb-1 font-medium">
          Relief Needs
        </label>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="Describe the affected families' needs"
          required
          rows={4}
          className="w-full rounded-lg border p-3"
        />
      </div>

      <button
        type="submit"
        className="rounded-lg bg-blue-600 px-5 py-2 text-white"
      >
        Submit Request
      </button>
    </form>
  );
}

export default RequestForm;
