const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
const chatWindow = document.getElementById("chatWindow");

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  // Display user message
  const userMsg = document.createElement("div");
  userMsg.className = "message user";
  userMsg.textContent = text;
  chatWindow.appendChild(userMsg);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  userInput.value = "";

  // Temporary bot reply
  const botMsg = document.createElement("div");
  botMsg.className = "message bot";
  botMsg.textContent = "Thinking...";
  chatWindow.appendChild(botMsg);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: text }),
    });

    const data = await response.json();
    botMsg.textContent = data.answer || "No response.";
  } catch (error) {
    botMsg.textContent = "Error contacting AI server.";
  }

  chatWindow.scrollTop = chatWindow.scrollHeight;
}
document.addEventListener("DOMContentLoaded", function () {
  const chatWindow = document.getElementById("chatWindow");

  // Add a friendly AI welcome message
  const welcomeMessage = document.createElement("div");
  welcomeMessage.classList.add("bot-message");
  welcomeMessage.innerHTML = `
    <p>👋 Hello there! I’m <strong>CyberGuard AI</strong>, your personal cybersecurity assistant.</p>
    <p>Ask me about cyber threats, code safety, or security best practices — I’m here to help!</p>
  `;

  chatWindow.appendChild(welcomeMessage);
});
