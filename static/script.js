document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("question");
  const quickButtons = document.querySelectorAll(".quick-question");
  const reportTypeSelector = document.getElementById("reportType");

  function appendMessage(sender, text) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message");
    msgDiv.innerHTML = `<span class='${sender}'>${sender === "user" ? "You" : "Gemini"}:</span> ${text}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    const reportType = reportTypeSelector.value;

    if (!question) return;
    appendMessage("user", question);
    input.value = "";
    appendMessage("bot", "Thinking...");

    const body = { question, reportType };

    // 🔸 Add productId only for target report (optional enhancement)
    if (reportType === "target") {
      body.productId = "13";  // Set this dynamically if you add a selector later
    }

    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();
    document.querySelector(".bot:last-of-type").parentNode.remove();
    appendMessage("bot", data.response);
  });

  quickButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      input.value = btn.dataset.q;
      form.dispatchEvent(new Event("submit"));
    });
  });
});
