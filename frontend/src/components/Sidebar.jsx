import { PlusIcon, TrashIcon } from "./icons";

const DOT = {
    READY: "bg-emerald-500",
    PENDING: "bg-amber-500 animate-pulse",
    FAILED: "bg-red-500",
};

function ownerOf(githubUrl) {
    try {
        return new URL(githubUrl).pathname.split("/")[1];
    } catch {
        return "";
    }
}

export default function Sidebar({
    repositories,
    selectedId,
    error,
    open,
    onClose,
    onSelect,
    onNew,
    onDelete,
}) {
    return (
        <>
            {/* Mobile backdrop */}
            {open && (
                <div
                    className="fixed inset-0 z-30 bg-slate-900/30 md:hidden"
                    onClick={onClose}
                />
            )}

            <aside
                className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-slate-50 transition-transform md:static md:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}
            >
                <div className="p-3">
                    <p className="px-2 py-2 text-lg font-semibold tracking-tight">
                        RepoMind
                    </p>
                    <button
                        onClick={onNew}
                        className="mt-1 flex w-full items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-blue-800"
                    >
                        <PlusIcon />
                        Add repository
                    </button>
                </div>

                <nav className="flex-1 overflow-y-auto px-3 pb-3">
                    <p className="px-2 pb-2 pt-3 text-xs font-medium text-slate-500">
                        Repositories
                    </p>

                    {error && (
                        <p className="px-2 text-sm text-red-700">{error}</p>
                    )}

                    {!error && repositories.length === 0 && (
                        <p className="px-2 text-sm text-slate-500">
                            Nothing indexed yet. Add a repository to start.
                        </p>
                    )}

                    <ul className="space-y-0.5">
                        {repositories.map((repo) => {
                            const active = repo.id === selectedId;
                            return (
                                <li key={repo.id} className="group relative">
                                    <button
                                        onClick={() => onSelect(repo.id)}
                                        aria-current={active ? "page" : undefined}
                                        className={`w-full rounded-lg px-2 py-2 pr-9 text-left focus-visible:outline-2 focus-visible:outline-blue-800 ${active ? "bg-slate-200/70" : "hover:bg-slate-100"}`}
                                    >
                                        <span className="flex items-center gap-2">
                                            <span
                                                className={`h-1.5 w-1.5 shrink-0 rounded-full ${DOT[repo.status] ?? DOT.PENDING}`}
                                                title={repo.status}
                                            />
                                            <span className={`truncate text-sm ${active ? "font-medium" : ""}`}>
                                                {repo.name}
                                            </span>
                                        </span>
                                        <span className="block truncate pl-3.5 text-xs text-slate-500">
                                            {ownerOf(repo.github_url)}
                                        </span>
                                    </button>
                                    <button
                                        onClick={() => onDelete(repo)}
                                        aria-label={`Delete ${repo.name}`}
                                        className="absolute right-1.5 top-1/2 -translate-y-1/2 rounded-md p-1.5 text-slate-400 opacity-0 hover:bg-slate-200 hover:text-red-700 focus:opacity-100 group-hover:opacity-100"
                                    >
                                        <TrashIcon />
                                    </button>
                                </li>
                            );
                        })}
                    </ul>
                </nav>
            </aside>
        </>
    );
}