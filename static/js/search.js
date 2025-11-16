// document.addEventListener("DOMContentLoaded", () => {
//     initSearch();
// });

// async function initSearch() {
//     const input = document.getElementById("searchInput");
//     input.addEventListener("input", () => {
//         const q = input.value.trim();
//         if (q.length >= 2) performSearch(q);
//     });
//     input.addEventListener("keypress", e => {
//         if (e.key === "Enter") performSearch(input.value.trim());
//     });
// }

// // Use exactly the same buildCardHTML as home.js
// function buildCardHTML(game) {
//     const genres = game.genres?.join(", ") || "";
//     const cover = game.cover || "/static/placeholder-game.png";
//     const title = escapeHtml(game.title || game.name || "Untitled");

//     return `
//     <div class="group relative aspect-[3/4] w-52 shrink-0 snap-start overflow-hidden rounded-lg 
//         transition-transform duration-300 ease-in-out hover:scale-105 hover:z-10 cursor-pointer" 
//         data-name="${encodeURIComponent(title)}">
        
//         <img class="h-full w-full object-cover" src="${cover}" 
//             alt="${title}" onerror="this.src='/static/placeholder-game.png'"/>
        
//         <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent"></div>
        
//         <div class="absolute bottom-0 left-0 right-0 p-3">
//             <h4 class="font-bold text-white truncate">${title}</h4>
//             <p class="text-xs text-gray-300 truncate">${genres}</p>
//         </div>
//     </div>
//     `;
// }

// async function performSearch(query) {
//     const container = document.getElementById("resultsGrid");
//     container.innerHTML = ""; // clear previous results
//     try {
//         const res = await fetch(`/api/search_game?q=${encodeURIComponent(query)}`);
//         const data = await res.json();
//         if (!data.results?.length) {
//             container.innerHTML = `<div class="p-4 text-gray-400">No results found for "${query}"</div>`;
//             return;
//         }
//         container.innerHTML = data.results.map(buildCardHTML).join("");
//         attachCardClicks(container);
//     } catch (err) {
//         console.error("Search error:", err);
//         container.innerHTML = `<div class="p-4 text-gray-400">Failed to search. Try again.</div>`;
//     }
// }

// // Same as home.js
// function attachCardClicks(container) {
//     container.querySelectorAll("[data-name]").forEach(card => {
//         card.addEventListener("click", () => {
//             const name = card.getAttribute("data-name");
//             if (name) {
//                 window.location.href = `G_DETAILS.html?name=${name}`;
//             }
//         });
//     });
// }

// function escapeHtml(s) {
//     if (!s) return "";
//     return s.replace(/[&<>"'`=\/]/g, c => ({
//         '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;',
//         "'": '&#39;', '/': '&#x2F;', '`': '&#x60;', '=': '&#x3D;'
//     })[c]);
// }
