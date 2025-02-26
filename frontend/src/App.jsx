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
      setError(
        error.response?.data?.detail || "Failed to fetch README. Ensure the URL is correct."
      );
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(readme);
    alert("README copied to clipboard!");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white flex flex-col items-center justify-center px-4">
      <div className="bg-gray-950 shadow-lg rounded-lg p-8 max-w-2xl w-full text-center">
        <h1 className="text-3xl font-bold mb-4 text-blue-400">GitHub README Generator</h1>
        <p className="text-gray-400 mb-6">Enter a GitHub repository URL to generate a README.</p>

        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            placeholder="https://github.com/user/repository"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            className="flex-1 px-4 py-2 text-white rounded-md border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            onClick={fetchReadme}
            className="bg-blue-500 hover:bg-blue-600 text-white font-bold px-6 py-2 rounded-md transition disabled:bg-gray-600"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate"}
          </button>
        </div>

        {error && <p className="text-red-400 mt-4">{error}</p>}

        {readme && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold text-blue-400 mb-2 text-left">Generated README:</h2>
            <textarea
              value={readme}
              onChange={(e) => setReadme(e.target.value)}
              className="w-full h-64 p-4 bg-gray-800 rounded-md border border-gray-700 text-gray-300 resize-none focus:outline-none focus:ring-2 focus:ring-blue-400"
            ></textarea>
            <button
              onClick={copyToClipboard}
              className="mt-4 bg-green-500 hover:bg-green-600 text-white font-bold px-6 py-2 rounded-md transition"
            >
              Copy to Clipboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
