// Site du guide « Sécuriser votre ordinateur personnel » : choix du système et liste de
// vérification. Ce fichier est écrit à la main et publié tel quel.
// Sans JavaScript, toutes les instructions restent affichées et les cases se cochent
// normalement, sans être retenues. Les réglages restent dans le navigateur du lecteur
// (localStorage) : rien n'est envoyé.
(() => {
  "use strict";

  const SYSTEM_KEY = "guide-systeme";
  const CHECKLIST_KEY = "guide-liste-de-verification";
  const SYSTEMS = ["all", "win", "mac", "linux"];

  // Le stockage peut être indisponible (navigation privée, cookies bloqués) : le site
  // fonctionne alors normalement, sans retenir les réglages.
  const storage = {
    get(key) {
      try {
        return localStorage.getItem(key);
      } catch {
        return null;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, value);
      } catch {
        // Réglage non retenu.
      }
    },
  };

  // Encadrés propres à un système : un bouton, dans leur titre, les replie ou les rouvre
  // (motif « accordéon » : le titre reste un titre pour les lecteurs d'écran). Un contenu
  // replié reste trouvable par la recherche dans la page, là où le navigateur le permet.
  const cards = [...document.querySelectorAll(".card[data-os]")];

  function setOpen(card, open) {
    card.querySelector(".card-toggle").setAttribute("aria-expanded", String(open));
    card.classList.toggle("folded", !open);
    const body = card.querySelector(".card-body");
    if (open) body.removeAttribute("hidden");
    else body.setAttribute("hidden", "until-found");
  }

  for (const card of cards) {
    const title = card.querySelector(".card-title");
    const body = card.querySelector(".card-body");
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "card-toggle";
    toggle.setAttribute("aria-controls", body.id);
    toggle.append(...title.childNodes);
    title.append(toggle);
    toggle.addEventListener("click", () => {
      setOpen(card, toggle.getAttribute("aria-expanded") !== "true");
    });
    body.addEventListener("beforematch", () => setOpen(card, true));
    setOpen(card, true);
  }

  // Choix du système : les encadrés des autres systèmes se replient, et le lecteur peut
  // toujours les rouvrir. Le choix vaut pour toutes les pages.
  function showSystem(system) {
    for (const card of cards) setOpen(card, system === "all" || card.dataset.os === system);
  }

  const filter = document.querySelector(".os-filter");
  if (filter) {
    const saved = storage.get(SYSTEM_KEY);
    const system = SYSTEMS.includes(saved) ? saved : "all";
    filter.querySelector(`input[value="${system}"]`).checked = true;
    if (system !== "all") showSystem(system);
    filter.addEventListener("change", (event) => {
      storage.set(SYSTEM_KEY, event.target.value);
      showSystem(event.target.value);
    });
  }

  // Liste de vérification : les cases cochées sont retenues d'après le texte de chaque
  // mesure, pour qu'une mesure ajoutée ou retirée du guide ne décale pas les autres.
  function loadChecked() {
    try {
      const saved = JSON.parse(storage.get(CHECKLIST_KEY) || "[]");
      return new Set(Array.isArray(saved) ? saved : []);
    } catch {
      return new Set();
    }
  }

  for (const list of document.querySelectorAll("ul.checklist")) {
    const boxes = [...list.querySelectorAll('input[type="checkbox"]')];
    const tools = list.nextElementSibling;
    if (!boxes.length || !tools || !tools.classList.contains("check-tools")) continue;
    const progress = tools.querySelector(".check-progress");
    const measure = (box) => box.labels[0].textContent.trim();

    const update = () => {
      const done = boxes.filter((box) => box.checked).length;
      const plural = done > 1 ? "s" : "";
      progress.textContent = `${done} mesure${plural} cochée${plural} sur ${boxes.length}`;
    };
    const save = () => {
      const checked = loadChecked();
      for (const box of boxes) {
        if (box.checked) checked.add(measure(box));
        else checked.delete(measure(box));
      }
      storage.set(CHECKLIST_KEY, JSON.stringify([...checked]));
    };

    const checked = loadChecked();
    for (const box of boxes) box.checked = checked.has(measure(box));
    update();
    list.addEventListener("change", () => {
      save();
      update();
    });
    tools.querySelector("button").addEventListener("click", () => {
      for (const box of boxes) box.checked = false;
      save();
      update();
    });
    tools.hidden = false;
  }
})();
