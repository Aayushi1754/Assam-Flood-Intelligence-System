import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { submitReliefRequest } from "../api/floodSenseApi";

const API_URL = "http://127.0.0.1:8000";

function SubmitRequest() {
const navigate = useNavigate();

const [mode, setMode] = useState("text");
const [location, setLocation] = useState("");
const [text, setText] = useState("");
const [image, setImage] = useState(null);
const [message, setMessage] = useState("");
const [loading, setLoading] = useState(false);
const fileInputRef = useRef(null);
const [imagePreview, setImagePreview] = useState("");

useEffect(() => {
if (!image) {
setImagePreview("");
return;
}

const previewURL = URL.createObjectURL(image);
setImagePreview(previewURL);

return () => URL.revokeObjectURL(previewURL);

}, [image]);

async function handleSubmit(event) {
event.preventDefault();
setMessage("");
setLoading(true);

try {
  // IMAGE MODE: extract text, then analyze the extracted report.
  if (mode === "image") {
    if (!image) {
      setMessage("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("files", image);

    const ocrResponse = await fetch(
      `${API_URL}/extract-image-text`,
      {
        method: "POST",
        body: formData,
      }
    );

    const ocrData = await ocrResponse.json();

    if (!ocrResponse.ok) {
      throw new Error(
        ocrData.detail || "Unable to extract text from the image."
      );
    }

    const extractedResult = ocrData.results?.find(
      (item) => item.success && item.text?.trim()
    );

    if (!extractedResult) {
      setMessage("No readable text was found. Try a clearer image.");
      return;
    }

    // Display the extracted text in the form.
    setText(extractedResult.text);

    // Send the extracted text to the bulk-analysis endpoint.
    const analysisResponse = await fetch(
      `${API_URL}/analyze-flood-bulk`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: [
            {
              text: extractedResult.text,
              location: location.trim(),
            },
          ],
        }),
      }
    );

    const analysisData = await analysisResponse.json();

    if (!analysisResponse.ok) {
      throw new Error(
        analysisData.detail || "Flood report analysis failed."
      );
    }

    const result = analysisData.results?.[0];

    if (!result) {
      throw new Error("The backend returned no analysis result.");
    }

    if (!result.saved_to_database) {
      throw new Error(
        result.error || "The report could not be saved to the database."
      );
    }

    // Open the Results page with the analysis returned by FastAPI.
    navigate("/results", {
      state: {
        result: {
          ...result,
          extracted_text: extractedResult.text,
          filename: image.name,
        },
      },
    });

    return;
  }

  // TEXT MODE: keep your existing text submission flow.
  if (!text.trim()) {
    setMessage("Please describe the relief needs.");
    return;
  }

  const result = await submitReliefRequest(location, text);

  if (result.saved_to_database) {
    navigate("/results", {
      state: { result },
    });
  } else {
    setMessage("Request analyzed, but saving was not confirmed.");
  }
} catch (error) {
  setMessage(
    error.message ||
      "Unable to submit your request right now. Please try again."
  );
} finally {
  setLoading(false);
}

}

function handleImageChange(event) {
const selectedImage = event.target.files?.[0] || null;
setImage(selectedImage);
setMessage("");
}

function handleRemoveImage() {
setImage(null);

if (fileInputRef.current) {
  fileInputRef.current.value = "";
}

}

return (
<div className="mx-auto max-w-2xl p-8">
<h1 className="text-3xl font-bold">
Submit a Relief Request
</h1>

  <p className="mt-2 text-gray-600">
    Upload a flood news image or describe the relief needs.
  </p>

  <div className="mt-6 flex gap-4">
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

  <form onSubmit={handleSubmit} className="mt-6 space-y-4">
    <input
      type="text"
      placeholder="Affected location"
      value={location}
      onChange={(event) => setLocation(event.target.value)}
      required
      className="w-full rounded border p-3"
    />

    {mode === "text" ? (
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
      <div>
        <input
          ref={fileInputRef}
          id="image-upload"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          required
          onChange={handleImageChange}
          className="hidden"
        />

        <div className="flex items-center gap-3">
          <label
            htmlFor="image-upload"
            className="cursor-pointer rounded border border-teal-700 px-4 py-2 text-sm text-teal-700 hover:bg-teal-50"
          >
            Choose Image
          </label>

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

        {image && (
          <div className="mt-3">
            <img
              src={imagePreview}
              alt="Selected flood news report"
              className="max-h-60 rounded object-contain"
            />

            <p className="mt-2 text-sm text-gray-600">
              {image.name}
            </p>
          </div>
        )}
      </div>
    )}

    <button
      type="submit"
      disabled={loading}
      className="w-full rounded bg-teal-700 p-3 text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-60"
    >
      {loading
        ? mode === "image"
          ? "Extracting text and analyzing..."
          : "Submitting..."
        : "Submit Request"}
    </button>
  </form>

  {message && (
    <p role="status" className="mt-4 text-sm text-red-600">
      {message}
    </p>
  )}

  {mode === "image" && text && (
    <div className="mt-6 rounded border bg-white p-4">
      <h2 className="font-semibold">Extracted Text</h2>
      <p className="mt-2 whitespace-pre-wrap text-gray-700">
        {text}
      </p>
    </div>
  )}
</div>

);
}

export default SubmitRequest;