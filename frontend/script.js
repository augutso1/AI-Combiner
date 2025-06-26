document.getElementById("generateBtn").addEventListener("click", async function() {
    const prompt = document.getElementById("prompt").value;
    const modelSelect = document.getElementById("model");
    const responseElement = document.getElementById("response");
    const loadingElement = document.getElementById("loading");

    const selectedModels = Array.from(modelSelect.selectedOptions).map(option => option.value);

    if (!prompt.trim()) {
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
        // Envie o prompt e os modelos selecionados para o backend
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                query: prompt,
                models: selectedModels
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Como o backend faz streaming, precisamos ler o corpo como texto
        const reader = response.body.getReader();
        let result = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            result += new TextDecoder().decode(value);
        }
        responseElement.innerText = result;
    } catch (error) {
        console.error("Fetch error:", error);
        responseElement.innerText = "Error fetching response: " + error.message;
    }

    loadingElement.classList.add("hidden");
});

window.addEventListener("DOMContentLoaded", async function() {
    const modelSelect = document.getElementById("model");
    const res = await fetch("/models");
    const data = await res.json();
    data.models.forEach(model => {
        const option = document.createElement("option");
        option.value = model;
        option.text = model;
        modelSelect.appendChild(option);
    });
});