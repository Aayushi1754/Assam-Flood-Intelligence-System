import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { submitReliefRequest } from "../api/floodSenseApi";

function SubmitRequest() {
  // Allow navigation to the Results page
  const navigate = useNavigate();

  // Store which input mode the user has selected
  const [mode, setMode] = useState("text");

  // Store the affected location and relief description
  const [location, setLocation] = useState("");
  const [text, setText] = useState("");

  // Store the selected image and submission message
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState("");

  // Create a reference to access the hidden file input
  const fileInputRef = useRef(null);

  // Store the URL used to display the selected image preview
  const [imagePreview, setImagePreview] = useState("");

  // Update the image preview whenever the selected image changes
  useEffect(() => {
    // Clear the preview if no image is selected
    if (!image) {
      setImagePreview("");
      return;
    }

    // Create a temporary URL for displaying the image
    const previewURL = URL.createObjectURL(image);
    setImagePreview(previewURL);

    // Release the temporary URL when the image changes
    return () => URL.revokeObjectURL(previewURL);
  }, [image]);

  // Handle submission of the relief request form
  async function handleSubmit(event) {
    // Prevent the browser from refreshing the page
    event.preventDefault();

    // Image analysis is not connected yet
    if (mode === "image") {
      setMessage("Image analysis will be added later.");
      return;
    }

    try {
      // Send the location and description to the FastAPI backend
      const result = await submitReliefRequest(location, text);

      // Open Results only when the backend confirms saving
      if (result.saved_to_database) {
        // Pass the backend response to the Results page
        navigate("/results", {
          state: { result: result },
        });
      } else {
        // Show a message if saving was not confirmed
        setMessage("Request analyzed, but saving was not confirmed.");
      }
    } catch (error) {
      // Display a friendly message if the backend connection fails
      setMessage(
        "Unable to submit your request right now. Please try again later."
      );
    }
  }

  // Handle selection of an image from the user's device
  function handleImageChange(event) {
    // Store the selected image file
    setImage(event.target.files[0] || null);

    // Clear any previous message
    setMessage("");
  }

  // Remove the selected image from the form
  function handleRemoveImage() {
    // Clear the image and its preview
    setImage(null);

    // Reset the file input so the same image can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      {/* Display the page title */}
      <h1 className="text-3xl font-bold">
        Submit a Relief Request
      </h1>

      {/* Briefly explain the purpose of the page */}
      <p className="mt-2 text-gray-600">
        Upload a flood news image or describe the relief needs.
      </p>

      {/* Let the user choose between image and text input */}
      <div className="mt-6 flex gap-4">
        {/* Button for selecting image upload mode */}
        <button
          type="button"
          onClick={() => {
            setMode("image");
            setMessage("");
          }}
          className={`rounded border p-3 ${
            mode === "image"
              ? "border-teal-700 bg-teal-100"
              : "border-gray-300"
          }`}
        >
          Upload Image
        </button>

        {/* Button for selecting text input mode */}
        <button
          type="button"
          onClick={() => {
            setMode("text");
            setMessage("");
          }}
          className={`rounded border p-3 ${
            mode === "text"
              ? "border-teal-700 bg-teal-100"
              : "border-gray-300"
          }`}
        >
          Enter Need
        </button>
      </div>

      {/* Form containing the location and input fields */}
      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        {/* Input field for the affected location */}
        <input
          type="text"
          placeholder="Affected location"
          value={location}
          onChange={(event) => setLocation(event.target.value)}
          required
          className="w-full rounded border p-3"
        />

        {/* Display the appropriate input based on the selected mode */}
        {mode === "text" ? (
          // Text area for describing the relief requirements
          <textarea
            placeholder="Describe the relief needs..."
            value={text}
            onChange={(event) => setText(event.target.value)}
            required
            maxLength={5000}
            rows={5}
            className="w-full rounded border p-3"
          />
        ) : (
          // Image upload section
          <div>
            {/* Hidden file input opened by the Choose Image button */}
            <input
              ref={fileInputRef}
              id="image-upload"
              type="file"
              accept="image/*"
              required
              onChange={handleImageChange}
              className="hidden"
            />

            {/* Display the image selection and removal buttons */}
            <div className="flex items-center gap-3">
              {/* Open the file picker to select an image */}
              <label
                htmlFor="image-upload"
                className="cursor-pointer rounded border border-teal-700 px-4 py-2 text-sm text-teal-700 hover:bg-teal-50"
              >
                Choose Image
              </label>

              {/* Show Remove Image only when an image is selected */}
              {image && (
                <button
                  type="button"
                  onClick={handleRemoveImage}
                  className="rounded border border-red-500 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  Remove Image
                </button>
              )}
            </div>

            {/* Show the selected image preview and filename */}
            {image && (
              <div className="mt-3">
                {/* Display a preview of the selected image */}
                <img
                  src={imagePreview}
                  alt="Selected flood news report"
                  className="max-h-60 rounded object-contain"
                />

                {/* Display the selected file's name */}
                <p className="mt-2 text-sm text-gray-600">
                  {image.name}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Button to submit the form */}
        <button
          type="submit"
          className="w-full rounded bg-teal-700 p-3 text-white hover:bg-teal-800"
        >
          Submit Request
        </button>
      </form>

      {/* Display success, error, or informational messages */}
      {message && (
        <p role="status" className="mt-4 text-sm">
          {message}
        </p>
      )}
    </div>
  );
}

export default SubmitRequest;
