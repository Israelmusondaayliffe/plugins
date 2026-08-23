"use client";

import { useEffect, useSyncExternalStore } from "react";

const storageKey = "community-agent-plugins-theme";

type Theme = "paper" | "sumi";

function applyTheme(theme: Theme) {
  if (theme === "sumi") {
    document.documentElement.dataset.theme = "sumi";
  } else {
    delete document.documentElement.dataset.theme;
  }
}

export function ThemeToggle() {
  const theme = useSyncExternalStore(
    (onStoreChange) => {
      window.addEventListener("storage", onStoreChange);
      window.addEventListener("community-agent-plugins-theme-change", onStoreChange);
      return () => {
        window.removeEventListener("storage", onStoreChange);
        window.removeEventListener("community-agent-plugins-theme-change", onStoreChange);
      };
    },
    () => (window.localStorage.getItem(storageKey) === "sumi" ? "sumi" : "paper"),
    () => "paper",
  );

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  function toggleTheme() {
    const nextTheme: Theme = theme === "paper" ? "sumi" : "paper";
    applyTheme(nextTheme);
    window.localStorage.setItem(storageKey, nextTheme);
    window.dispatchEvent(new Event("community-agent-plugins-theme-change"));
  }

  return (
    <button
      aria-label={
        theme === "paper" ? "Switch to Sumi theme" : "Switch to Paper theme"
      }
      aria-pressed={theme === "sumi"}
      className="theme-toggle"
      data-testid="theme-toggle"
      onClick={toggleTheme}
      type="button"
    >
      <span className="theme-toggle-swatch" aria-hidden="true" />
      {theme === "paper" ? "Sumi" : "Paper"}
    </button>
  );
}
