import { useState } from "react";
import axios from "axios";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [readme, setReadme] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchReadme = async () => {
    setLoading(true);
    setError("");
    setReadme("");
  
    try {
      const response = await axios.get(`http://127.0.0.1:8000/scrape`, {
        params: { repo_url: repoUrl },
      });
      setReadme(response.data.readme);
    } catch (error) {
      console.error("Error fetching README:", error);
      setError(error.response?.data?.detail || "Failed to fetch README. Ensure the URL is correct.");
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-4">GitHub Scraper</h1>
      <input
        type="text"
        placeholder="Enter GitHub repository URL"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        className="border p-2 rounded w-80 mb-2"
      />
      <button
        onClick={fetchReadme}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        disabled={loading}
      >
        {loading ? "Fetching..." : "Generate README"}
      </button>

      {error && <p className="text-red-500 mt-4">{error}</p>}

      {readme && (
        <div className="bg-white p-4 mt-4 w-full max-w-2xl rounded shadow">
          <h2 className="text-lg font-bold mb-2">Generated README:</h2>
          <pre className="whitespace-pre-wrap">{readme}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
