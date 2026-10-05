const API_URL = "http://127.0.0.1:8001/api/v1";

async function request(path, options = {}) {
    let response;

    try {
        response = await fetch(`${API_URL}${path}`, {
            headers: { "Content-Type": "application/json" },
            ...options,
        });
    } catch {
        throw new Error(
            "Can't reach the backend at 127.0.0.1:8001. Is uvicorn running?"
        );
    }

    let data = null;
    try {
        data = await response.json();
    } catch {
        // Empty body (e.g. 204 No Content) or non-JSON
    }

    if (!response.ok) {
        const detail = Array.isArray(data?.detail)
            ? data.detail.map((d) => `${d.loc?.at(-1)}: ${d.msg}`).join(", ")
            : data?.detail;
        throw new Error(detail || `Request failed (${response.status})`);
    }

    return data;
}

export function listRepositories() {
    return request("/repositories");
}

export function indexRepository(githubUrl) {
    return request("/repositories", {
        method: "POST",
        body: JSON.stringify({ github_url: githubUrl }),
    });
}

export function deleteRepository(repositoryId) {
    return request(`/repositories/${repositoryId}`, { method: "DELETE" });
}

export function askRepository(repositoryId, question) {
    return request("/chat/", {
        method: "POST",
        body: JSON.stringify({
            repository_id: repositoryId,
            question,
        }),
    });
}