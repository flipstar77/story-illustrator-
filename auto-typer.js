// Auto-typer script for browser
// To use: Open browser console (F12), paste this script, and run it

// Configuration
const commands = ["go on"]; // Add more commands if needed
const intervalSeconds = 5; // Time between commands in seconds

let isRunning = true;
let commandIndex = 0;

// Find the input field (adjust selector if needed)
function getInputField() {
    // Try common selectors for chat/command inputs
    return document.querySelector('textarea, input[type="text"], [contenteditable="true"]');
}

// Type text character by character (more natural)
async function typeText(element, text) {
    element.focus();

    for (let char of text) {
        // Set value for input/textarea
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.value += char;
            element.dispatchEvent(new Event('input', { bubbles: true }));
        }
        // Set text for contenteditable
        else if (element.isContentEditable) {
            element.textContent += char;
            element.dispatchEvent(new Event('input', { bubbles: true }));
        }

        await new Promise(resolve => setTimeout(resolve, 50)); // 50ms delay between chars
    }
}

// Press Enter key
function pressEnter(element) {
    const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true,
        cancelable: true
    });

    element.dispatchEvent(enterEvent);

    // Also try submit if it's a form
    const form = element.closest('form');
    if (form) {
        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    }

    // Trigger keyup as well
    const keyupEvent = new KeyboardEvent('keyup', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        bubbles: true
    });
    element.dispatchEvent(keyupEvent);
}

// Main loop
async function autoType() {
    console.log('Auto-typer started. Type "stopAutoTyper()" to stop.');

    while (isRunning) {
        const inputField = getInputField();

        if (!inputField) {
            console.log('Input field not found. Make sure you\'re on the right page.');
            await new Promise(resolve => setTimeout(resolve, intervalSeconds * 1000));
            continue;
        }

        const command = commands[commandIndex % commands.length];
        console.log(`Typing: "${command}"`);

        // Clear existing text
        if (inputField.tagName === 'INPUT' || inputField.tagName === 'TEXTAREA') {
            inputField.value = '';
        } else if (inputField.isContentEditable) {
            inputField.textContent = '';
        }

        // Type the command
        await typeText(inputField, command);

        // Wait a bit before pressing enter
        await new Promise(resolve => setTimeout(resolve, 500));

        // Press Enter
        pressEnter(inputField);
        console.log('Enter pressed');

        commandIndex++;

        // Wait for the next interval
        await new Promise(resolve => setTimeout(resolve, intervalSeconds * 1000));
    }
}

// Function to stop the script
window.stopAutoTyper = function() {
    isRunning = false;
    console.log('Auto-typer stopped');
};

// Start the script
autoType();
