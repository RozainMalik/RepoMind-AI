import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArrowUpIcon, FileIcon } from "./icons";

const SUGGESTIONS = [
    "What does this repository do?",
    "Where is authentication implemented?",
    "Where are API routes defined?",
    "How is error handling implemented?",
];

// Styles for rendered markdown (no typography plugin needed)
const MARKDOWN_STYLES = [
    "leading-relaxed text-slate-800",
    "[&_p]:my-3 [&_p:first-child]:mt-0",
    "[&_ul]:my-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:my-3 [&_ol]:list-decimal [&_ol]:pl-6 [&_li]:my-1",
    "[&_h1]:mt-5 [&_h1]:text-lg [&_h1]:font-semibold [&_h2]:mt-5 [&_h2]:font-semibold [&_h3]:mt-4 [&_h3]:font-semibold",
    "[&_a]:text-blue-800 [&_a]:underline",
    "[&_code]:font-mono [&_code]:text-[0.875em]",
    "[&_:not(pre)>code]:rounded [&_:not(pre)>code]:bg-slate-100 [&_:not(pre)>code]:px-1.5 [&_:not(pre)>code]:py-0.5",
    "[&_pre]:my-4 [&_pre]:overflow-x-auto [&_pre]:rounded-xl [&_pre]:bg-slate-900 [&_pre]:p-4 [&_pre]:text-slate-100",
    "[&_table]:my-4 [&_table]:w-full [&_table]:text-sm [&_th]:border-b [&_th]:border-slate-300 [&_th]:py-2 [&_th]:text-left [&_td]:border-b [&_td]:border-slate-200 [&_td]:py-2",
].join(" ");

function Sources({ sources, repoUrl }) {
    if (!sources?.length) return null;

    return (
        <div className="mt-4">
            <p className="mb-2 text-xs font-medium text-slate-500">Sources</p>
            <div className="grid gap-2 sm:grid-cols-2">
                {sources.map((s, i) => (
                    <a
                        key={`${s.file_path}-${s.start_line}-${i}`}
                        href={`${repoUrl.replace(/\/$/, "")}/blob/HEAD/${s.file_path}#L${s.start_line}-L${s.end_line}`}
                        target="_blank"
                        rel="noreferrer"
                        title={`Relevance ${s.score?.toFixed(2) ?? "–"}`}
                        className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-blue-800"
                    >
                        <span className="shrink-0 text-slate-400"><FileIcon /></span>
                        <span className="min-w-0 flex-1 truncate font-mono text-xs text-slate-800">
                            {s.file_path}
                        </span>
                        <span className="shrink-0 text-xs text-slate-500 tabular-nums">
                            L{s.start_line}–{s.end_line}
                        </span>
                    </a>
                ))}
            </div>
        </div>
    );
}

function Message({ message, repoUrl }) {
    if (message.role === "user") {
        return (
            <div className="flex justify-end">
                <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl bg-slate-100 px-4 py-2.5">
                    {message.content}
                </div>
            </div>
        );
    }

    if (message.error) {
        return (
            <p role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">
                {message.error}
            </p>
        );
    }

    return (
        <div>
            <div className={MARKDOWN_STYLES}>
                <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
            </div>
            <Sources sources={message.sources} repoUrl={repoUrl} />
        </div>
    );
}

function Thinking() {
    return (
        <div className="flex items-center gap-3 text-sm text-slate-500" aria-live="polite">
            <span className="flex gap-1">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.3s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:-0.15s]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" />
            </span>
            Searching the code and writing an answer
        </div>
    );
}

function Composer({ onSend, disabled, placeholder }) {
    const [text, setText] = useState("");
    const ref = useRef(null);

    // Grow with content up to ~8 lines
    useEffect(() => {
        const el = ref.current;
        if (!el) return;
        el.style.height = "auto";
        el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
    }, [text]);

    function send() {
        const question = text.trim();
        if (!question || disabled) return;
        onSend(question);
        setText("");
    }

    return (
        <div className="px-4 pb-4 pt-2">
            <div className="mx-auto max-w-3xl">
                <form
                    onSubmit={(e) => { e.preventDefault(); send(); }}
                    className="flex items-end gap-2 rounded-2xl border border-slate-300 bg-white p-2 shadow-sm focus-within:border-slate-500"
                >
                    <label htmlFor="question" className="sr-only">Question</label>
                    <textarea
                        id="question"
                        ref={ref}
                        rows={1}
                        autoFocus
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                                e.preventDefault();
                                send();
                            }
                        }}
                        placeholder={placeholder}
                        className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-1.5 outline-none"
                    />
                    <button
                        type="submit"
                        aria-label="Ask"
                        disabled={disabled || !text.trim()}
                        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-800 text-white hover:bg-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-800 disabled:cursor-not-allowed disabled:opacity-30"
                    >
                        <ArrowUpIcon />
                    </button>
                </form>
                <p className="mt-2 text-center text-xs text-slate-400">
                    Answers come from a local model and can be wrong. Check the sources.
                </p>
            </div>
        </div>
    );
}

export default function ChatView({
    repository,
    messages,
    asking,
    busy,
    onAsk,
    indexing,
    onRetry,
}) {
    const bottomRef = useRef(null);
    const ready = repository.status === "READY";

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages.length, asking]);

    return (
        <>
            <div className="flex-1 overflow-y-auto">
                <div className="mx-auto max-w-3xl space-y-8 px-4 py-8">
                    {!ready && (
                        <div className="rounded-xl border border-slate-200 p-6">
                            <p className="font-medium">
                                {repository.status === "FAILED"
                                    ? `Indexing ${repository.name} failed.`
                                    : `${repository.name} isn't finished indexing.`}
                            </p>
                            <p className="mt-1 text-sm text-slate-600">
                                Check the backend logs for the error, then index it again.
                            </p>
                            <button
                                onClick={onRetry}
                                disabled={indexing}
                                className="mt-4 rounded-lg bg-blue-800 px-4 py-2 text-sm font-medium text-white hover:bg-blue-900 disabled:opacity-40"
                            >
                                {indexing ? "Indexing…" : "Index again"}
                            </button>
                        </div>
                    )}

                    {ready && messages.length === 0 && (
                        <div className="pt-[12vh]">
                            <h2 className="text-2xl font-semibold tracking-tight">
                                Ask anything about {repository.name}
                            </h2>
                            <div className="mt-6 grid gap-2 sm:grid-cols-2">
                                {SUGGESTIONS.map((q) => (
                                    <button
                                        key={q}
                                        onClick={() => onAsk(q)}
                                        disabled={busy}
                                        className="rounded-xl border border-slate-200 px-4 py-3 text-left text-sm text-slate-700 hover:border-slate-400 hover:bg-slate-50 disabled:opacity-50"
                                    >
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((message, i) => (
                        <Message key={i} message={message} repoUrl={repository.github_url} />
                    ))}

                    {asking && <Thinking />}
                    <div ref={bottomRef} />
                </div>
            </div>

            {ready && (
                <Composer
                    onSend={onAsk}
                    disabled={busy}
                    placeholder={`Ask about ${repository.name}`}
                />
            )}
        </>
    );
}