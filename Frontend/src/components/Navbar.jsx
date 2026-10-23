import { Link } from "react-router-dom";

function Navbar() {
  return (
    // Navigation bar at the top of the website
    <nav className="flex items-center justify-between bg-white px-6 py-4 shadow">
      {/* Website name links to Home */}
      <Link to="/" className="text-2xl font-bold text-teal-700">
        FloodSense
      </Link>

      {/* Links to the different pages */}
      <div className="flex gap-6">
        <Link to="/">Home</Link>
        <Link to="/submit-request">Submit Request</Link>
        <Link to="/results">Results</Link>
        <Link to="/operations">Operations</Link>
      </div>
    </nav>
  );
}

export default Navbar;
