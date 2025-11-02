/**
 * Terminal initialization - independent of Firebase
 * This loads first to ensure the terminal is always available
 */
import { Terminal } from "./terminal.js";

// Initialize Terminal immediately
const terminal = new Terminal("terminal-container");
const terminalToggle = document.getElementById("terminal-toggle");

if (terminalToggle) {
  terminalToggle.addEventListener("click", () => {
    const container = document.getElementById("terminal-container");
    if (container && container.classList.contains("hidden")) {
      terminal.show();
    } else {
      terminal.hide();
    }
  });
}

// Keyboard shortcut: Ctrl+` or Cmd+` to toggle terminal
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "`") {
    e.preventDefault();
    const container = document.getElementById("terminal-container");
    if (container && container.classList.contains("hidden")) {
      terminal.show();
    } else {
      terminal.hide();
    }
  }
});

// Export terminal instance for use by other modules if needed
window.devTerminal = terminal;
