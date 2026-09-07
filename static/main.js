console.log("✅ main.js loaded");
// Chooses the correct WebSocket protocol depending on the page type (http / https)
const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws"; 
const wsHost = window.location.host; // Retrieves the current host (e.g., localhost:8000)
const app = document.getElementById("app"); // Retrieves the main container where HTML pages will be injected
let ws = new WebSocket(`${wsProtocol}://${wsHost}/ws`); // Opens the WebSocket connection with the Python backend
let pendingQuestion = null;
let pendingStats = null;
// This function is called for each message received from the server
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  const { type, payload } = msg;

  switch (type) {
    case "change_page": // The server requests a page change
      loadFragment(payload); //
      break;
    
    case "ui_update": // The server requests a UI update
      updateUI(payload);
      break;
    case "set_buttons":
      setButtons(payload);
      break;
    case "question":
      if (document.getElementById("prompt-area")) {
        renderQuestion(payload);
      } else {
        pendingQuestion = payload;
      }
      break;
    case "show_stats":
      if (document.getElementById("stat-total-time")) {
        renderStats(payload);
      } else {
        pendingStats = payload;
      }
      break;

    default:
      console.warn("Unknown message type:", type);
  }
};

// Updates the display based on the data sent by the server
// Core display function: EVERYTHING the player sees on screen goes through here
function updateUI(dict) {
  for (const [id, [text, visible]] of Object.entries(dict)) { // Iterates over all received values

    if (id === "change") {
      const el = document.getElementById(id);
      if (!el) continue;

      if (visible !== undefined) { // The server decides whether the button is visible
        const row = el.closest('div') || el;
        if (visible) row.classList.remove('hidden');
        else row.classList.add('hidden');
      }
      continue;
    }

    const el = document.getElementById(id); // Finds the HTML element corresponding to the id
    if (!el) continue;

    if (id === "status") { // Special case: game status (timer)
      el.textContent = text;

      const match = text.match(/(\d+)\s*seconds?/);  // Looks for a number of seconds in the text

      if (match) {
        const seconds = parseInt(match[1], 10);

        if (seconds <= 10) {
          el.classList.add("timer-urgent");

          if (audioUnlocked && !ticTacPlaying) { // Starts the sound if allowed
            ticTacSound.currentTime = 0;
            ticTacSound.play().catch(() => {});
            ticTacPlaying = true;
          }

        } else {
          el.classList.remove("timer-urgent");

          if (ticTacPlaying) {
            ticTacSound.pause();
            ticTacSound.currentTime = 0;
            ticTacPlaying = false;
          }
        }

      } else {
        el.classList.remove("timer-urgent");

        if (ticTacPlaying) {
          ticTacSound.pause();
          ticTacSound.currentTime = 0;
          ticTacPlaying = false;
        }
      }

    } else {
      const safeText = // General case: simple text display
        text === null || text === "null" || text === undefined
          ? ""
          : String(text);

      if (id === "candidate") { // The candidate is displayed without animation
        el.textContent = safeText;
      } else {
        if (el.textContent !== safeText && safeText !== "") { // Animation only if the value changes
          scrambleText(el, safeText);
        } else {
          el.textContent = safeText;
        }
      }
    }

    const row = el.closest('div') || el; // Manages visibility (show / hide)
    if (visible !== undefined) {
      if (visible) row.classList.remove('hidden');
      else row.classList.add('hidden');
    }
  }
}

// Sends an action (button click) to the server
function button_click(page, button, payload) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      page: page,
      button: button,
      message: payload
    }));
  } else {
    console.warn("WebSocket non connecté — action ignorée");
  }
}

// Loads an HTML file and inserts it into #app (page change)
async function loadFragment(name) {
  try {
    const response = await fetch(`./fragments/${name}.html`);
    if (!response.ok) throw new Error("Fragment introuvable");
    const html = await response.text();
    app.innerHTML = html;

    if (pendingQuestion) {
      renderQuestion(pendingQuestion);
      pendingQuestion = null;
    }
    if (pendingStats) {
      renderStats(pendingStats);
      pendingStats = null;
    }
  } catch (err) {
    app.innerHTML = `<p style="color:red;text-align:center;">Erreur de chargement : ${err.message}</p>`;
  }
}

// Listens to every click on the page
document.addEventListener("click", (e) => {
  const btn = e.target; // Clicked element
  if (!btn.classList.contains("toggle") && !btn.classList.contains("value-toggle")) return; // Only handle toggle-type buttons

  let value = btn.dataset.value === "true"; // Read the current value (true / false)
  value = !value;
  btn.dataset.value = value;

  if (btn.classList.contains("value-toggle")) { // Update the text displayed on the button
    btn.textContent = value ? "Enabled" : "Disabled";
  } else {
    btn.textContent = value ? "Visible" : "Invisible";
  }

  btn.style.background = value ? "white" : "black"; // Visual update of the button (user feedback)
  btn.style.color = value ? "black" : "white";
});
let wordStates = [];   // [{ japanese, german, selected }, ...]
let currentPage = 0;
const PAGE_SIZE = 25;

function setButtons(data) {
    wordStates = data.map(w => ({ japanese: w.japanese, german: w.german, selected: false }));
    currentPage = 0;
    renderPage();
}

function renderPage() {
  const container = document.getElementById("word-buttons");
  if (!container) return;

  const start = currentPage * PAGE_SIZE;
  const slice = wordStates.slice(start, start + PAGE_SIZE);
  const maxPage = Math.ceil(wordStates.length / PAGE_SIZE);

  // page buttons instead of prev/next
  const nav = document.getElementById("page-nav");
  if (nav) {
    nav.innerHTML = "";
    for (let i = 0; i < maxPage; i++) {
      const btn = document.createElement("button");
      btn.textContent = i + 1;
      if (i === currentPage) btn.classList.add("selected");
      btn.onclick = () => { currentPage = i; renderPage(); };
      nav.appendChild(btn);
    }
  }

  // select all button
  const selectAllBtn = document.querySelector("button[onclick='handleSelectAll()']");
  if (selectAllBtn) {
    const allSelected = slice.every(w => w.selected);
    selectAllBtn.textContent = allSelected ? "deselect all" : "select all";
  }

  container.innerHTML = "";
  slice.forEach((item, localIndex) => {
    const globalIndex = start + localIndex;
    const card = document.createElement("div");
    card.className = "word-card" + (item.selected ? " selected" : "");
    card.innerHTML = `<span class="jp">${item.japanese}</span><span class="de">${item.german}</span>`;
    card.onclick = () => toggleWord(globalIndex, card);
    container.appendChild(card);
  });
}
S
function toggleWord(globalIndex, card) {
    wordStates[globalIndex].selected = !wordStates[globalIndex].selected;
    card.classList.toggle("selected");

    // update select all button label after toggle
    const start = currentPage * PAGE_SIZE;
    const slice = wordStates.slice(start, start + PAGE_SIZE);
    const selectAllBtn = document.querySelector("button[onclick='handleSelectAll()']");
    if (selectAllBtn) {
        const allSelected = slice.every(w => w.selected);
        selectAllBtn.textContent = allSelected ? "deselect all" : "select all";
    }
}

function handleSelectAll() {
    const start = currentPage * PAGE_SIZE;
    const slice = wordStates.slice(start, start + PAGE_SIZE);
    const allSelected = slice.every(w => w.selected);
    slice.forEach((_, i) => {
        wordStates[start + i].selected = !allSelected;
    });
    renderPage();
}

function handleNav(direction) {
    const maxPage = Math.ceil(wordStates.length / PAGE_SIZE) - 1;
    if (direction === 'next' && currentPage < maxPage) currentPage++;
    if (direction === 'prev' && currentPage > 0) currentPage--;
    renderPage();
}

function handleStart() {
    const selected = wordStates
        .map((w, i) => w.selected ? i : null)
        .filter(i => i !== null);
    button_click('word_selection', 'start', selected);
}


// ── Question renderer (all modes) ─────────────────────────────────

function renderQuestion(data) {
  const prompt = document.getElementById("prompt-area");
  const container = document.getElementById("answer-buttons");
  if (!prompt || !container) return;

  prompt.innerHTML = "";
  container.innerHTML = "";

  // image sizing: 20vw on desktop, 100% on mobile
  const imgStyle = "width:min(20vw, 100%); object-fit:contain; cursor:pointer; border-radius:8px; display:block;";

  if (data.mode === "japanese") {
    prompt.innerHTML = `<span style="font-size:3rem;">${data.japanese}</span>`;
    data.buttons.forEach(btn => {
      const el = document.createElement("button");
      el.textContent = btn.german;
      el.onclick = () => button_click('learning', 'answer', btn.correct);
      container.appendChild(el);
    });

  } else if (data.mode === "marines_image") {
    prompt.innerHTML = `<span style="font-size:2rem;">${data.word.replaceAll("_", " ")}</span>`;
    container.style.flexDirection = "row";
    container.style.flexWrap = "wrap";
    data.choices.forEach(choice => {
      const el = document.createElement("img");
      el.src = choice.path;
      el.style.cssText = imgStyle;
      el.onclick = () => button_click('learning', 'answer', choice.correct);
      container.appendChild(el);
    });

  } else if (data.mode === "marines_word") {
    prompt.innerHTML = `<img src="${data.image}" style="${imgStyle} cursor:default;">`;
    data.buttons.forEach(btn => {
      const el = document.createElement("button");
      el.textContent = btn.name.replaceAll("_", " ");
      el.style.whiteSpace = "normal";
      el.onclick = () => button_click('learning', 'answer', btn.correct);
      container.appendChild(el);
    });

  } else if (data.mode === "marines_odd") {
    prompt.innerHTML = `<span style="font-size:1.5rem;">Find the one that is <strong>not</strong> in: <em>${data.category}</em></span>`;
    container.style.flexDirection = "row";
    container.style.flexWrap = "wrap";
    data.buttons.forEach(btn => {
      const wrapper = document.createElement("div");
      wrapper.style.cssText = "display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;";
      const el = document.createElement("img");
      el.src = btn.path;
      el.style.cssText = imgStyle;
      const label = document.createElement("span");
      label.textContent = btn.name.replaceAll("_", " ");
      label.style.cssText = "font-size:0.75rem;text-align:center;white-space:normal;word-break:break-word;";
      wrapper.appendChild(el);
      wrapper.appendChild(label);
      wrapper.onclick = () => button_click('learning', 'answer', btn.correct);
      container.appendChild(wrapper);
    });

  } else if (data.mode === "marines_category") {
    prompt.innerHTML = `<img src="${data.image}" style="${imgStyle} cursor:default;"><span style="font-size:1rem;margin-top:8px;">${data.name.replaceAll("_", " ")}</span>`;
    prompt.style.flexDirection = "column";
    data.buttons.forEach(btn => {
      const el = document.createElement("button");
      el.textContent = btn.category.replaceAll("_", " ");
      el.style.whiteSpace = "normal";
      el.onclick = () => button_click('learning', 'answer', btn.correct);
      container.appendChild(el);
    });
  }

  renderLastWord(data.last_word, data.mode);
}

function renderLastWord(last, mode) {
  const label = document.getElementById("last-label");
  const answer = document.getElementById("last-answer");
  if (!label || !answer) return;

  if (!last) {
    label.textContent = "";
    answer.textContent = "";
    return;
  }

  if (mode === "japanese") {
    label.textContent = last.japanese;
    answer.textContent = last.german;
  } else if (mode === "marines_category") {
    label.textContent = last.name;
    answer.textContent = last.category.replaceAll("_", " ");
  } else {
    label.textContent = "";
    answer.textContent = last.name.replaceAll("_", " ");
  }
  answer.style.color = last.correct ? "green" : "red";
}

// ── Stats renderer ────────────────────────────────────────────────



function renderStats(data) {
  const totalTime = document.getElementById("stat-total-time");
  const accuracy = document.getElementById("stat-accuracy");
  const fastest = document.getElementById("stat-fastest");
  const slowest = document.getElementById("stat-slowest");
  const rows = document.getElementById("stat-rows");

  if (!totalTime) { pendingStats = data; return; }

  totalTime.textContent = `${data.total_time}s`;
  accuracy.textContent = `${data.accuracy}%`;
  fastest.textContent = data.fastest ? `${data.fastest.word} (${data.fastest.time}s)` : "-";
  slowest.textContent = data.slowest ? `${data.slowest.word} (${data.slowest.time}s)` : "-";

  rows.innerHTML = "<strong>Word</strong><strong>Wrong</strong><strong>Time</strong>";
  data.rows.forEach(r => {
    rows.innerHTML += `<span>${r.word}</span><span style="color:${r.wrong > 0 ? 'red' : 'green'}">${r.wrong}</span><span>${r.time}s</span>`;
  });
}

// add to ws.onmessage switch:
// case "show_stats":
//   renderStats(payload);
//   break;