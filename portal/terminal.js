/**
 * Developer Console / Terminal Component
 * Provides a simple terminal interface for debugging and administrative tasks
 */

export class Terminal {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.history = [];
    this.historyIndex = 0;
    this.commands = this.initializeCommands();
    this.render();
  }

  initializeCommands() {
    return {
      help: {
        description: 'Show available commands',
        execute: () => {
          const commandList = Object.entries(this.commands)
            .map(([name, cmd]) => `  ${name.padEnd(15)} - ${cmd.description}`)
            .join('\n');
          return `Available commands:\n${commandList}`;
        }
      },
      clear: {
        description: 'Clear the terminal',
        execute: () => {
          this.clearOutput();
          return '';
        }
      },
      version: {
        description: 'Show system version',
        execute: () => 'Claims Processing Portal v1.0.0'
      },
      status: {
        description: 'Show system status',
        execute: () => {
          // Note: These are hardcoded values for the initial implementation.
          // Future enhancement: dynamically check Firebase auth and portal mode
          return `System Status: Online
Firebase Auth: Connected
Portal Mode: Development`;
        }
      },
      echo: {
        description: 'Echo the provided text',
        execute: (args) => args.join(' ')
      }
    };
  }

  render() {
    this.container.innerHTML = `
      <div class="terminal-container">
        <div class="terminal-header">
          <span class="terminal-title">Developer Console</span>
          <button class="terminal-close" id="terminal-close">×</button>
        </div>
        <div class="terminal-output" id="terminal-output">
          <div class="terminal-line">Welcome to Claims Processing Portal Console</div>
          <div class="terminal-line">Type 'help' for available commands</div>
        </div>
        <div class="terminal-input-container">
          <span class="terminal-prompt">$</span>
          <input type="text" class="terminal-input" id="terminal-input" autocomplete="off" />
        </div>
      </div>
    `;

    this.setupEventListeners();
  }

  setupEventListeners() {
    const input = document.getElementById('terminal-input');
    const closeBtn = document.getElementById('terminal-close');

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        this.executeCommand(input.value);
        input.value = '';
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (this.historyIndex > 0) {
          this.historyIndex--;
          input.value = this.history[this.historyIndex] || '';
        }
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (this.historyIndex < this.history.length - 1) {
          this.historyIndex++;
          input.value = this.history[this.historyIndex] || '';
        } else {
          this.historyIndex = this.history.length;
          input.value = '';
        }
      }
    });

    closeBtn.addEventListener('click', () => {
      this.container.classList.add('hidden');
    });
  }

  executeCommand(commandLine) {
    const output = document.getElementById('terminal-output');
    
    // Add command to history
    if (commandLine.trim()) {
      this.history.push(commandLine);
      this.historyIndex = this.history.length;
    }

    // Display the command
    const commandDiv = document.createElement('div');
    commandDiv.className = 'terminal-line terminal-command';
    commandDiv.textContent = `$ ${commandLine}`;
    output.appendChild(commandDiv);

    // Parse and execute
    const parts = commandLine.trim().split(/\s+/);
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);

    let result;
    if (this.commands[command]) {
      try {
        result = this.commands[command].execute(args);
      } catch (error) {
        result = `Error: ${error.message}`;
      }
    } else if (command) {
      result = `Command not found: ${command}. Type 'help' for available commands.`;
    }

    // Display result
    if (result) {
      const resultDiv = document.createElement('div');
      resultDiv.className = 'terminal-line terminal-result';
      resultDiv.textContent = result;
      output.appendChild(resultDiv);
    }

    // Auto-scroll to bottom
    output.scrollTop = output.scrollHeight;
  }

  clearOutput() {
    const output = document.getElementById('terminal-output');
    output.innerHTML = '';
  }

  show() {
    this.container.classList.remove('hidden');
    const input = document.getElementById('terminal-input');
    if (input) input.focus();
  }

  hide() {
    this.container.classList.add('hidden');
  }
}
