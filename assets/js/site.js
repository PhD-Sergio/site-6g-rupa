// Light/dark toggle. Without a saved choice the page follows the OS setting;
// the saved choice is applied before first paint by the inline script in head.html.
(() => {
  const root = document.documentElement;
  const button = document.querySelector("[data-theme-toggle]");
  if (!button) return;

  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");
  const isDark = () => (root.dataset.theme ? root.dataset.theme === "dark" : prefersDark.matches);
  const sync = () => button.setAttribute("aria-pressed", String(isDark()));

  button.addEventListener("click", () => {
    const next = isDark() ? "light" : "dark";
    root.dataset.theme = next;
    try {
      localStorage.setItem("theme", next);
    } catch (e) {}
    sync();
  });
  prefersDark.addEventListener("change", sync);
  sync();
})();

// YouTube videos: nothing loads from YouTube until the reader presses play.
// The link then becomes a privacy-enhanced player; without JavaScript it
// simply opens the video on YouTube.
document.querySelectorAll("[data-youtube]").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const player = document.createElement("iframe");
    player.src = `https://www.youtube-nocookie.com/embed/${link.dataset.youtube}?autoplay=1&rel=0`;
    player.title = link.dataset.title || "Video";
    player.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    player.allowFullscreen = true;
    link.replaceWith(player);
    player.focus();
  });
});

// Software demos: a muted loop plays over the screenshot while its entry is
// hovered or focused. Nothing is downloaded until then.
(() => {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.querySelectorAll("[data-hover-video]").forEach((entry) => {
    const video = entry.querySelector("video");
    if (!video) return;
    const play = () => {
      entry.classList.add("is-playing");
      video.play().catch(() => entry.classList.remove("is-playing"));
    };
    const stop = () => {
      entry.classList.remove("is-playing");
      video.pause();
    };
    entry.addEventListener("pointerenter", play);
    entry.addEventListener("pointerleave", stop);
    entry.addEventListener("focusin", play);
    entry.addEventListener("focusout", (event) => {
      if (!entry.contains(event.relatedTarget)) stop();
    });
  });
})();
