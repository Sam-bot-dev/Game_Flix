document.addEventListener("DOMContentLoaded", () => {
  initHome();
});

async function initHome() {
  try {
    await Promise.all([
      loadTrending(),
      loadNewReleases(),
      loadRecommended()
    ]);
  } catch (err) {
    console.error("Error initializing home:", err);
  }
}

function buildCardHTML(game) {
  const genres = game.genres?.join(", ") || "";
  const cover = game.cover || "/static/placeholder-game.png";
  const title = escapeHtml(game.title || game.name || "Untitled");

  // Use data-name for dynamic navigation
  return `
    <div class="group relative aspect-[3/4] w-52 shrink-0 snap-start overflow-hidden rounded-lg 
    transition-transform duration-300 ease-in-out hover:scale-105 hover:z-10 cursor-pointer" 
    data-name="${encodeURIComponent(title)}">
      
      <img class="h-full w-full object-cover" src="${cover}" 
      alt="${title}" onerror="this.src='/static/placeholder-game.png'"/>
      
      <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
      
      <div class="absolute bottom-0 left-0 right-0 p-3">
        <h4 class="font-bold text-white truncate">${title}</h4>
        <p class="text-xs text-gray-300 truncate">${genres}</p>
      </div>
    </div>
  `;
}

// ------------------ Trending ------------------
async function loadTrending() {
  const container = document.getElementById("trending-row");
  if (!container) return;
  container.innerHTML = loadingPlaceholder(6);

  try {
    const res = await fetch("/api/games/trending");
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    container.innerHTML = data.results.map(buildCardHTML).join("");
    attachCardClicks(container);

  } catch (err) {
    console.error("Trending error:", err);
    container.innerHTML = `<div class="p-4 text-gray-400">Failed to load trending games.</div>`;
  }
}

// ------------------ New Releases ------------------
async function loadNewReleases() {
  const container = document.getElementById("new-row");
  if (!container) return;
  container.innerHTML = loadingPlaceholder(6);

  try {
    const res = await fetch("/api/games/new");
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    container.innerHTML = data.results.map(buildCardHTML).join("");
    attachCardClicks(container);

  } catch (err) {
    console.error("New Releases error:", err);
    container.innerHTML = `<div class="p-4 text-gray-400">Failed to load new releases.</div>`;
  }
}

// ------------------ Recommended ------------------
async function loadRecommended() {
  const container = document.getElementById("recommended-row");
  if (!container) return;
  container.innerHTML = loadingPlaceholder(4);

  try {
    const res = await fetch("/api/recommend");
    const data = await res.json();

    if (data.error) throw new Error(data.error);

    container.innerHTML = data.results.map(buildCardHTML).join("");
    attachCardClicks(container);

  } catch (err) {
    console.error("Recommended error:", err);
    container.innerHTML = `<div class="p-4 text-gray-400">Failed to load recommendations.</div>`;
  }
}

// ------------------ Utilities ------------------
function attachCardClicks(container) {
  // Query for data-name now, not data-id
  container.querySelectorAll("[data-name]").forEach(card => {
    card.addEventListener("click", () => {
      const name = card.getAttribute("data-name");
      if (name) {
        window.location.href = `G_DETAILS.html?name=${name}`;
      }
    });
  });
}

function loadingPlaceholder(count) {
  return Array(count).fill(`
    <div class="aspect-[3/4] w-52 shrink-0 rounded-lg bg-white/5 animate-pulse"></div>
  `).join("");
}

function escapeHtml(s) {
  if (!s) return "";
  return s.replace(/[&<>"'`=\/]/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;',
    "'": '&#39;', '/': '&#x2F;', '`': '&#x60;', '=': '&#x3D;'
  })[c]);
}
