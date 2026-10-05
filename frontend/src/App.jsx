// import { useEffect, useState } from "react";
// import { askRepository, indexRepository } from "./services/api";

// const GITHUB_URL_PATTERN = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;

// const EXAMPLE_QUESTIONS = [
//     "What does this repository do?",
//     "Where is authentication implemented?",
//     "Where are API routes defined?",
//     "How is error handling implemented?",
// ];

// function StatusBadge({ status }) {
//     const styles = {
//         READY: "bg-emerald-50 text-emerald-800 ring-emerald-600/20",
//         PENDING: "bg-amber-50 text-amber-800 ring-amber-600/20",
//         FAILED: "bg-red-50 text-red-800 ring-red-600/20",
//     };
//     const dots = {
//         READY: "bg-emerald-500",
//         PENDING: "bg-amber-500 animate-pulse",
//         FAILED: "bg-red-500",
//     };
//     const labels = {
//         READY: "Ready for questions",
//         PENDING: "Indexing",
//         FAILED: "Indexing failed",
//     };

//     return (
//         <span
//             className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm ring-1 ring-inset ${styles[status] ?? styles.PENDING}`}
//         >
//             <span className={`h-2 w-2 rounded-full ${dots[status] ?? dots.PENDING}`} />
//             {labels[status] ?? status}
//         </span>
//     );
// }

// function SourceRow({ source, repoUrl }) {
//     const { file_path, start_line, end_line, score } = source;
//     // Link straight to the lines on GitHub (default branch)
//     const href = repoUrl
//         ? `${repoUrl.replace(/\/$/, "")}/blob/HEAD/${file_path}#L${start_line}-L${end_line}`
//         : null;

//     const content = (
//         <>
//             <span className="font-mono text-sm text-slate-900 break-all">
//                 {file_path}
//             </span>
//             <span className="ml-auto shrink-0 text-sm text-slate-500 tabular-nums">
//                 Lines {start_line}–{end_line}
//             </span>
//             {typeof score === "number" && (
//                 <span className="shrink-0 w-12 text-right text-xs text-slate-400 tabular-nums">
//                     {score.toFixed(2)}
//                 </span>
//             )}
//         </>
//     );

//     const rowClass =
//         "flex items-center gap-4 px-4 py-3 border-t border-slate-200 first:border-t-0";

//     return href ? (
//         <a
//             href={href}
//             target="_blank"
//             rel="noreferrer"
//             className={`${rowClass} hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-blue-700`}
//         >
//             {content}
//         </a>
//     ) : (
//         <div className={rowClass}>{content}</div>
//     );
// }

// function App() {
//     const [githubUrl, setGithubUrl] = useState("");
//     const [repository, setRepository] = useState(null);
//     const [indexing, setIndexing] = useState(false);
//     const [indexSeconds, setIndexSeconds] = useState(0);

//     const [question, setQuestion] = useState("");
//     const [answer, setAnswer] = useState(null);
//     const [sources, setSources] = useState([]);
//     const [loading, setLoading] = useState(false);

//     const [error, setError] = useState(null);

//     const repositoryId = repository?.id ?? null;
//     const repositoryStatus = repository?.status?.toUpperCase() ?? null;
//     const isReady = repositoryStatus === "READY";

//     // Indexing is synchronous on the backend, so show elapsed time
//     useEffect(() => {
//         if (!indexing) return;
//         setIndexSeconds(0);
//         const timer = setInterval(() => setIndexSeconds((s) => s + 1), 1000);
//         return () => clearInterval(timer);
//     }, [indexing]);

//     async function handleIndex(e) {
//         e.preventDefault();
//         const url = githubUrl.trim();

//         if (!GITHUB_URL_PATTERN.test(url)) {
//             setError("Enter a URL like https://github.com/psf/requests");
//             return;
//         }

//         setError(null);
//         setIndexing(true);
//         setRepository(null);
//         setAnswer(null);
//         setSources([]);

//         try {
//             const repo = await indexRepository(url);
//             setRepository(repo);
//             if (repo.status === "FAILED") {
//                 setError("The repository was cloned but indexing failed. Check the backend logs.");
//             }
//         } catch (err) {
//             setError(err.message);
//         } finally {
//             setIndexing(false);
//         }
//     }

//     async function handleAsk(e) {
//         e?.preventDefault();
//         if (!question.trim() || !isReady || loading) return;

//         setError(null);
//         setLoading(true);
//         setAnswer(null);
//         setSources([]);

//         try {
//             const response = await askRepository(repositoryId, question.trim());
//             setAnswer(response.answer);
//             setSources(response.sources ?? []);
//         } catch (err) {
//             setError(err.message);
//         } finally {
//             setLoading(false);
//         }
//     }

//     function handleQuestionKeyDown(e) {
//         // Enter asks, Shift+Enter adds a new line
//         if (e.key === "Enter" && !e.shiftKey) {
//             e.preventDefault();
//             handleAsk();
//         }
//     }

//     return (
//         <div className="min-h-screen bg-slate-50 text-slate-900">
//             <main className="mx-auto max-w-3xl px-6 py-16">
//                 <header className="mb-12">
//                     <h1 className="text-4xl font-semibold tracking-tight">
//                         RepoMind AI
//                     </h1>
//                     <p className="mt-2 text-lg text-slate-600">
//                         Ask questions about any GitHub repository and get answers
//                         with the exact files and lines they come from.
//                     </p>
//                 </header>

//                 {/* Step 1: index */}
//                 <section className="rounded-xl border border-slate-200 bg-white p-6">
//                     <form onSubmit={handleIndex}>
//                         <label
//                             htmlFor="github-url"
//                             className="block text-sm font-medium text-slate-700"
//                         >
//                             GitHub repository
//                         </label>
//                         <div className="mt-2 flex flex-col gap-3 sm:flex-row">
//                             <input
//                                 id="github-url"
//                                 type="url"
//                                 value={githubUrl}
//                                 onChange={(e) => setGithubUrl(e.target.value)}
//                                 placeholder="https://github.com/psf/requests"
//                                 disabled={indexing}
//                                 className="flex-1 rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm focus:border-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-700/20 disabled:bg-slate-100"
//                             />
//                             <button
//                                 type="submit"
//                                 disabled={indexing || !githubUrl.trim()}
//                                 className="rounded-lg bg-blue-800 px-5 py-2 text-sm font-medium text-white hover:bg-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
//                             >
//                                 {indexing ? "Indexing…" : "Index repository"}
//                             </button>
//                         </div>
//                     </form>

//                     {indexing && (
//                         <p className="mt-4 text-sm text-slate-600">
//                             Cloning, chunking and embedding files. Large
//                             repositories can take a few minutes ({indexSeconds}s).
//                         </p>
//                     )}

//                     {repository && !indexing && (
//                         <div className="mt-4 flex flex-wrap items-center gap-3">
//                             <StatusBadge status={repositoryStatus} />
//                             <span className="font-mono text-sm text-slate-600">
//                                 {repository.name}
//                             </span>
//                             <span className="text-sm text-slate-400">
//                                 ID {repositoryId}
//                             </span>
//                         </div>
//                     )}
//                 </section>

//                 {error && (
//                     <div
//                         role="alert"
//                         className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
//                     >
//                         {error}
//                     </div>
//                 )}

//                 {/* Step 2: ask */}
//                 <section
//                     className={`mt-6 rounded-xl border border-slate-200 bg-white p-6 ${isReady ? "" : "opacity-60"}`}
//                 >
//                     <form onSubmit={handleAsk}>
//                         <label
//                             htmlFor="question"
//                             className="block text-sm font-medium text-slate-700"
//                         >
//                             Ask about the code
//                         </label>
//                         <textarea
//                             id="question"
//                             rows={3}
//                             value={question}
//                             onChange={(e) => setQuestion(e.target.value)}
//                             onKeyDown={handleQuestionKeyDown}
//                             disabled={!isReady || loading}
//                             placeholder={
//                                 isReady
//                                     ? "Where is authentication implemented?"
//                                     : "Index a repository first"
//                             }
//                             className="mt-2 w-full resize-y rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-700/20 disabled:bg-slate-100"
//                         />

//                         {isReady && !answer && !loading && (
//                             <div className="mt-3 flex flex-wrap gap-2">
//                                 {EXAMPLE_QUESTIONS.map((q) => (
//                                     <button
//                                         key={q}
//                                         type="button"
//                                         onClick={() => setQuestion(q)}
//                                         className="rounded-full border border-slate-300 px-3 py-1 text-sm text-slate-700 hover:border-blue-700 hover:text-blue-800"
//                                     >
//                                         {q}
//                                     </button>
//                                 ))}
//                             </div>
//                         )}

//                         <div className="mt-4 flex items-center justify-between">
//                             <span className="text-xs text-slate-400">
//                                 Enter to ask, Shift+Enter for a new line
//                             </span>
//                             <button
//                                 type="submit"
//                                 disabled={!isReady || loading || !question.trim()}
//                                 className="rounded-lg bg-blue-800 px-5 py-2 text-sm font-medium text-white hover:bg-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
//                             >
//                                 {loading ? "Thinking…" : "Ask"}
//                             </button>
//                         </div>
//                     </form>

//                     {loading && (
//                         <p className="mt-4 text-sm text-slate-600">
//                             Searching the repository and generating an answer…
//                         </p>
//                     )}
//                 </section>

//                 {/* Step 3: answer + sources */}
//                 {answer && (
//                     <section className="mt-6" aria-live="polite">
//                         <h2 className="text-sm font-medium text-slate-700">Answer</h2>
//                         <div className="mt-2 whitespace-pre-wrap leading-relaxed text-slate-800">
//                             {answer}
//                         </div>

//                         {sources.length > 0 && (
//                             <>
//                                 <h2 className="mt-8 text-sm font-medium text-slate-700">
//                                     Sources
//                                 </h2>
//                                 <div className="mt-2 overflow-hidden rounded-xl border border-slate-200 bg-white">
//                                     {sources.map((source, i) => (
//                                         <SourceRow
//                                             key={`${source.file_path}-${source.start_line}-${i}`}
//                                             source={source}
//                                             repoUrl={repository?.github_url}
//                                         />
//                                     ))}
//                                 </div>
//                             </>
//                         )}
//                     </section>
//                 )}
//             </main>
//         </div>
//     );
// }

// export default App;

import { useCallback, useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import AddRepository from "./components/AddRepository";
import ChatView from "./components/ChatView";
import { MenuIcon } from "./components/icons";
import {
    askRepository,
    deleteRepository,
    indexRepository,
    listRepositories,
} from "./services/api";

// Backend enum may serialize as "ready" or "READY"
const normalize = (repo) => ({ ...repo, status: repo.status?.toUpperCase() });

export default function App() {
    const [repositories, setRepositories] = useState([]);
    const [listError, setListError] = useState(null);
    const [selectedId, setSelectedId] = useState(null);

    // { [repositoryId]: [{ role, content, sources?, error? }] }
    const [conversations, setConversations] = useState({});
    const [askingId, setAskingId] = useState(null);

    const [indexing, setIndexing] = useState(false);
    const [indexError, setIndexError] = useState(null);

    const [sidebarOpen, setSidebarOpen] = useState(false);

    const selected = repositories.find((r) => r.id === selectedId) ?? null;

    const loadRepositories = useCallback(async () => {
        try {
            const data = await listRepositories();
            setRepositories(data.map(normalize));
            setListError(null);
        } catch (err) {
            setListError(err.message);
        }
    }, []);

    useEffect(() => {
        loadRepositories();
    }, [loadRepositories]);

    function selectRepository(id) {
        setSelectedId(id);
        setSidebarOpen(false);
    }

    function startNew() {
        setSelectedId(null);
        setIndexError(null);
        setSidebarOpen(false);
    }

    async function handleIndex(githubUrl) {
        setIndexing(true);
        setIndexError(null);

        try {
            const repo = normalize(await indexRepository(githubUrl));
            // Put it at the top of the list (replacing it if it was already there)
            setRepositories((prev) => [repo, ...prev.filter((r) => r.id !== repo.id)]);
            setSelectedId(repo.id);
        } catch (err) {
            setIndexError(err.message);
        } finally {
            setIndexing(false);
        }
    }

    function appendMessage(repositoryId, message) {
        setConversations((prev) => ({
            ...prev,
            [repositoryId]: [...(prev[repositoryId] ?? []), message],
        }));
    }

    async function handleAsk(question) {
        const repositoryId = selectedId;
        appendMessage(repositoryId, { role: "user", content: question });
        setAskingId(repositoryId);

        try {
            const response = await askRepository(repositoryId, question);
            appendMessage(repositoryId, {
                role: "assistant",
                content: response.answer,
                sources: response.sources ?? [],
            });
        } catch (err) {
            appendMessage(repositoryId, { role: "assistant", error: err.message });
        } finally {
            setAskingId(null);
        }
    }

    async function handleDelete(repo) {
        const ok = window.confirm(
            `Delete ${repo.name}? This removes its index and local clone. You can index it again later.`
        );
        if (!ok) return;

        try {
            await deleteRepository(repo.id);
            setRepositories((prev) => prev.filter((r) => r.id !== repo.id));
            setConversations((prev) => {
                const next = { ...prev };
                delete next[repo.id];
                return next;
            });
            if (selectedId === repo.id) setSelectedId(null);
        } catch (err) {
            window.alert(`Couldn't delete ${repo.name}: ${err.message}`);
        }
    }

    return (
        <div className="flex h-dvh bg-white text-slate-900">
            <Sidebar
                repositories={repositories}
                selectedId={selectedId}
                error={listError}
                open={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
                onSelect={selectRepository}
                onNew={startNew}
                onDelete={handleDelete}
            />

            <main className="flex min-w-0 flex-1 flex-col">
                <header className="flex items-center gap-3 border-b border-slate-200 px-4 py-3">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        aria-label="Open repositories"
                        className="rounded-md p-1.5 text-slate-600 hover:bg-slate-100 md:hidden"
                    >
                        <MenuIcon />
                    </button>
                    <h1 className="truncate text-sm font-medium">
                        {selected ? selected.name : "New repository"}
                    </h1>
                    {selected && (
                        <a
                            href={selected.github_url}
                            target="_blank"
                            rel="noreferrer"
                            className="ml-auto shrink-0 text-sm text-slate-500 hover:text-slate-900"
                        >
                            View on GitHub
                        </a>
                    )}
                </header>

                {selected ? (
                    <ChatView
                        key={selected.id}
                        repository={selected}
                        messages={conversations[selected.id] ?? []}
                        asking={askingId === selected.id}
                        busy={askingId !== null}
                        onAsk={handleAsk}
                        indexing={indexing}
                        onRetry={() => handleIndex(selected.github_url)}
                    />
                ) : (
                    <AddRepository
                        onIndex={handleIndex}
                        indexing={indexing}
                        error={indexError}
                    />
                )}
            </main>
        </div>
    );
}