const API_BASE = "http://localhost:8000";

async function uploadPDF() {
  const fileInput = document.getElementById("pdfFile");
  const status = document.getElementById("uploadStatus");

  if (!fileInput.files.length) {
    alert("Please select a PDF");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  status.innerText = "Uploading...";

  try {
    const res = await fetch(`${API_BASE}/upload-pdf`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Upload failed");

    status.innerText = "✅ PDF uploaded successfully";
    document.getElementById("chatBox").innerHTML = "";
  } catch (err) {
    status.innerText = "❌ Upload failed";
  }
}

async function askQuestion() {
  const input = document.getElementById("questionInput");
  const chatBox = document.getElementById("chatBox");
  const question = input.value.trim();

  if (!question) return;

  // Show user message
  chatBox.innerHTML += `
    <div class="message user">You: ${question}</div>
  `;

  input.value = "";

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });

    const data = await res.json();

    chatBox.innerHTML += `
      <div class="message bot">Bot: ${data.answer}</div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (err) {
    chatBox.innerHTML += `
      <div class="message bot">❌ Error getting response</div>
    `;
  }
}
