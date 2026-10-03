import { useState } from "react";
import { askRepository } from "./services/api";

function App() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState(null);
    const [loading, setLoading] = useState(false);

    async function handleAsk() {
        if (!question.trim()) return;

        setLoading(true);
        setAnswer(null);

        try {
            const response = await askRepository(question);
            setAnswer(response);
        } catch (error) {
            console.error(error);
            setAnswer({
                answer: "Something went wrong while processing your question."
            });
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen p-10">
            <h1 className="text-3xl font-bold mb-6">
                RepoMind AI
            </h1>

            <textarea
                className="border rounded-lg w-full p-3"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about your repository..."
            />

            <button
                onClick={handleAsk}
                disabled={loading}
                className="mt-4 bg-black text-white px-5 py-2 rounded-lg disabled:opacity-50"
            >
                {loading ? "Thinking..." : "Ask"}
            </button>

            {loading && (
                <p className="mt-4 text-gray-500">
                    🔎 Searching the repository and generating an answer...
                </p>
            )}

            {answer && (
                <div className="mt-8">
                    <h2 className="font-bold">
                        Answer
                    </h2>

                    <p className="mt-2">
                        {answer.answer}
                    </p>
                </div>
            )}
        </div>
    );
}

export default App;