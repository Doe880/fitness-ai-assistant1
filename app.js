const API_URL = "https://fitness-ai-assistant1.onrender.com/ask";

const form = document.getElementById("ask-form");
const input = document.getElementById("query-input");
const statusEl = document.getElementById("status");
const chatEl = document.getElementById("chat");
const exampleButtons = document.querySelectorAll(".example-btn");

let history = [];

function addMessage(role, text, sources = []) {
  const div = document.createElement("div");
  div.className = `message ${role}`;

  div.textContent = text;

  if (role === "assistant" && sources.length > 0) {
    const sourcesEl = document.createElement("div");
    sourcesEl.className = "sources";

    sourcesEl.innerHTML =
      "<strong>Источники:</strong><br>" +
      sources
        .map((source) => {
          return `ID ${source.id}: ${source.title} (${source.category}, score ${source.score})`;
        })
        .join("<br>");

    div.appendChild(sourcesEl);
  }

  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function askQuestion(query) {
  const button = form.querySelector("button");

  addMessage("user", query);

  history.push({
    role: "user",
    content: query
  });

  statusEl.textContent = "Ассистент ищет ответ...";
  button.disabled = true;
  input.value = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query,
        history: history.slice(-8)
      })
    });

    let data;

    try {
      data = await response.json();
    } catch {
      data = { detail: await response.text() };
    }

    if (!response.ok) {
      throw new Error(data.detail || `Ошибка сервера: ${response.status}`);
    }

    addMessage("assistant", data.answer, data.sources || []);

    history.push({
      role: "assistant",
      content: data.answer
    });

    statusEl.textContent = "";
  } catch (error) {
    console.error(error);
    statusEl.textContent = "Ошибка: " + error.message;
  } finally {
    button.disabled = false;
  }
}

form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const query = input.value.trim();
  if (!query) return;

  await askQuestion(query);
});

exampleButtons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    const query = btn.dataset.query;
    await askQuestion(query);
  });
});