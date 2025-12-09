async function generateData() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    const selectedPgns = Array.from(checkboxes).map(cb => cb.value);
    const format = document.getElementById('format').value;
    const duration = document.getElementById('duration').value;

    if (selectedPgns.length === 0) {
        alert("Please select at least one PGN!");
        return;
    }

    const button = document.querySelector('button');
    button.innerText = "Generating...";
    button.disabled = true;

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pgns: selectedPgns, format: format, duration: duration })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `j1939_dataset.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            alert("Generation failed. Server returned error.");
        }
    } catch (error) {
        console.error(error);
        alert("An error occurred while connecting to the server.");
    }

    button.innerText = "🚀 Generate & Download";
    button.disabled = false;
}
