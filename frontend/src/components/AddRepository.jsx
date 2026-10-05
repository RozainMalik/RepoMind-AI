import { useEffect, useState } from "react";

const GITHUB_URL_PATTERN = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;

const EXAMPLES = [
    "https://github.com/psf/requests",
    "https://github.com/pallets/flask",
    "https://github.com/fastapi/fastapi",
];

export default function AddRepository({ onIndex, indexing, error }) {
    const [url, setUrl] = useState("");
    const [localError, setLocalError] = useState(null);
    const [seconds, setSeconds] = useState(0);

    // Indexing is synchronous on the backend, so show elapsed time
    useEffect(() => {
        if (!indexing) return;
        setSeconds(0);
        const timer = setInterval(() => setSeconds((s) => s + 1), 1000);
        return () => clearInterval(timer);
    }, [indexing]);

    function handleSubmit(e) {
        e.preventDefault();
        const value = url.trim();

        if (!GITHUB_URL_PATTERN.test(value)) {
            setLocalError("Enter a URL like https://github.com/psf/requests");
            return;
        }

        setLocalError(null);
        onIndex(value);
    }

    const shownError = localError ?? error;

    return (
        <div className="flex flex-1 items-center justify-center overflow-y-auto px-6 py-12">
            <div className="w-full max-w-xl">
                <h2 className="text-3xl font-semibold tracking-tight">
                    Which repository should we read?
                </h2>
                <p className="mt-3 leading-relaxed text-slate-600">
                    Paste a public GitHub URL. RepoMind clones and indexes the
                    code, then answers your questions with the files and lines
                    it used.
                </p>

                <form
                    onSubmit={handleSubmit}
                    className="mt-8 flex items-center gap-2 rounded-2xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-slate-500"
                >
                    <label htmlFor="github-url" className="sr-only">
                        GitHub repository URL
                    </label>
                    <input
                        id="github-url"
                        type="url"
                        autoFocus
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://github.com/owner/repo"
                        disabled={indexing}
                        className="min-w-0 flex-1 bg-transparent px-3 py-2 font-mono text-sm outline-none disabled:text-slate-400"
                    />
                    <button
                        type="submit"
                        disabled={indexing || !url.trim()}
                        className="shrink-0 rounded-xl bg-blue-800 px-4 py-2 text-sm font-medium text-white hover:bg-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        {indexing ? "Indexing…" : "Index repository"}
                    </button>
                </form>

                {indexing && (
                    <p className="mt-4 text-sm text-slate-600" aria-live="polite">
                        Cloning, chunking and embedding files ({seconds}s). Large
                        repositories can take a few minutes.
                    </p>
                )}

                {shownError && !indexing && (
                    <p role="alert" className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
                        {shownError}
                    </p>
                )}

                {!indexing && (
                    <div className="mt-6 flex flex-wrap gap-2">
                        {EXAMPLES.map((example) => (
                            <button
                                key={example}
                                type="button"
                                onClick={() => setUrl(example)}
                                className="rounded-full border border-slate-200 px-3 py-1 font-mono text-xs text-slate-600 hover:border-slate-400 hover:text-slate-900"
                            >
                                {example.replace("https://github.com/", "")}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}