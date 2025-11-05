"""
Prompt Enhancer Chat Tab for Story Illustrator V3

A chat-style interface for enhancing prompts using Ollama or Prompt Quill.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
import pyperclip


class PromptEnhancerTab:
    """Prompt Enhancer Chat Interface"""

    def __init__(self, notebook, root):
        """
        Initialize the Prompt Enhancer tab

        Args:
            notebook: ttk.Notebook to add tab to
            root: Main Tkinter root window
        """
        self.root = root
        self.notebook = notebook

        # State
        self.last_enhanced_prompt = None
        self.prompt_enhancer = None
        self.ollama_enhancer = None

        # Create the tab
        self.frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame, text="💬 Prompt Enhancer")

        # Build UI
        self._create_ui()

        # Initialize enhancers in background
        threading.Thread(target=self._init_prompt_enhancers, daemon=True).start()

    def _create_ui(self):
        """Create the UI components"""
        # Title
        ttk.Label(self.frame, text="AI Prompt Enhancer Chat",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Status bar
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(
            status_frame,
            text="⏳ Initializing...",
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(status_frame, text="🔄 Refresh",
                  command=self._refresh_status).pack(side=tk.RIGHT, padx=5)

        # Main content
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Left - Chat
        self._create_chat_area(content_frame)

        # Right - Settings
        self._create_settings_area(content_frame)

        # Add welcome message
        self._add_chat_message("system", "Welcome! Enter a simple prompt to enhance it.")

    def _create_chat_area(self, parent):
        """Create the chat area"""
        chat_frame = ttk.LabelFrame(parent, text="Chat", padding="10")
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            height=20,
            wrap=tk.WORD,
            state='disabled',
            font=('Arial', 10)
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Configure tags
        self.chat_history.tag_config('user', foreground='#4CAF50', font=('Arial', 10, 'bold'))
        self.chat_history.tag_config('ai', foreground='#2196F3', font=('Arial', 10, 'bold'))
        self.chat_history.tag_config('system', foreground='#FF9800', font=('Arial', 9, 'italic'))
        self.chat_history.tag_config('error', foreground='#F44336')
        self.chat_history.tag_config('prompt', foreground='#333', font=('Arial', 10))

        # Input area
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Your Prompt:").pack(anchor=tk.W)

        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=('Arial', 10)
        )
        self.input_text.pack(fill=tk.X, pady=(2, 5))

        # Buttons
        btn_row = ttk.Frame(input_frame)
        btn_row.pack(fill=tk.X)

        ttk.Button(btn_row, text="✨ Enhance",
                  command=self.enhance_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="📋 Copy Last",
                  command=self.copy_last).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row, text="🗑️ Clear",
                  command=self.clear_chat).pack(side=tk.LEFT, padx=2)

        # Bind Ctrl+Enter
        self.input_text.bind('<Control-Return>', lambda e: self.enhance_prompt())

    def _create_settings_area(self, parent):
        """Create settings panel"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        # Settings
        settings_frame = ttk.LabelFrame(right_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Backend
        ttk.Label(settings_frame, text="Backend:").pack(anchor=tk.W)
        self.backend_var = tk.StringVar(value="auto")
        for text, value in [
            ("Auto (Best)", "auto"),
            ("Prompt Quill", "quill"),
            ("Ollama", "ollama")
        ]:
            ttk.Radiobutton(
                settings_frame,
                text=text,
                variable=self.backend_var,
                value=value
            ).pack(anchor=tk.W, padx=10)

        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Style
        ttk.Label(settings_frame, text="Style:").pack(anchor=tk.W, pady=(5, 2))
        self.style_var = tk.StringVar(value="cinematic")
        ttk.Combobox(
            settings_frame,
            textvariable=self.style_var,
            values=["cinematic", "photorealistic", "anime", "oil painting",
                   "digital art", "concept art", "3d render"],
            state='readonly',
            width=18
        ).pack(fill=tk.X)

        ttk.Separator(settings_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # Quality tags
        self.quality_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Add Quality Tags",
            variable=self.quality_var
        ).pack(anchor=tk.W)

        # Info
        info_frame = ttk.LabelFrame(right_frame, text="Quick Start", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True)

        info = """1. Enter a prompt
   e.g. "rocket man"

2. Press Ctrl+Enter
   or click Enhance

3. Copy the enhanced
   prompt for use

Backends:
• Prompt Quill: Best
  (needs setup)
• Ollama: Local LLM
• Auto: Uses best

Shortcuts:
  Ctrl+Enter: Enhance
"""
        ttk.Label(
            info_frame,
            text=info,
            justify=tk.LEFT,
            foreground='gray',
            font=('Arial', 9)
        ).pack()

        # Actions
        actions_frame = ttk.LabelFrame(right_frame, text="Actions", padding="10")
        actions_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            actions_frame,
            text="📚 Examples",
            command=self.show_examples
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            actions_frame,
            text="ℹ️ Status",
            command=self.show_status
        ).pack(fill=tk.X, pady=2)

    def _init_prompt_enhancers(self):
        """Initialize enhancers in background"""
        try:
            from story_illustrator.prompt_quill import OllamaPromptEnhancer, PromptEnhancer

            self.ollama_enhancer = OllamaPromptEnhancer()
            self.prompt_enhancer = PromptEnhancer()

            backends = []
            if self.prompt_enhancer and self.prompt_enhancer.is_available():
                backends.append("Prompt Quill")
            if self.ollama_enhancer and self.ollama_enhancer.is_available:
                backends.append("Ollama")

            if backends:
                status = f"✅ Ready - {', '.join(backends)}"
                self._add_chat_message("system", f"Initialized: {', '.join(backends)}")
            else:
                status = "⚠️ No backends available"
                self._add_chat_message("error", "No enhancers available. Install Ollama or Prompt Quill.")

            self.root.after(0, lambda: self.status_label.config(text=status))

        except ImportError as e:
            status = f"❌ Import Error"
            self.root.after(0, lambda: self.status_label.config(text=status))
            self.root.after(0, lambda: self._add_chat_message("error",
                f"Failed to import: {str(e)}"))

    def _add_chat_message(self, role, message):
        """Add message to chat"""
        def _add():
            self.chat_history.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")

            if role == "user":
                self.chat_history.insert(tk.END, f"[{timestamp}] ", 'system')
                self.chat_history.insert(tk.END, "You: ", 'user')
                self.chat_history.insert(tk.END, f"{message}\n\n", 'prompt')
            elif role == "ai":
                self.chat_history.insert(tk.END, f"[{timestamp}] ", 'system')
                self.chat_history.insert(tk.END, "Enhanced: ", 'ai')
                self.chat_history.insert(tk.END, f"{message}\n\n", 'prompt')
            elif role == "system":
                self.chat_history.insert(tk.END, f"[{timestamp}] {message}\n", 'system')
            elif role == "error":
                self.chat_history.insert(tk.END, f"[{timestamp}] ERROR: {message}\n", 'error')

            self.chat_history.config(state='disabled')
            self.chat_history.see(tk.END)

        self.root.after(0, _add)

    def enhance_prompt(self):
        """Enhance user's prompt"""
        prompt = self.input_text.get('1.0', tk.END).strip()

        if not prompt:
            messagebox.showwarning("Empty", "Enter a prompt first!")
            return

        self._add_chat_message("user", prompt)
        self.input_text.delete('1.0', tk.END)

        threading.Thread(target=self._enhance_thread, args=(prompt,), daemon=True).start()

    def _enhance_thread(self, prompt):
        """Enhance in background"""
        try:
            backend = self.backend_var.get()
            style = self.style_var.get()
            quality = self.quality_var.get()

            enhanced = None
            backend_used = None

            if backend == "auto":
                # Try Prompt Quill first
                if self.prompt_enhancer and self.prompt_enhancer.is_available():
                    result = self.prompt_enhancer.enhance_image_prompt(prompt)
                    if result.get('success'):
                        enhanced = result['enhanced_prompt']
                        backend_used = "Prompt Quill"

                # Fallback to Ollama
                if not enhanced and self.ollama_enhancer and self.ollama_enhancer.is_available:
                    result = self.ollama_enhancer.enhance_image_prompt(
                        prompt, style=style, add_quality_tags=quality
                    )
                    if result.get('success'):
                        enhanced = result['enhanced_prompt']
                        backend_used = "Ollama"

            elif backend == "quill":
                if self.prompt_enhancer and self.prompt_enhancer.is_available():
                    result = self.prompt_enhancer.enhance_image_prompt(prompt)
                    if result.get('success'):
                        enhanced = result['enhanced_prompt']
                        backend_used = "Prompt Quill"
                else:
                    self._add_chat_message("error", "Prompt Quill not available")
                    return

            elif backend == "ollama":
                if self.ollama_enhancer and self.ollama_enhancer.is_available:
                    result = self.ollama_enhancer.enhance_image_prompt(
                        prompt, style=style, add_quality_tags=quality
                    )
                    if result.get('success'):
                        enhanced = result['enhanced_prompt']
                        backend_used = "Ollama"
                else:
                    self._add_chat_message("error", "Ollama not available")
                    return

            if enhanced:
                self.last_enhanced_prompt = enhanced
                self._add_chat_message("ai", enhanced)
                self._add_chat_message("system", f"Used: {backend_used}")
            else:
                self._add_chat_message("error", "No backends available")

        except Exception as e:
            self._add_chat_message("error", f"Failed: {str(e)}")

    def copy_last(self):
        """Copy last enhanced prompt"""
        if self.last_enhanced_prompt:
            pyperclip.copy(self.last_enhanced_prompt)
            messagebox.showinfo("Copied!", "Enhanced prompt copied!")
        else:
            messagebox.showwarning("No Prompt", "No enhanced prompt yet!")

    def clear_chat(self):
        """Clear chat history"""
        self.chat_history.config(state='normal')
        self.chat_history.delete('1.0', tk.END)
        self.chat_history.config(state='disabled')
        self._add_chat_message("system", "Chat cleared!")

    def _refresh_status(self):
        """Refresh status"""
        threading.Thread(target=self._init_prompt_enhancers, daemon=True).start()

    def show_examples(self):
        """Show example prompts"""
        examples = [
            "rocket man in space",
            "medieval knight",
            "cyberpunk city",
            "mountain landscape",
            "robot portrait"
        ]

        win = tk.Toplevel(self.root)
        win.title("Examples")
        win.geometry("350x250")

        ttk.Label(win, text="Click to use:", font=('Arial', 12, 'bold')).pack(pady=10)

        for ex in examples:
            ttk.Button(
                win,
                text=ex,
                command=lambda e=ex: self._use_example(e, win)
            ).pack(fill=tk.X, padx=20, pady=3)

    def _use_example(self, example, window):
        """Use example"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', example)
        window.destroy()
        self.enhance_prompt()

    def show_status(self):
        """Show service status"""
        info = "=== Services Status ===\n\n"

        if self.ollama_enhancer:
            status = self.ollama_enhancer.get_status()
            info += f"Ollama:\n  Available: {status['available']}\n  Model: {status['model']}\n"
            if status['error']:
                info += f"  Error: {status['error']}\n"
        else:
            info += "Ollama: Not initialized\n"

        info += "\n"

        if self.prompt_enhancer:
            info += f"Prompt Quill:\n  {self.prompt_enhancer.get_status_message()}\n"
        else:
            info += "Prompt Quill: Not initialized\n"

        info += "\n=== URLs ===\n"
        info += "Qdrant: http://localhost:6333/dashboard\n"
        info += "Prompt Quill: http://localhost:64738\n"
        info += "Ollama: http://localhost:11434\n"

        win = tk.Toplevel(self.root)
        win.title("Status")
        win.geometry("450x350")

        text = scrolledtext.ScrolledText(win, font=('Courier', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', info)
        text.config(state='disabled')

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=5)
