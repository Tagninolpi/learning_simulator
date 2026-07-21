console.log("✅ main.js loaded");
// Chooses the correct WebSocket protocol depending on the page type (http / https)
const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws"; 
const wsHost = window.location.host; // Retrieves the current host (e.g., localhost:8000)
const app = document.getElementById("app"); // Retrieves the main container where HTML pages will be injected
let ws = new WebSocket(`${wsProtocol}://${wsHost}/ws`); // Opens the WebSocket connection with the Python backend
let pendingQuestion = null;

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
      if (document.getElementById("current-japanese")) {
          renderQuestion(payload);
      } else {
          pendingQuestion = payload;
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

    // page indicator
    const indicator = document.getElementById("page-indicator");
    if (indicator) indicator.textContent = `page ${currentPage + 1} / ${maxPage}`;

    // update select all button label
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

function renderQuestion(data) {
  // top: japanese symbol
  const jpEl = document.getElementById("current-japanese");
  if (jpEl) jpEl.textContent = data.japanese;

  // middle: 5 answer buttons
  const container = document.getElementById("answer-buttons");
  if (container) {
    container.innerHTML = "";
    data.buttons.forEach(btn => {
      const el = document.createElement("button");
      el.textContent = btn.german;
      el.onclick = () => {
        button_click('learning', 'answer', btn.correct);
      };
      container.appendChild(el);
    });
  }

  // bottom: last word result
  if (data.last_word) {
    const lastJp = document.getElementById("last-japanese");
    const lastDe = document.getElementById("last-german");
    if (lastJp) lastJp.textContent = data.last_word.japanese;
    if (lastDe) {
      lastDe.textContent = data.last_word.german;
      lastDe.style.color = data.last_word.correct ? "green" : "red";
    }
  }
}