(() => {
  const root = document.documentElement;
  const stored = localStorage.getItem("comiccraft-theme");
  if (stored) root.dataset.theme = stored;

  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    toggle.textContent = root.dataset.theme === "light" ? "☾" : "☼";
    toggle.addEventListener("click", () => {
      root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
      localStorage.setItem("comiccraft-theme", root.dataset.theme);
      toggle.textContent = root.dataset.theme === "light" ? "☾" : "☼";
    });
  }

  const form = document.getElementById("comicForm");
  if (form) {
    form.addEventListener("submit", () => {
      const button = form.querySelector(".generate-btn");
      if (!button) return;
      button.disabled = true;
      button.classList.add("loading");
      button.querySelector("span").textContent = "Creating your comic…";
    });
  }
})();
