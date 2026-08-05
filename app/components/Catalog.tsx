"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { marketplaceName, plugins } from "../catalog.generated";
import { CopyCommand } from "./CopyCommand";

const categories = [
  "All",
  ...Array.from(new Set(plugins.map((plugin) => plugin.category))),
];

export function Catalog() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [sortMode, setSortMode] = useState<"curated" | "skills">("curated");
  const [selectedSlug, setSelectedSlug] = useState(plugins[0].slug);
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const isTyping =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target instanceof HTMLSelectElement ||
        target?.isContentEditable;

      if (event.key === "/" && !isTyping) {
        event.preventDefault();
        searchRef.current?.focus();
      }

      if (event.key === "Escape") {
        setQuery("");
        setCategory("All");
        searchRef.current?.focus();
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const categoryMatches = plugins.filter(
      (plugin) => category === "All" || plugin.category === category,
    );
    const directMatches = categoryMatches.filter((plugin) =>
      [plugin.name, plugin.slug].join(" ").toLowerCase().includes(needle),
    );
    const broadMatches = categoryMatches.filter((plugin) => {
      const haystack = [
        plugin.name,
        plugin.slug,
        plugin.description,
        plugin.longDescription,
        ...plugin.skills.map((skill) => skill.name + " " + skill.description),
      ]
        .join(" ")
        .toLowerCase();
      return !needle || haystack.includes(needle);
    });
    const filtered = needle && directMatches.length ? directMatches : broadMatches;

    if (sortMode === "skills") {
      return [...filtered].sort(
        (left, right) => right.counts.skills - left.counts.skills,
      );
    }

    return filtered;
  }, [category, query, sortMode]);

  const selectedPlugin =
    matches.find((plugin) => plugin.slug === selectedSlug) ?? matches[0] ?? null;

  function resetCatalog() {
    setQuery("");
    setCategory("All");
    setSortMode("curated");
    setSelectedSlug(plugins[0].slug);
    searchRef.current?.focus();
  }

  return (
    <div className="catalog">
      <div className="catalog-tools">
        <label className="search-field">
          <span>Search the registry</span>
          <span className="search-control">
            <input
              aria-keyshortcuts="/"
              aria-label="Search plugins and skills"
              data-testid="catalog-search"
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Plugin or skill name"
              ref={searchRef}
              type="search"
              value={query}
            />
            <kbd>/</kbd>
          </span>
        </label>

        <div className="filter-group">
          <span className="control-label">Category</span>
          <div className="filter-list" aria-label="Filter by category">
            {categories.map((item) => (
              <button
                aria-pressed={category === item}
                key={item}
                onClick={() => setCategory(item)}
                type="button"
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="catalog-status">
        <p aria-live="polite">
          {matches.length} {matches.length === 1 ? "record" : "records"}
        </p>
        <div className="sort-list" aria-label="Sort plugins">
          <span>Sort</span>
          <button
            aria-pressed={sortMode === "curated"}
            onClick={() => setSortMode("curated")}
            type="button"
          >
            Curated
          </button>
          <button
            aria-pressed={sortMode === "skills"}
            onClick={() => setSortMode("skills")}
            type="button"
          >
            Most skills
          </button>
        </div>
      </div>

      {matches.length > 0 && selectedPlugin ? (
        <div className="registry-layout">
          <div className="registry-list" aria-label="Plugin registry">
            {matches.map((plugin, index) => {
              const selected = selectedPlugin.slug === plugin.slug;
              return (
                <button
                  aria-pressed={selected}
                  className="registry-row"
                  data-testid={"plugin-row-" + plugin.slug}
                  key={plugin.slug}
                  onClick={() => setSelectedSlug(plugin.slug)}
                  onFocus={() => setSelectedSlug(plugin.slug)}
                  onMouseEnter={() => setSelectedSlug(plugin.slug)}
                  type="button"
                >
                  <span className="registry-index">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span className="registry-name">{plugin.name}</span>
                  <span className="registry-category">{plugin.category}</span>
                  <span className="registry-count">
                    {plugin.counts.skills} skills
                  </span>
                  <span className="registry-arrow" aria-hidden="true">
                    ↗
                  </span>
                </button>
              );
            })}
          </div>

          <aside
            className="registry-preview"
            data-testid="plugin-preview"
            key={selectedPlugin.slug}
            aria-label={selectedPlugin.name + " selected plugin"}
          >
            <div className="preview-topline">
              <span>{selectedPlugin.category}</span>
              <span>{selectedPlugin.counts.skills} skills</span>
            </div>
            <div className="platform-list" aria-label="Supported platforms">
              {selectedPlugin.platforms.map((platform) => (
                <span key={platform}>{platform}</span>
              ))}
            </div>
            <p className="preview-install-note">{selectedPlugin.runtimeNote}</p>
            <div className="preview-copy">
              <h3>{selectedPlugin.name}</h3>
              <p>{selectedPlugin.longDescription}</p>
            </div>
            <div className="preview-skills">
              <span>Featured skills</span>
              <ul>
                {selectedPlugin.skills.slice(0, 5).map((skill) => (
                  <li key={skill.name}>{skill.name}</li>
                ))}
              </ul>
            </div>
            <div className="preview-actions">
              {selectedPlugin.platforms.includes("Codex") ? (
                <CopyCommand
                  command={
                    "codex plugin add " +
                    selectedPlugin.slug +
                    "@" +
                    marketplaceName
                  }
                  compact
                  label="Codex install command"
                />
              ) : (
                <CopyCommand
                  command={
                    "/plugin install " +
                    selectedPlugin.slug +
                    "@" +
                    marketplaceName
                  }
                  compact
                  label="Claude Code install command"
                />
              )}
              <p className="preview-install-note">
                Open the full record for host-specific installation and support.
              </p>
              <Link href={"/plugins/" + selectedPlugin.slug}>
                Open plugin record
              </Link>
            </div>
          </aside>
        </div>
      ) : (
        <div className="empty-state">
          <p>No plugin matches this search.</p>
          <button onClick={resetCatalog} type="button">
            Reset registry
          </button>
        </div>
      )}
    </div>
  );
}
