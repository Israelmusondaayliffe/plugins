"use client";

import { useState } from "react";

type CopyCommandProps = {
  command: string;
  compact?: boolean;
  label?: string;
};

export function CopyCommand({
  command,
  compact = false,
  label = "command",
}: CopyCommandProps) {
  const [status, setStatus] = useState<"idle" | "copied" | "failed">("idle");

  async function copy() {
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(command);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = command;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        const copied = document.execCommand("copy");
        textarea.remove();
        if (!copied) throw new Error("Fallback copy failed");
      }
      setStatus("copied");
    } catch {
      setStatus("failed");
    }
    window.setTimeout(() => setStatus("idle"), 1800);
  }

  const buttonText =
    status === "copied"
      ? "Copied"
      : status === "failed"
        ? "Copy failed"
        : "Copy";
  const announcement =
    status === "copied"
      ? label + " copied to clipboard"
      : status === "failed"
        ? label + " could not be copied"
        : "";

  return (
    <div className={"copy-command" + (compact ? " copy-command-compact" : "")}>
      <code>{command}</code>
      <button
        aria-label={
          status === "idle" ? "Copy " + label + ": " + command : announcement
        }
        onClick={copy}
        type="button"
      >
        {buttonText}
      </button>
      <span className="sr-only" aria-live="polite">
        {announcement}
      </span>
    </div>
  );
}
