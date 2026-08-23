"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { collections, plugins } from "../catalog.generated";
const categories = [
  "All",
  ...Array.from(new Set(plugins.map((plugin) => plugin.category))),
];
const hostOptions = [
  "All hosts",
  "Codex",
  "Claude Code",
  "Claude Cowork",
] as const;

export function Catalog() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [collectionSlug, setCollectionSlug] = useState("all");
  const [host, setHost] =
    useState<(typeof hostOptions)[number]>("All hosts");
  const [sortMode, setSortMode] = useState<"curated" | "skills">("curated");
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
        setCollectionSlug("all");
        setHost("All hosts");
        setSortMode("curated");
        window.requestAnimationFrame(() => searchRef.current?.focus());
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const matches = useMemo(() => {
    const needle = query.trim().toLowerCase();
    const selectedCollection = collections.find(
      (collection) => collection.slug === collectionSlug,
    );
    const scopedPlugins = plugins.filter((plugin) => {
      const inCategory = category === "All" || plugin.category === category;
      const onHost =
        host === "All hosts" || plugin.platforms.some((item) => item === host);
      const inCollection =
        !selectedCollection ||
        selectedCollection.plugins.some((item) => item === plugin.slug);
      return inCategory && onHost && inCollection;
    });
    const directMatches = scopedPlugins.filter((plugin) =>
      [plugin.name, plugin.slug].join(" ").toLowerCase().includes(needle),
    );
    const broadMatches = scopedPlugins.filter((plugin) => {
      const haystack = [
        plugin.name,
        plugin.slug,
        plugin.description,
        plugin.longDescription,
        JSON.stringify(plugin.guide),
        ...plugin.skills.map((skill) => skill.name + " " + skill.description),
      ]
        .join(" ")
        .toLowerCase();
      return !needle || haystack.includes(needle);
    });
    const filtered = broadMatches;

    if (sortMode === "skills") {
      return [...filtered].sort(
        (left, right) => right.counts.skills - left.counts.skills,
      );
    }

    if (!needle) return filtered;

    const directSlugs = new Set(directMatches.map((plugin) => plugin.slug));
    return [...filtered].sort(
      (left, right) =>
        Number(directSlugs.has(right.slug)) - Number(directSlugs.has(left.slug)),
    );
  }, [category, collectionSlug, host, query, sortMode]);

  function resetCatalog() {
    setQuery("");
    setCategory("All");
    setCollectionSlug("all");
    setHost("All hosts");
    setSortMode("curated");
    searchRef.current?.focus();
  }

  return (
    <div className="catalog">
      <div className="catalog-tools">
        <div
          aria-labelledby="collection-filter-label"
          className="filter-group collection-filter"
          role="group"
        >
          <span className="control-label" id="collection-filter-label">
            Outcome collection
          </span>
          <div
            className="filter-list"
            aria-label="Filter by outcome collection"
            data-testid="collection-filter"
          >
            <button
              aria-pressed={collectionSlug === "all"}
              onClick={() => setCollectionSlug("all")}
              type="button"
            >
              All outcomes
            </button>
            {collections.map((collection) => (
              <button
                aria-pressed={collectionSlug === collection.slug}
                key={collection.slug}
                onClick={() => setCollectionSlug(collection.slug)}
                type="button"
              >
                {collection.name}
              </button>
            ))}
          </div>
        </div>

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

        <div
          aria-labelledby="category-filter-label"
          className="filter-group"
          role="group"
        >
          <span className="control-label" id="category-filter-label">
            Category
          </span>
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

        <div
          aria-labelledby="host-filter-label"
          className="filter-group host-filter"
          role="group"
        >
          <span className="control-label" id="host-filter-label">
            Verified host
          </span>
          <div
            className="filter-list"
            aria-label="Filter by verified host"
            data-testid="host-filter"
          >
            {hostOptions.map((item) => (
              <button
                aria-pressed={host === item}
                key={item}
                onClick={() => setHost(item)}
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
          {matches.length} of {plugins.length} public records
        </p>
        <div
          aria-labelledby="sort-plugins-label"
          className="sort-list"
          role="group"
        >
          <span id="sort-plugins-label">Sort</span>
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

      {matches.length > 0 ? (
        <div className="registry-list" aria-label="Plugin registry">
          {matches.map((plugin, index) => {
            const collection = collections.find((item) =>
              item.plugins.some((slug) => slug === plugin.slug),
            );
            return (
              <Link
                className={
                  "registry-row outcome-" + (collection?.slug ?? "uncategorized")
                }
                data-outcome={collection?.slug ?? "uncategorized"}
                data-testid={"plugin-row-" + plugin.slug}
                href={"/plugins/" + plugin.slug}
                key={plugin.slug}
              >
                <span className="registry-index" aria-hidden="true">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <span className="registry-main">
                  <span className="registry-name">{plugin.name}</span>
                  <span className="registry-description">
                    {plugin.description}
                  </span>
                </span>
                <span className="registry-meta">
                  <span className="registry-category">
                    {collection?.name ?? plugin.category}
                  </span>
                  <span className="registry-hosts" aria-label="Verified hosts">
                    {plugin.platforms.join(" / ")}
                  </span>
                  <span className="registry-count">
                    {plugin.counts.skills} skills
                  </span>
                </span>
                <span className="registry-arrow" aria-hidden="true">
                  ↗
                </span>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="empty-state">
          <p>No public plugin matches these filters.</p>
          <button onClick={resetCatalog} type="button">
            Reset registry
          </button>
        </div>
      )}
    </div>
  );
}
