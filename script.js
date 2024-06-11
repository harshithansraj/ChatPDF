async function askQuestion() {
    const query = document.getElementById("query-input").value;
    const askButton = document.getElementById("ask-button");
    const buttonText = document.getElementById("button-text");
    const loadingSpinner = document.getElementById("loading-spinner");

    // Show loading spinner and disable button
    buttonText.style.display = 'none';
    loadingSpinner.style.display = 'block';
    askButton.disabled = true;

    try {
        const response = await fetch("/ask_pdf", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();
        document.getElementById("answer").innerText = data.answer;
        const sourcesList = document.getElementById("sources");
        sourcesList.innerHTML = "";
        data.sources.forEach((source) => {
            const listItem = document.createElement("li");
            listItem.innerText = source.page_content;
            sourcesList.appendChild(listItem);
        });
    } catch (error) {
        console.error("Error:", error);
    } finally {
        // Hide loading spinner and enable button
        buttonText.style.display = 'block';
        loadingSpinner.style.display = 'none';
        askButton.disabled = false;
    }
}
