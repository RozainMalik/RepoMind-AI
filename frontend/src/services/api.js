const API_URL = "http://127.0.0.1:8001/api/v1";

export async function askRepository(question){

    const response = await fetch(
        `${API_URL}/chat/`,
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                question
            })
        }
    );
    return await response.json();
}

export async function indexRepository(githubUrl) {
    const response = await fetch(
        `${API_URL}/repositories`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                github_url: githubUrl
            })
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Failed to index repository");
    }

    return data;
}