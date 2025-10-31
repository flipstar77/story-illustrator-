// ==UserScript==
// @name         Auto-Typer Pro
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Advanced auto-typer that runs on any webpage. Install with Tampermonkey/Violentmonkey/Greasemonkey
// @author       You
// @match        *://*/*
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_registerMenuCommand
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    // Configuration
    let config = {
        commands: ['go on'],
        interval: 5,
        enabled: false,
        randomize: false,
        randomDelay: false,
        typing_speed: 0, // 0 = instant, >0 = chars per second
        selector: '', // Custom selector for input field
        loopMode: 'infinite', // 'infinite', 'once', 'count'
        loopCount: 10
    };

    // State
    let isRunning = false;
    let intervalId = null;
    let commandIndex = 0;
    let commandsSent = 0;
    let ui = null;

    // Load saved config
    function loadConfig() {
        const saved = GM_getValue('autoTyperConfig');
        if (saved) {
            try {
                config = { ...config, ...JSON.parse(saved) };
            } catch (e) {
                console.error('Failed to load config:', e);
            }
        }
    }

    // Save config
    function saveConfig() {
        GM_setValue('autoTyperConfig', JSON.stringify(config));
    }

    // Find input field
    function getInputField() {
        if (config.selector) {
            const field = document.querySelector(config.selector);
            if (field) return field;
        }

        // Try common selectors
        const selectors = [
            'textarea:focus',
            'input[type="text"]:focus',
            '[contenteditable="true"]:focus',
            'textarea',
            'input[type="text"]',
            '[contenteditable="true"]',
            '#prompt-textarea',
            '[role="textbox"]',
            '.chat-input',
            '[placeholder*="message" i]',
            '[placeholder*="type" i]'
        ];

        for (let selector of selectors) {
            const field = document.querySelector(selector);
            if (field && !field.disabled && !field.readOnly) {
                return field;
            }
        }

        return null;
    }

    // Type text character by character
    async function typeText(element, text) {
        element.focus();

        if (config.typing_speed === 0) {
            // Instant mode
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeInputValueSetter.call(element, text);
                element.dispatchEvent(new Event('input', { bubbles: true }));
            } else if (element.isContentEditable) {
                element.textContent = text;
                element.dispatchEvent(new Event('input', { bubbles: true }));
            }
        } else {
            // Type character by character
            const delay = 1000 / config.typing_speed;

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.value = '';
                for (let char of text) {
                    if (!isRunning) break;
                    element.value += char;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    await sleep(delay);
                }
            } else if (element.isContentEditable) {
                element.textContent = '';
                for (let char of text) {
                    if (!isRunning) break;
                    element.textContent += char;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                    await sleep(delay);
                }
            }
        }
    }

    // Press Enter
    function pressEnter(element) {
        const events = ['keydown', 'keypress', 'keyup'];
        events.forEach(eventType => {
            const event = new KeyboardEvent(eventType, {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
                bubbles: true,
                cancelable: true
            });
            element.dispatchEvent(event);
        });

        // Try form submit
        const form = element.closest('form');
        if (form) {
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);
        }

        // Try clicking submit button
        const submitButton = element.closest('form')?.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.click();
        }
    }

    // Sleep utility
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Log to UI
    function log(message, type = 'info') {
        if (!ui) return;

        const logDiv = ui.querySelector('#at-log');
        if (!logDiv) return;

        const timestamp = new Date().toLocaleTimeString();
        const entry = document.createElement('div');
        entry.className = `at-log-entry at-${type}`;
        entry.textContent = `[${timestamp}] ${message}`;
        logDiv.appendChild(entry);
        logDiv.scrollTop = logDiv.scrollHeight;

        // Keep only last 50 entries
        while (logDiv.children.length > 50) {
            logDiv.removeChild(logDiv.firstChild);
        }

        // Update stats
        const statsDiv = ui.querySelector('#at-stats');
        if (statsDiv) {
            statsDiv.textContent = `Commands sent: ${commandsSent}`;
        }
    }

    // Execute command
    async function executeCommand() {
        if (config.loopMode !== 'infinite' && commandsSent >= config.loopCount) {
            log('Reached command limit. Stopping.', 'success');
            stopTyping();
            return;
        }

        const inputField = getInputField();
        if (!inputField) {
            log('Input field not found! Stopping...', 'error');
            stopTyping();
            return;
        }

        // Get command
        let command;
        if (config.randomize) {
            command = config.commands[Math.floor(Math.random() * config.commands.length)];
        } else {
            command = config.commands[commandIndex % config.commands.length];
            commandIndex++;
        }

        log(`Typing: "${command}"`, 'info');

        // Type the command
        await typeText(inputField, command);
        await sleep(200);

        // Press Enter
        pressEnter(inputField);
        commandsSent++;
        log(`✓ Sent (${commandsSent})`, 'success');

        if (config.loopMode === 'once' && commandsSent >= config.commands.length) {
            log('Completed one cycle. Stopping.', 'success');
            stopTyping();
        }
    }

    // Start typing
    function startTyping() {
        if (isRunning) return;

        if (config.commands.length === 0 || config.commands[0] === '') {
            log('No commands configured!', 'error');
            return;
        }

        isRunning = true;
        commandsSent = 0;
        updateUI();

        log('Auto-typer started!', 'success');

        // Execute immediately
        executeCommand();

        // Set interval
        const runInterval = () => {
            if (!isRunning) return;

            let delay = config.interval * 1000;
            if (config.randomDelay) {
                const variation = delay * 0.2;
                delay = delay + (Math.random() * variation * 2 - variation);
            }

            intervalId = setTimeout(() => {
                executeCommand().then(runInterval);
            }, delay);
        };

        // Schedule next execution
        let delay = config.interval * 1000;
        if (config.randomDelay) {
            const variation = delay * 0.2;
            delay = delay + (Math.random() * variation * 2 - variation);
        }
        intervalId = setTimeout(runInterval, delay);
    }

    // Stop typing
    function stopTyping() {
        if (!isRunning) return;

        isRunning = false;
        if (intervalId) {
            clearTimeout(intervalId);
            intervalId = null;
        }

        log('Auto-typer stopped!', 'info');
        updateUI();
    }

    // Toggle typing
    function toggleTyping() {
        if (isRunning) {
            stopTyping();
        } else {
            startTyping();
        }
    }

    // Update UI
    function updateUI() {
        if (!ui) return;

        const statusDiv = ui.querySelector('#at-status');
        const startBtn = ui.querySelector('#at-start-btn');
        const stopBtn = ui.querySelector('#at-stop-btn');

        if (isRunning) {
            statusDiv.textContent = '🟢 Running';
            statusDiv.style.color = '#4ec9b0';
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            statusDiv.textContent = '⚫ Stopped';
            statusDiv.style.color = '#f48771';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }

    // Create UI
    function createUI() {
        const container = document.createElement('div');
        container.id = 'auto-typer-ui';
        container.innerHTML = `
            <style>
                #auto-typer-ui {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 350px;
                    background: #2d2d2d;
                    color: #ffffff;
                    border-radius: 10px;
                    padding: 15px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                    font-family: 'Segoe UI', Arial, sans-serif;
                    z-index: 999999;
                    font-size: 13px;
                }
                #auto-typer-ui.at-minimized {
                    width: 200px;
                    height: auto;
                }
                #auto-typer-ui.at-minimized .at-content {
                    display: none;
                }
                #auto-typer-ui .at-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 10px;
                    cursor: move;
                }
                #auto-typer-ui .at-title {
                    font-weight: bold;
                    font-size: 14px;
                }
                #auto-typer-ui .at-controls {
                    display: flex;
                    gap: 5px;
                }
                #auto-typer-ui button {
                    padding: 6px 12px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 12px;
                    font-weight: 500;
                }
                #auto-typer-ui .at-btn-primary {
                    background: #4ec9b0;
                    color: #000;
                }
                #auto-typer-ui .at-btn-danger {
                    background: #f48771;
                    color: #000;
                }
                #auto-typer-ui .at-btn-secondary {
                    background: #3e3e3e;
                    color: #fff;
                }
                #auto-typer-ui button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }
                #auto-typer-ui input, #auto-typer-ui textarea, #auto-typer-ui select {
                    width: 100%;
                    padding: 6px;
                    background: #1e1e1e;
                    border: 1px solid #3e3e3e;
                    border-radius: 5px;
                    color: #fff;
                    font-size: 12px;
                    margin: 5px 0;
                    box-sizing: border-box;
                }
                #auto-typer-ui textarea {
                    min-height: 60px;
                    font-family: monospace;
                }
                #auto-typer-ui label {
                    display: block;
                    margin-top: 8px;
                    margin-bottom: 3px;
                    color: #9cdcfe;
                    font-size: 12px;
                }
                #auto-typer-ui #at-status {
                    font-weight: bold;
                    margin: 10px 0;
                }
                #auto-typer-ui #at-log {
                    background: #1e1e1e;
                    padding: 8px;
                    border-radius: 5px;
                    max-height: 120px;
                    overflow-y: auto;
                    font-size: 11px;
                    font-family: monospace;
                    margin-top: 10px;
                }
                #auto-typer-ui .at-log-entry {
                    margin: 2px 0;
                }
                #auto-typer-ui .at-info { color: #9cdcfe; }
                #auto-typer-ui .at-success { color: #4ec9b0; }
                #auto-typer-ui .at-error { color: #f48771; }
                #auto-typer-ui #at-stats {
                    margin-top: 8px;
                    font-size: 11px;
                    color: #888;
                }
            </style>
            <div class="at-header">
                <div class="at-title">🤖 Auto-Typer</div>
                <div class="at-controls">
                    <button class="at-btn-secondary" id="at-minimize-btn" title="Minimize">_</button>
                    <button class="at-btn-secondary" id="at-close-btn" title="Close">×</button>
                </div>
            </div>
            <div class="at-content">
                <div id="at-status">⚫ Stopped</div>

                <label>Commands (one per line):</label>
                <textarea id="at-commands" placeholder="go on"></textarea>

                <label>Interval (seconds):</label>
                <input type="number" id="at-interval" value="5" min="1" max="3600">

                <label>
                    <input type="checkbox" id="at-randomize"> Randomize order
                </label>
                <label>
                    <input type="checkbox" id="at-random-delay"> Random delay (±20%)
                </label>

                <div style="margin-top: 10px; display: flex; gap: 5px;">
                    <button class="at-btn-primary" id="at-start-btn">▶ Start</button>
                    <button class="at-btn-danger" id="at-stop-btn" disabled>⬛ Stop</button>
                    <button class="at-btn-secondary" id="at-save-btn">💾</button>
                </div>

                <div id="at-log"></div>
                <div id="at-stats">Commands sent: 0</div>
            </div>
        `;

        document.body.appendChild(container);

        // Load config into UI
        const commandsInput = container.querySelector('#at-commands');
        const intervalInput = container.querySelector('#at-interval');
        const randomizeCheck = container.querySelector('#at-randomize');
        const randomDelayCheck = container.querySelector('#at-random-delay');

        commandsInput.value = config.commands.join('\n');
        intervalInput.value = config.interval;
        randomizeCheck.checked = config.randomize;
        randomDelayCheck.checked = config.randomDelay;

        // Event listeners
        container.querySelector('#at-start-btn').addEventListener('click', startTyping);
        container.querySelector('#at-stop-btn').addEventListener('click', stopTyping);

        container.querySelector('#at-save-btn').addEventListener('click', () => {
            config.commands = commandsInput.value.split('\n').filter(c => c.trim());
            config.interval = parseFloat(intervalInput.value);
            config.randomize = randomizeCheck.checked;
            config.randomDelay = randomDelayCheck.checked;
            saveConfig();
            log('Configuration saved!', 'success');
        });

        container.querySelector('#at-minimize-btn').addEventListener('click', () => {
            container.classList.toggle('at-minimized');
        });

        container.querySelector('#at-close-btn').addEventListener('click', () => {
            stopTyping();
            container.remove();
            ui = null;
        });

        // Make draggable
        let isDragging = false;
        let currentX, currentY, initialX, initialY;

        const header = container.querySelector('.at-header');
        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            initialX = e.clientX - container.offsetLeft;
            initialY = e.clientY - container.offsetTop;
        });

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                container.style.left = currentX + 'px';
                container.style.top = currentY + 'px';
                container.style.right = 'auto';
                container.style.bottom = 'auto';
            }
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
        });

        return container;
    }

    // Show/hide UI
    function toggleUI() {
        if (ui) {
            ui.remove();
            ui = null;
            stopTyping();
        } else {
            ui = createUI();
            log('Ready! Configure and click Start.', 'info');
        }
    }

    // Initialize
    loadConfig();

    // Register menu command
    GM_registerMenuCommand('Toggle Auto-Typer', toggleUI);

    // Keyboard shortcut: Ctrl+Shift+A
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.shiftKey && e.key === 'A') {
            e.preventDefault();
            toggleUI();
        }
    });

    console.log('Auto-Typer Pro loaded! Press Ctrl+Shift+A to open.');
})();
