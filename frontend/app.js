const API_URL = "http://127.0.0.1:8000/ask";
// После деплоя на Render заменить на:
// const API_URL = "https://your-render-service.onrender.com/ask";

const form = document.getElementById("ask-form");
const input = document.getElementById("query-input");
const statusEl = document.getElementById("status");
const answerEl = document.getElementById("answer");
const exampleButtons = document.querySelectorAll(".example-btn");

async function askQuestion(query) {
  const button = form.querySelector("button");

  statusEl.textContent = "Ищу ответ в базе знаний...";
  answerEl.classList.add("hidden");
  answerEl.textContent = "";
  button.disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Ошибка сервера");
    }

    statusEl.textContent = "";
    answerEl.textContent = data.answer;
    answerEl.classList.remove("hidden");
  } catch (error) {
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
    input.value = query;
    await askQuestion(query);
  });
});