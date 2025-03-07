document.getElementById("generateBtn").addEventListener("click", async function() {
    const prompt = document.getElementById("prompt").value;
    const modelSelect = document.getElementById("model");
    const responseElement = document.getElementById("response");
    const loadingElement = document.getElementById("loading");

    // Get selected models
    const selectedModels = Array.from(modelSelect.selectedOptions).map(option => option.value);

    if (!prompt) {
        alert("Please enter a prompt.");
        return;
    }
    if (selectedModels.length === 0) {
        alert("Please select at least one model.");
        return;
    }

    responseElement.innerText = "";
    loadingElement.classList.remove("hidden");

    try {
        const response = await fetch("http://localhost:8000/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt, models: selectedModels, api_key: "YOUR_API_KEY" })
        });

        const data = await response.json();
        responseElement.innerText = data.combined_response || "No response received.";
    } catch (error) {
        responseElement.innerText = "Error fetching response.";
    }

    loadingElement.classList.add("hidden");
});
