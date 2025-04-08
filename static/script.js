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
        // Function to call the GROQ API for a specific model
        const callGroqAPI = async (model) => {
            const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer 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"
                },
                body: JSON.stringify({ 
                    model: model,
                    messages: [
                        { role: "system", content: "You are a helpful assistant." },
                        { role: "user", content: prompt }
                    ],
                    temperature: 0.7,
                    max_tokens: 2048
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error for model ${model}! Status: ${response.status}`);
            }

            const data = await response.json();
            return {
                model: model,
                content: data.choices[0].message.content
            };
        };

        // Call all selected models in parallel
        const modelPromises = selectedModels.map(model => callGroqAPI(model));
        const modelResponses = await Promise.all(modelPromises);

        // If there's only one model, just show its response
        if (modelResponses.length === 1) {
            responseElement.innerText = modelResponses[0].content;
        } else {
            // If multiple models, combine their responses
            // First, display each individual response
            let combinedResponse = "";
            
            modelResponses.forEach((response, index) => {
                const modelName = modelSelect.options.namedItem(response.model)?.text || response.model;
                combinedResponse += `---- ${modelName} Response ----\n\n${response.content}\n\n`;
            });
            
            // If there are multiple models, we'll also try to synthesize a combined response
            // by using one of the models to combine the responses
            if (modelResponses.length > 1) {
                try {
                    // Use the most capable model to synthesize (assuming it's the first in the list - llama-3.3-70b-versatile)
                    const synthesizingModel = "llama-3.3-70b-versatile";
                    
                    // Build a prompt for synthesizing the responses
                    let synthesisPrompt = "I've received multiple AI responses to the following query:\n\n";
                    synthesisPrompt += `QUERY: ${prompt}\n\nRESPONSES:\n\n`;
                    
                    modelResponses.forEach((response, index) => {
                        const modelName = modelSelect.options.namedItem(response.model)?.text || response.model;
                        synthesisPrompt += `RESPONSE ${index + 1} (${modelName}):\n${response.content}\n\n`;
                    });
                    
                    synthesisPrompt += "Please synthesize these responses into a single, comprehensive answer that captures the best insights from each response. If the responses contradict each other, highlight the different perspectives.";
                    
                    const synthesisResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer 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"
                        },
                        body: JSON.stringify({ 
                            model: synthesizingModel,
                            messages: [
                                { role: "system", content: "You are a helpful assistant tasked with synthesizing multiple AI responses." },
                                { role: "user", content: synthesisPrompt }
                            ],
                            temperature: 0.5,
                            max_tokens: 2048
                        })
                    });
                    
                    if (synthesisResponse.ok) {
                        const synthesisData = await synthesisResponse.json();
                        combinedResponse += `\n---- SYNTHESIZED RESPONSE ----\n\n${synthesisData.choices[0].message.content}`;
                    }
                } catch (error) {
                    console.error("Error synthesizing responses:", error);
                    combinedResponse += "\n---- SYNTHESIZED RESPONSE ----\n\nFailed to synthesize responses.";
                }
            }
            
            responseElement.innerText = combinedResponse;
        }
    } catch (error) {
        console.error("Fetch error:", error);
        responseElement.innerText = "Error fetching response: " + error.message;
    }

    loadingElement.classList.add("hidden");
});