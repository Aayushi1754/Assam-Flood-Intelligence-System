import { useNavigate } from "react-router-dom";

function Home() {
  // Used to open other pages
  const navigate = useNavigate();

  return (
    <div>
      {/* Home page banner with flood background.pic that is there in public folder.down mt means margin like did in css,margin and padding concept.*/}
      <section
        className="min-h-[450px] bg-cover bg-center p-12 text-white"   /*Adds padding (inner space) (-p-12) on all four sides.450px is min height*/
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('/assam-flood.jpg')",
        }}
      >
        <h1 className="text-5xl font-bold">FloodSense</h1> 

        <p className="mt-5 max-w-xl leading-8">    
          An intelligent flood-relief management system that
          identifies urgent needs, analyzes relief requests,
          and helps organize resources for flood-affected
          communities in Assam.
        </p>

        {/* Navigate to the request form. */}
        <button
          onClick={() => navigate("/submit-request")}
          className="mt-6 rounded bg-teal-600 px-6 py-3 text-white"
        >
          Get Started  
        </button>
      </section>

      {/* Explain the three main features */}
      <section className="bg-gray-50 p-10">
        <h2 className="text-center text-3xl font-bold">
          How FloodSense Works
        </h2>

        <div className="mx-auto mt-8 grid max-w-5xl gap-6 md:grid-cols-3">

          {/* Feature 1 */}
          <div className="rounded bg-white p-6 shadow">
            <h3 className="text-xl font-bold">Submit Request</h3>
            <p className="mt-3 text-gray-600">
              Enter the location and describe the relief needs.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="rounded bg-white p-6 shadow">
            <h3 className="text-xl font-bold">Analyze Needs</h3>
            <p className="mt-3 text-gray-600">
              Extract important keywords and identify urgency.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="rounded bg-white p-6 shadow">
            <h3 className="text-xl font-bold">Manage Resources</h3>
            <p className="mt-3 text-gray-600">
              Organize requests using scheduling algorithms.
            </p>
          </div>

        </div>
      </section>
    </div>
  );
}

export default Home;  // baad mein to use in other files
// px- horizontal padding   py- vertical padding.Similarly mx and my.rounded- to give slight curve to sides.