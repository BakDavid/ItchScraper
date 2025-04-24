async function getJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch ${url}`);
    return res.json();
}

function stringToGradient(str) {
    const hash = [...str].reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const hue = hash % 360;
    return `linear-gradient(135deg, hsl(${hue}, 70%, 60%), hsl(${
        (hue + 60) % 360
    }, 70%, 60%))`;
}

function createCard(jam) {
    const card = document.createElement("a");
    card.className = "jam-card";
    card.href = jam.url;
    card.target = "_blank";
    card.style.background = stringToGradient(jam.name);
    card.innerHTML = `
      <div class="jam-title">${jam.name}</div>
      <div class="jam-meta">👥 Joined: ${jam.joined ?? "?"}</div>
    `;
    return card;
}

async function loadAllJams() {
    const index = await getJSON("../data/index.json"); // Adjust path as needed
    const allJams = [];
    const seen = new Set();

    for (const file of index) {
        try {
            const jams = await getJSON(`../data/${file}`);
            for (const jam of jams) {
                if (!seen.has(jam.url)) {
                    seen.add(jam.url);
                    allJams.push(jam);
                }
            }
        } catch (e) {
            console.error(`Error loading ${file}:`, e);
        }
    }

    return allJams;
}

async function renderJams() {
    const container = document.getElementById("jam-list");
    const jams = await loadAllJams();

    jams.sort((a, b) => (b.joined || 0) - (a.joined || 0));
    jams.forEach((jam) => container.appendChild(createCard(jam)));
}

renderJams();
