const API_BASE_URL = "https://fitness-ai-assistant1.onrender.com";

const authScreen = document.getElementById("auth-screen");
const mainScreen = document.getElementById("main-screen");
const logoutBtn = document.getElementById("logout-btn");

const loginTab = document.getElementById("login-tab");
const registerTab = document.getElementById("register-tab");
const authForm = document.getElementById("auth-form");
const authSubmit = document.getElementById("auth-submit");
const authStatus = document.getElementById("auth-status");
const emailInput = document.getElementById("email-input");
const passwordInput = document.getElementById("password-input");

const navButtons = document.querySelectorAll(".nav-btn");
const screens = document.querySelectorAll(".screen");

const chatEl = document.getElementById("chat");
const askForm = document.getElementById("ask-form");
const queryInput = document.getElementById("query-input");
const chatStatus = document.getElementById("chat-status");
const exampleButtons = document.querySelectorAll(".example-btn");

const profileForm = document.getElementById("profile-form");
const goalInput = document.getElementById("goal-input");
const levelInput = document.getElementById("level-input");
const equipmentInput = document.getElementById("equipment-input");
const daysInput = document.getElementById("days-input");
const profileStatus = document.getElementById("profile-status");

const createPlanBtn = document.getElementById("create-plan-btn");
const plansList = document.getElementById("plans-list");
const plansStatus = document.getElementById("plans-status");

let authMode = "login";

function getToken() {
  return localStorage.getItem("fitness_token");
}

function setToken(token) {
  localStorage.setItem("fitness_token", token);
}

function clearToken() {
  localStorage.removeItem("fitness_token");
}

async function apiRequest(path, options = {}) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
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

  return data;
}

function showMain() {
  authScreen.classList.add("hidden");
  mainScreen.classList.remove("hidden");
  logoutBtn.classList.remove("hidden");
}

function showAuth() {
  authScreen.classList.remove("hidden");
  mainScreen.classList.add("hidden");
  logoutBtn.classList.add("hidden");
}

function setAuthMode(mode) {
  authMode = mode;

  if (mode === "login") {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
    authSubmit.textContent = "Войти";
  } else {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");
    authSubmit.textContent = "Зарегистрироваться";
  }

  authStatus.textContent = "";
}

function showScreen(screenId) {
  screens.forEach((screen) => {
    screen.classList.toggle("hidden", screen.id !== screenId);
  });

  navButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.screen === screenId);
  });

  if (screenId === "plans-screen") {
    loadPlans();
  }
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;

  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function loadHistory() {
  try {
    const messages = await apiRequest("/history");

    chatEl.innerHTML = "";

    if (messages.length === 0) {
      addMessage("assistant", "Привет! Я помогу с тренировками, питанием и программой на неделю.");
      return;
    }

    messages.forEach((message) => {
      addMessage(message.role, message.content);
    });
  } catch (error) {
    console.error(error);
  }
}

async function askQuestion(query) {
  addMessage("user", query);
  chatStatus.textContent = "Ассистент ищет ответ...";
  queryInput.value = "";

  try {
    const data = await apiRequest("/ask", {
      method: "POST",
      body: JSON.stringify({ query })
    });

    addMessage("assistant", data.answer);
    chatStatus.textContent = "";
  } catch (error) {
    console.error(error);
    chatStatus.textContent = "Ошибка: " + error.message;
  }
}

async function saveProfile(event) {
  event.preventDefault();

  profileStatus.textContent = "Сохраняю профиль...";

  try {
    await apiRequest("/profile", {
      method: "POST",
      body: JSON.stringify({
        goal: goalInput.value,
        level: levelInput.value,
        equipment: equipmentInput.value,
        days_per_week: Number(daysInput.value)
      })
    });

    profileStatus.textContent = "Профиль сохранён.";
  } catch (error) {
    profileStatus.textContent = "Ошибка: " + error.message;
  }
}

async function createWorkoutPlan() {
  plansStatus.textContent = "Создаю тренировочный план...";

  try {
    const data = await apiRequest("/workout-plan", {
      method: "POST",
      body: JSON.stringify({
        goal: goalInput.value,
        level: levelInput.value,
        equipment: equipmentInput.value,
        days_per_week: Number(daysInput.value)
      })
    });

    plansStatus.textContent = "План создан.";
    await loadPlans();
  } catch (error) {
    plansStatus.textContent = "Ошибка: " + error.message;
  }
}

async function loadPlans() {
  plansStatus.textContent = "Загружаю планы...";
  plansList.innerHTML = "";

  try {
    const plans = await apiRequest("/workout-plans");

    if (plans.length === 0) {
      plansStatus.textContent = "Планов пока нет.";
      return;
    }

    plansStatus.textContent = "";

    plans.forEach((plan) => {
      const card = document.createElement("div");
      card.className = "plan-card";

      const title = document.createElement("h3");
      title.textContent = plan.title;

      const content = document.createElement("pre");
      content.textContent = plan.content;

      card.appendChild(title);
      card.appendChild(content);
      plansList.appendChild(card);
    });
  } catch (error) {
    plansStatus.textContent = "Ошибка: " + error.message;
  }
}

async function initApp() {
  if (!getToken()) {
    showAuth();
    return;
  }

  try {
    await apiRequest("/me");
    showMain();
    await loadHistory();
  } catch {
    clearToken();
    showAuth();
  }
}

loginTab.addEventListener("click", () => setAuthMode("login"));
registerTab.addEventListener("click", () => setAuthMode("register"));

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  authStatus.textContent = "Подождите...";

  const path = authMode === "login" ? "/login" : "/register";

  try {
    const data = await apiRequest(path, {
      method: "POST",
      body: JSON.stringify({
        email: emailInput.value,
        password: passwordInput.value
      })
    });

    setToken(data.access_token);
    authStatus.textContent = "";
    showMain();
    await loadHistory();
  } catch (error) {
    authStatus.textContent = "Ошибка: " + error.message;
  }
});

logoutBtn.addEventListener("click", () => {
  clearToken();
  showAuth();
});

navButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    showScreen(btn.dataset.screen);
  });
});

askForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  if (!query) return;

  await askQuestion(query);
});

exampleButtons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    await askQuestion(btn.dataset.query);
  });
});

profileForm.addEventListener("submit", saveProfile);
createPlanBtn.addEventListener("click", createWorkoutPlan);

initApp();