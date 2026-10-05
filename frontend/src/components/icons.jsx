const base = {
    width: 18,
    height: 18,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
};

export const PlusIcon = () => (
    <svg {...base}><path d="M12 5v14M5 12h14" /></svg>
);

export const TrashIcon = () => (
    <svg {...base} width={16} height={16}>
        <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" />
    </svg>
);

export const MenuIcon = () => (
    <svg {...base}><path d="M4 6h16M4 12h16M4 18h16" /></svg>
);

export const ArrowUpIcon = () => (
    <svg {...base}><path d="M12 19V5M5 12l7-7 7 7" /></svg>
);

export const FileIcon = () => (
    <svg {...base} width={14} height={14}>
        <path d="M14 3H6a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V8z" />
        <path d="M14 3v5h5" />
    </svg>
);