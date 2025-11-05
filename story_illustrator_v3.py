#!/usr/bin/env python3
"""
Story Illustrator V3 - Clean Modular Version

A complete workflow tool for creating illustrated story videos:
- Phase 1: Story chunking (manual or API-based)
- Phase 2: Automated image generation prompts
- Phase 3: Video rendering with FFmpeg
- Phase 4: Multi-language SRT translation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from pathlib import Path
from datetime import datetime
import pyautogui
import pyperclip
import re

# Import our modular components
from story_illustrator.utils.config import ConfigManager
from story_illustrator.core.project_manager import ProjectManager
from story_illustrator.core.phase1_logic import StoryChunker
from story_illustrator.core.phase2_logic import ImageGenerator
from story_illustrator.core.phase3_logic import VideoRenderer
from story_illustrator.core.phase4_logic import SRTTranslator, WhisperTranscriber
from story_illustrator.utils.videoswarm_launcher import VideoSwarmLauncher

# Try to import TTS (requires PyTorch, may fail)
try:
    from story_illustrator.core.tts_generator import TTSGenerator
    from story_illustrator.utils.voice_manager import VoicePreset, VoiceManager
    TTS_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Warning: TTS module not available: {e}")
    TTS_AVAILABLE = False
    TTSGenerator = None
    VoicePreset = None
    VoiceManager = None

# Import DengeAI Prompt Builder
try:
    from story_illustrator.utils.dengeai_prompt_builder import DengeAIPromptBuilder
    from story_illustrator.utils.prompt_image_mapper import PromptImageMapper
    from PIL import Image, ImageTk
    DENGEAI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: DengeAI Prompt Builder not available: {e}")
    DENGEAI_AVAILABLE = False
    DengeAIPromptBuilder = None
    PromptImageMapper = None

# Import Prompt Enhancer Chat UI
from story_illustrator.ui import PromptEnhancerTab


class StoryIllustratorApp:
    """Main application for Story Illustrator"""

    def __init__(self, root):
        self.root = root
        self.root.title("📖 Story Illustrator V3 - Modular Edition")
        self.root.geometry("1000x950")
        self.root.resizable(True, True)

        # Initialize managers
        self.config = ConfigManager()
        self.project_manager = ProjectManager()
        self.story_chunker = StoryChunker(logger=self.log)
        self.image_generator = ImageGenerator(logger=self.log)
        self.tts_generator = TTSGenerator(logger=self.log) if TTS_AVAILABLE else None
        self.videoswarm_launcher = VideoSwarmLauncher()

        # State
        self.sections = []
        self.current_project_name = None
        self.is_running = False

        # Folders
        self.output_folder = Path.cwd() / "story_images"
        self.output_folder.mkdir(exist_ok=True)

        # Create UI
        self.create_ui()

        # Load existing projects
        self.refresh_project_list()

        # Bind close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        """Create the main user interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create main tabs
        self.create_settings_tab()
        self.create_sleep_videos_notebook()
        self.create_actor_filmography_tab()
        self.create_dengeai_prompt_builder_tab()

        # Add Prompt Enhancer Chat tab
        PromptEnhancerTab(self.notebook, self.root)

    # ========== SETTINGS TAB ==========

    def create_settings_tab(self):
        """Create Settings tab for API keys"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="⚙️ Settings")

        ttk.Label(frame, text="Application Settings",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))

        # API Keys section
        api_frame = ttk.LabelFrame(frame, text="API Keys", padding="20")
        api_frame.pack(fill=tk.X, pady=10)

        # OpenAI API Key
        api_row = ttk.Frame(api_frame)
        api_row.pack(fill=tk.X, pady=10)
        ttk.Label(api_row, text="OpenAI API Key:", width=20).pack(side=tk.LEFT, padx=5)
        self.api_key_var = tk.StringVar(value=self.config.get('openai_api_key', ''))
        ttk.Entry(api_row, textvariable=self.api_key_var, width=60, show='*').pack(side=tk.LEFT, padx=5)
        self.api_key_var.trace('w', lambda *args: self.config.set('openai_api_key', self.api_key_var.get()))

        ttk.Label(api_frame, text="Get your API key at: https://platform.openai.com/api-keys",
                 foreground='#569cd6', font=('Arial', 9)).pack(pady=5)

        # Perplexity API Key
        perplexity_row = ttk.Frame(api_frame)
        perplexity_row.pack(fill=tk.X, pady=10)
        ttk.Label(perplexity_row, text="Perplexity API Key:", width=20).pack(side=tk.LEFT, padx=5)
        self.perplexity_key_var = tk.StringVar(value=self.config.get('perplexity_api_key', ''))
        ttk.Entry(perplexity_row, textvariable=self.perplexity_key_var, width=60, show='*').pack(side=tk.LEFT, padx=5)
        self.perplexity_key_var.trace('w', lambda *args: self.config.set('perplexity_api_key', self.perplexity_key_var.get()))

        ttk.Label(api_frame, text="Get your API key at: https://www.perplexity.ai/settings/api",
                 foreground='#569cd6', font=('Arial', 9)).pack(pady=5)

        # TMDB API Key
        tmdb_row = ttk.Frame(api_frame)
        tmdb_row.pack(fill=tk.X, pady=10)
        ttk.Label(tmdb_row, text="TMDB API Key:", width=20).pack(side=tk.LEFT, padx=5)
        self.tmdb_key_var = tk.StringVar(value=self.config.get('tmdb_api_key', ''))
        ttk.Entry(tmdb_row, textvariable=self.tmdb_key_var, width=60, show='*').pack(side=tk.LEFT, padx=5)
        self.tmdb_key_var.trace('w', lambda *args: self.config.set('tmdb_api_key', self.tmdb_key_var.get()))

        ttk.Label(api_frame, text="Get your API key at: https://www.themoviedb.org/settings/api",
                 foreground='#569cd6', font=('Arial', 9)).pack(pady=5)

        # Instructions
        info_frame = ttk.LabelFrame(frame, text="About API Usage", padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        info_text = """
API Usage:
• OpenAI: Story chunking, SRT generation, translations (optional - for sleep videos)
• Perplexity: Actor filmography research (~$0.005 per query)
• TMDB: Movie poster downloads (free tier available)

Actor Filmography Feature:
• Research any actor's complete filmography
• Download all movie posters automatically
• Generate professional carousel videos

All API keys are stored locally in .env file and never shared.
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, foreground='gray').pack()

    # ========== PHASE 1: STORY CHUNKING ==========

    def create_phase1_tab(self):
        """Create Phase 1 UI - Story Chunking"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📝 Phase 1: Story Chunking")

        ttk.Label(frame, text="Phase 1: Chunk Your Story",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Story input
        story_frame = ttk.LabelFrame(frame, text="Your Story", padding="10")
        story_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_row = ttk.Frame(story_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_row, text="📂 Load File", command=self.load_story_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="📋 Copy to Clipboard", command=self.copy_story).pack(side=tk.LEFT, padx=5)

        self.story_text = scrolledtext.ScrolledText(story_frame, height=12, width=90)
        self.story_text.pack(fill=tk.BOTH, expand=True)

        # Chunking options
        chunk_frame = ttk.LabelFrame(frame, text="Chunking Options", padding="10")
        chunk_frame.pack(fill=tk.X, pady=5)

        ttk.Button(chunk_frame, text="🤖 Chunk via API (Automatic)",
                  command=self.chunk_via_api).pack(side=tk.LEFT, padx=5)
        ttk.Button(chunk_frame, text="📋 Copy Prompt (Manual)",
                  command=self.copy_chunking_prompt).pack(side=tk.LEFT, padx=5)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.phase1_log = scrolledtext.ScrolledText(log_frame, height=6, state='disabled')
        self.phase1_log.pack(fill=tk.BOTH, expand=True)

        # Instructions
        ttk.Label(frame, text="• API: Automatic chunking using GPT-4o-mini\n• Manual: Copy prompt, paste to ChatGPT, then go to Phase 2",
                 foreground='gray').pack(pady=5)

    def load_story_file(self):
        """Load story from file"""
        filename = filedialog.askopenfilename(
            title="Select Story File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.story_text.delete('1.0', tk.END)
                self.story_text.insert('1.0', f.read())

    def copy_story(self):
        """Copy story to clipboard"""
        story = self.story_text.get('1.0', tk.END).strip()
        if story:
            pyperclip.copy(story)
            messagebox.showinfo("Copied!", "Story copied to clipboard!")

    def copy_chunking_prompt(self):
        """Copy chunking prompt with story"""
        story = self.story_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("Error", "Please load a story first!")
            return

        prompt = self.story_chunker.generate_chunking_prompt(story)
        pyperclip.copy(prompt)
        messagebox.showinfo("Copied!",
            "Prompt copied to clipboard!\n\n"
            "Next: Paste into ChatGPT → Copy response → Phase 2")

    def chunk_via_api(self):
        """Chunk story via OpenAI API"""
        story = self.story_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("Error", "Please load a story first!")
            return

        api_key = self.config.get('openai_api_key', '').strip()
        if not api_key:
            messagebox.showerror("Error",
                "OpenAI API key required!\n\n"
                "Enter it in Phase 3 first.")
            return

        self.log("🤖 Starting API chunking...", "INFO", self.phase1_log)
        thread = threading.Thread(
            target=self._chunk_via_api_worker,
            args=(story, api_key),
            daemon=True
        )
        thread.start()

    def _chunk_via_api_worker(self, story, api_key):
        """Worker thread for API chunking"""
        try:
            from openai import OpenAI
            import httpx

            client = OpenAI(api_key=api_key, timeout=httpx.Timeout(300.0, connect=10.0))

            prompt = self.story_chunker.generate_chunking_prompt(story)

            self.log(f"📤 Sending to OpenAI ({len(story)} chars)...", "INFO", self.phase1_log)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            chunked_text = response.choices[0].message.content
            self.log(f"✅ Received response ({len(chunked_text)} chars)", "SUCCESS", self.phase1_log)

            # Parse sections
            self.sections = self.story_chunker.parse_sections(chunked_text)

            if self.sections:
                # Save project
                if not self.current_project_name:
                    self.current_project_name = self.project_manager.generate_project_name(
                        self.sections[0]['title']
                    )

                self.project_manager.save_project(self.current_project_name, self.sections)
                self.log(f"💾 Project saved: {len(self.sections)} sections", "SUCCESS", self.phase1_log)

                # Update TTS tab project label
                if hasattr(self, 'tts_project_label'):
                    self.tts_project_label.config(text=self.current_project_name, foreground='green')

                # Update Phase 2
                self.update_phase2_with_sections(chunked_text)
                self.refresh_project_list()

                messagebox.showinfo("Success!",
                    f"✅ Chunked into {len(self.sections)} sections!\n\n"
                    "Project saved. Ready for Phase 2!")
            else:
                self.log("❌ Failed to parse sections", "ERROR", self.phase1_log)

        except Exception as e:
            self.log(f"❌ API error: {e}", "ERROR", self.phase1_log)
            messagebox.showerror("Error", f"API chunking failed:\n\n{e}")

    # ========== PHASE 2: IMAGE GENERATION ==========

    def create_phase2_tab(self):
        """Create Phase 2 UI - Image Generation"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🎨 Phase 2: Generate Images")

        ttk.Label(frame, text="Phase 2: Auto-Generate Image Prompts",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Project selector and sections
        selector_frame = ttk.LabelFrame(frame, text="Load Project", padding="10")
        selector_frame.pack(fill=tk.X, pady=5)

        row = ttk.Frame(selector_frame)
        row.pack(fill=tk.X)

        ttk.Label(row, text="Project:").pack(side=tk.LEFT, padx=5)
        self.phase2_project_var = tk.StringVar()
        self.phase2_project_combo = ttk.Combobox(row, textvariable=self.phase2_project_var,
                                                  width=40, state='readonly')
        self.phase2_project_combo.pack(side=tk.LEFT, padx=5)
        self.phase2_project_combo.bind('<<ComboboxSelected>>', self.load_project_phase2)
        ttk.Button(row, text="🔄", command=self.refresh_project_list, width=3).pack(side=tk.LEFT)

        # Sections display
        sections_frame = ttk.LabelFrame(frame, text="Sections", padding="10")
        sections_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.sections_text = scrolledtext.ScrolledText(sections_frame, height=10)
        self.sections_text.pack(fill=tk.BOTH, expand=True)

        # Automation controls
        control_frame = ttk.LabelFrame(frame, text="Automation Settings", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Images per section:").pack(side=tk.LEFT, padx=5)
        self.images_per_section = tk.IntVar(value=4)
        ttk.Spinbox(row1, from_=1, to=10, textvariable=self.images_per_section,
                   width=5).pack(side=tk.LEFT)

        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Delay after prompt (seconds):").pack(side=tk.LEFT, padx=5)
        self.delay_after_prompt = tk.IntVar(value=150)
        ttk.Spinbox(row2, from_=30, to=600, textvariable=self.delay_after_prompt,
                   width=8).pack(side=tk.LEFT)

        # Start/Stop buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="▶️ Start Automation", command=self.start_automation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⏹️ Stop", command=self.stop_automation).pack(side=tk.LEFT, padx=5)

        # Progress
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill=tk.X, pady=5)
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack()

    def update_phase2_with_sections(self, text):
        """Update Phase 2 with parsed sections"""
        self.sections_text.delete('1.0', tk.END)
        self.sections_text.insert('1.0', text)

    def load_project_phase2(self, event=None):
        """Load selected project in Phase 2"""
        project_name = self.phase2_project_var.get()
        if not project_name:
            return

        project_data = self.project_manager.load_project(project_name)
        if project_data:
            self.sections = project_data['sections']
            self.current_project_name = project_name

            # Update TTS tab project label
            if hasattr(self, 'tts_project_label'):
                self.tts_project_label.config(text=project_name, foreground='green')

            # Display sections
            display_text = ""
            for i, section in enumerate(self.sections, 1):
                display_text += f"=== SECTION {i}: {section['title']} ===\n{section['text']}\n\n"
            self.sections_text.delete('1.0', tk.END)
            self.sections_text.insert('1.0', display_text.strip())

            messagebox.showinfo("Success!", f"Loaded {len(self.sections)} sections!")

    def start_automation(self):
        """Start image generation automation"""
        if not self.sections:
            messagebox.showerror("Error", "No sections loaded! Load a project or chunk a story first.")
            return

        self.is_running = True
        self.image_generator.automate_all_sections(
            self.sections,
            images_per_section=self.images_per_section.get(),
            delay_after_prompt=self.delay_after_prompt.get(),
            delay_between_go_on=self.delay_after_prompt.get()
        )

    def stop_automation(self):
        """Stop automation"""
        self.is_running = False
        self.image_generator.stop()

    # ========== PHASE 2.5: TTS NARRATION ==========

    def create_phase25_tab(self):
        """Create Phase 2.5 UI - TTS Narration"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🎙️ Phase 2.5: Narration")

        ttk.Label(frame, text="AI Voiceover Generation",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Project selection
        project_frame = ttk.LabelFrame(frame, text="Project", padding="10")
        project_frame.pack(fill=tk.X, pady=10)

        proj_row = ttk.Frame(project_frame)
        proj_row.pack(fill=tk.X)
        ttk.Label(proj_row, text="Current Project:", width=15).pack(side=tk.LEFT, padx=5)
        self.tts_project_label = ttk.Label(proj_row, text="No project loaded", foreground='red')
        self.tts_project_label.pack(side=tk.LEFT, padx=5)

        # Voice settings
        voice_frame = ttk.LabelFrame(frame, text="Voice Settings", padding="10")
        voice_frame.pack(fill=tk.X, pady=10)

        # Reference audio
        ref_row = ttk.Frame(voice_frame)
        ref_row.pack(fill=tk.X, pady=5)
        ttk.Label(ref_row, text="Reference Voice:", width=15).pack(side=tk.LEFT, padx=5)
        self.tts_ref_path_var = tk.StringVar(value="")
        ttk.Entry(ref_row, textvariable=self.tts_ref_path_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(ref_row, text="Browse", command=self.browse_reference_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(ref_row, text="Clear", command=lambda: self.tts_ref_path_var.set("")).pack(side=tk.LEFT)

        ttk.Label(voice_frame, text="Leave empty for default voice. Upload 3-15s audio for voice cloning.",
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W, padx=5)

        # TTS Parameters
        params_frame = ttk.LabelFrame(frame, text="Voice Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=10)

        # Exaggeration
        exp_row = ttk.Frame(params_frame)
        exp_row.pack(fill=tk.X, pady=5)
        ttk.Label(exp_row, text="Exaggeration:", width=15).pack(side=tk.LEFT)
        self.tts_exaggeration_var = tk.DoubleVar(value=0.5)
        ttk.Scale(exp_row, from_=0.25, to=2.0, variable=self.tts_exaggeration_var,
                 orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=5)
        ttk.Label(exp_row, textvariable=self.tts_exaggeration_var, width=5).pack(side=tk.LEFT)
        ttk.Label(exp_row, text="(0.5 = neutral)", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=5)

        # Temperature
        temp_row = ttk.Frame(params_frame)
        temp_row.pack(fill=tk.X, pady=5)
        ttk.Label(temp_row, text="Temperature:", width=15).pack(side=tk.LEFT)
        self.tts_temperature_var = tk.DoubleVar(value=0.8)
        ttk.Scale(temp_row, from_=0.05, to=2.0, variable=self.tts_temperature_var,
                 orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=5)
        ttk.Label(temp_row, textvariable=self.tts_temperature_var, width=5).pack(side=tk.LEFT)

        # CFG Weight
        cfg_row = ttk.Frame(params_frame)
        cfg_row.pack(fill=tk.X, pady=5)
        ttk.Label(cfg_row, text="CFG/Pace:", width=15).pack(side=tk.LEFT)
        self.tts_cfg_var = tk.DoubleVar(value=0.5)
        ttk.Scale(cfg_row, from_=0.0, to=1.0, variable=self.tts_cfg_var,
                 orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=5)
        ttk.Label(cfg_row, textvariable=self.tts_cfg_var, width=5).pack(side=tk.LEFT)

        # Generation options
        options_frame = ttk.LabelFrame(frame, text="Generation Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        self.tts_combine_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Combine all sections into single audio file",
                       variable=self.tts_combine_var).pack(anchor=tk.W)

        # Generate button
        gen_frame = ttk.Frame(frame)
        gen_frame.pack(fill=tk.X, pady=20)

        self.tts_generate_btn = ttk.Button(gen_frame, text="🎙️ Generate Narration",
                                          command=self.generate_narration, style='Accent.TButton')
        self.tts_generate_btn.pack(side=tk.LEFT, padx=5)

        self.tts_status_label = ttk.Label(gen_frame, text="", foreground='blue')
        self.tts_status_label.pack(side=tk.LEFT, padx=10)

        # Progress log
        log_frame = ttk.LabelFrame(frame, text="Generation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tts_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.tts_log.pack(fill=tk.BOTH, expand=True)

    def browse_reference_audio(self):
        """Browse for reference audio file"""
        path = filedialog.askopenfilename(
            title="Select Reference Audio (3-15 seconds)",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.m4a *.flac"),
                ("All Files", "*.*")
            ]
        )
        if path:
            self.tts_ref_path_var.set(path)

    def generate_narration(self):
        """Generate TTS narration for story sections"""
        if not self.current_project_name:
            messagebox.showwarning("No Project", "Please load a project first!")
            return

        if not self.sections:
            messagebox.showwarning("No Sections", "Please create story sections first in Phase 1!")
            return

        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._generate_narration_thread, daemon=True)
        thread.start()

    def _generate_narration_thread(self):
        """Thread worker for TTS generation"""
        try:
            self.tts_generate_btn.config(state='disabled')
            self.tts_status_label.config(text="Generating...", foreground='orange')

            # Extract text from sections
            sections_text = []
            for section in self.sections:
                if isinstance(section, dict):
                    sections_text.append(section.get('text', ''))
                else:
                    sections_text.append(str(section))

            # Prepare output directory
            project_dir = Path("projects") / self.current_project_name
            audio_dir = project_dir / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            # Get parameters
            ref_audio = self.tts_ref_path_var.get() or None
            if ref_audio and not Path(ref_audio).exists():
                ref_audio = None

            # Generate narration
            narration_path = self.tts_generator.generate_narration_for_sections(
                sections=sections_text,
                output_dir=audio_dir,
                combine=self.tts_combine_var.get(),
                audio_prompt_path=ref_audio,
                exaggeration=self.tts_exaggeration_var.get(),
                temperature=self.tts_temperature_var.get(),
                cfg_weight=self.tts_cfg_var.get()
            )

            if narration_path:
                # Auto-generate subtitles from narration
                self.tts_status_label.config(text="🎬 Generating subtitles...", foreground='blue')
                self.log("🎬 Auto-generating subtitles from narration...", "INFO", self.tts_log)

                # Create Whisper transcriber
                from story_illustrator.core.phase4_logic import WhisperTranscriber
                whisper = WhisperTranscriber(logger=self.log_to_tts)

                # Generate SRT
                srt_path = whisper.transcribe_to_srt(narration_path)

                if srt_path:
                    self.tts_status_label.config(text=f"✅ Complete! Audio + Subtitles saved!", foreground='green')
                    messagebox.showinfo("Success",
                        f"Narration generated successfully!\n\n"
                        f"Audio: {narration_path.name}\n"
                        f"Subtitles: {srt_path.name}\n\n"
                        f"Both saved to: {narration_path.parent}")
                else:
                    self.tts_status_label.config(text=f"✅ Audio saved (subtitles failed)", foreground='orange')
                    messagebox.showwarning("Partial Success",
                        f"Narration generated successfully!\n\nSaved to: {narration_path}\n\n"
                        f"(Subtitle generation failed - check log)")
            else:
                self.tts_status_label.config(text="❌ Generation failed", foreground='red')
                messagebox.showerror("Error", "Narration generation failed. Check the log for details.")

        except Exception as e:
            self.log(f"TTS generation error: {e}", "ERROR")
            self.tts_status_label.config(text=f"❌ Error: {str(e)}", foreground='red')
            messagebox.showerror("Error", f"TTS generation failed:\n{e}")
        finally:
            self.tts_generate_btn.config(state='normal')

    # ========== PHASE 3: VIDEO PRODUCTION ==========

    def create_phase3_tab(self):
        """Create Phase 3 UI - Video Production"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🎬 Phase 3: Create Videos")

        ttk.Label(frame, text="Phase 3: Render Videos with FFmpeg",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Project/Section selector
        selector_frame = ttk.LabelFrame(frame, text="Select Content", padding="10")
        selector_frame.pack(fill=tk.X, pady=5)

        # Project row
        proj_row = ttk.Frame(selector_frame)
        proj_row.pack(fill=tk.X, pady=2)
        ttk.Label(proj_row, text="Project:").pack(side=tk.LEFT, padx=5)
        self.phase3_project_var = tk.StringVar()
        self.phase3_project_combo = ttk.Combobox(proj_row, textvariable=self.phase3_project_var,
                                                  width=35, state='readonly')
        self.phase3_project_combo.pack(side=tk.LEFT, padx=5)
        self.phase3_project_combo.bind('<<ComboboxSelected>>', self.load_project_phase3)
        ttk.Button(proj_row, text="🔄", command=self.refresh_project_list, width=3).pack(side=tk.LEFT)

        # Section row
        sect_row = ttk.Frame(selector_frame)
        sect_row.pack(fill=tk.X, pady=2)
        ttk.Label(sect_row, text="Section:").pack(side=tk.LEFT, padx=5)
        self.section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(sect_row, textvariable=self.section_var,
                                          width=50, state='readonly')
        self.section_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Video settings
        settings_frame = ttk.LabelFrame(frame, text="Video Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        # Video parameters
        params_frame = ttk.Frame(settings_frame)
        params_frame.pack(fill=tk.X, pady=5)

        # Row 1: Duration and Transition
        row1 = ttk.Frame(params_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Image Duration (sec):").pack(side=tk.LEFT, padx=5)
        self.duration_var = tk.IntVar(value=5)
        ttk.Spinbox(row1, from_=1, to=30, textvariable=self.duration_var, width=5).pack(side=tk.LEFT)

        ttk.Label(row1, text="Transition:").pack(side=tk.LEFT, padx=(20, 5))
        self.transition_var = tk.StringVar(value='crossfade')
        ttk.Combobox(row1, textvariable=self.transition_var, values=['crossfade', 'none'],
                    width=10, state='readonly').pack(side=tk.LEFT)

        ttk.Label(row1, text="Duration (sec):").pack(side=tk.LEFT, padx=(10, 5))
        self.transition_duration_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(row1, from_=0.1, to=5.0, increment=0.1, textvariable=self.transition_duration_var,
                   width=5).pack(side=tk.LEFT)

        # Row 2: Resolution and FPS
        row2 = ttk.Frame(params_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Resolution:").pack(side=tk.LEFT, padx=5)
        self.resolution_var = tk.StringVar(value='1920x1080')
        ttk.Combobox(row2, textvariable=self.resolution_var,
                    values=['1920x1080', '1280x720', '3840x2160'],
                    width=12, state='readonly').pack(side=tk.LEFT)

        ttk.Label(row2, text="FPS:").pack(side=tk.LEFT, padx=(20, 5))
        self.fps_var = tk.IntVar(value=30)
        ttk.Spinbox(row2, from_=15, to=60, textvariable=self.fps_var, width=5).pack(side=tk.LEFT)

        ttk.Label(row2, text="Music Volume:").pack(side=tk.LEFT, padx=(20, 5))
        self.music_volume_var = tk.IntVar(value=30)
        ttk.Spinbox(row2, from_=0, to=100, textvariable=self.music_volume_var, width=5).pack(side=tk.LEFT)
        ttk.Label(row2, text="%").pack(side=tk.LEFT)

        # Audio files
        audio_frame = ttk.LabelFrame(settings_frame, text="Audio", padding="5")
        audio_frame.pack(fill=tk.X, pady=5)

        self.voiceover_var = tk.StringVar()
        self.srt_var = tk.StringVar()
        self.music_var = tk.StringVar()

        # Voiceover
        row = ttk.Frame(audio_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Voiceover:", width=15).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.voiceover_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_voiceover).pack(side=tk.LEFT)
        ttk.Button(row, text="🗜️ Compress", command=self.compress_audio).pack(side=tk.LEFT, padx=5)

        # SRT Subtitles
        row = ttk.Frame(audio_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="SRT Subtitles:", width=15).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.srt_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_srt).pack(side=tk.LEFT)
        ttk.Button(row, text="🎤 Generate from Voiceover", command=self.generate_srt).pack(side=tk.LEFT, padx=5)

        # Background Music
        row = ttk.Frame(audio_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Background Music:", width=15).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.music_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_music).pack(side=tk.LEFT)

        # Render button
        render_btn_frame = ttk.Frame(settings_frame)
        render_btn_frame.pack(pady=10)
        ttk.Button(render_btn_frame, text="🎬 Render Video", command=self.render_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(render_btn_frame, text="📂 Open Videos Folder", command=self.open_videos_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(render_btn_frame, text="▶️ Open Last Video", command=self.open_last_video).pack(side=tk.LEFT, padx=5)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Render Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.phase3_log = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.phase3_log.pack(fill=tk.BOTH, expand=True)

    def load_project_phase3(self, event=None):
        """Load project in Phase 3"""
        project_name = self.phase3_project_var.get()
        if not project_name:
            return

        project_data = self.project_manager.load_project(project_name)
        if project_data:
            self.sections = project_data['sections']

            # Update section dropdown
            section_names = [f"section_{i+1:02d}_{self.story_chunker.sanitize_filename(s['title'])}"
                           for i, s in enumerate(self.sections)]
            self.section_combo['values'] = section_names

    def browse_voiceover(self):
        """Browse for voiceover file"""
        filename = filedialog.askopenfilename(
            title="Select Voiceover Audio",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a"), ("All files", "*.*")]
        )
        if filename:
            self.voiceover_var.set(filename)

    def browse_srt(self):
        """Browse for SRT file"""
        filename = filedialog.askopenfilename(
            title="Select SRT File",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if filename:
            self.srt_var.set(filename)

    def browse_music(self):
        """Browse for music file"""
        filename = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a"), ("All files", "*.*")]
        )
        if filename:
            self.music_var.set(filename)

    def compress_audio(self):
        """Compress audio file to under 25MB for Whisper API"""
        voiceover = self.voiceover_var.get()
        if not voiceover or not Path(voiceover).exists():
            messagebox.showerror("Error", "Please select a voiceover file first!")
            return

        # Check file size
        file_size_mb = Path(voiceover).stat().st_size / (1024 * 1024)
        if file_size_mb <= 25:
            messagebox.showinfo("Info", f"File is already small enough ({file_size_mb:.1f} MB < 25 MB limit)")
            return

        self.log(f"🗜️ Compressing audio ({file_size_mb:.1f} MB)...", "INFO", self.phase3_log)
        renderer = VideoRenderer(logger=lambda msg, level: self.log(msg, level, self.phase3_log))

        thread = threading.Thread(
            target=self._compress_audio_worker,
            args=(renderer, voiceover),
            daemon=True
        )
        thread.start()

    def _compress_audio_worker(self, renderer, audio_file):
        """Worker thread for audio compression"""
        try:
            compressed_file = renderer.compress_audio(audio_file, target_size_mb=20)
            if compressed_file:
                self.voiceover_var.set(str(compressed_file))
                messagebox.showinfo("Success!", f"Audio compressed!\n\n{compressed_file}")
            else:
                messagebox.showerror("Error", "Compression failed! Check log.")
        except Exception as e:
            self.log(f"❌ Compression error: {e}", "ERROR", self.phase3_log)
            messagebox.showerror("Error", f"Compression failed:\n\n{e}")

    def generate_srt(self):
        """Generate SRT from voiceover audio using Whisper API"""
        voiceover = self.voiceover_var.get()
        if not voiceover or not Path(voiceover).exists():
            messagebox.showerror("Error", "Please select a voiceover file first!")
            return

        api_key = self.config.get('openai_api_key', '').strip()
        if not api_key:
            messagebox.showerror("Error",
                "OpenAI API key required!\n\n"
                "Enter it in the Settings tab first.")
            return

        self.log("🎤 Generating SRT from voiceover...", "INFO", self.phase3_log)
        transcriber = WhisperTranscriber(api_key, logger=lambda msg, level: self.log(msg, level, self.phase3_log))

        thread = threading.Thread(
            target=self._generate_srt_worker,
            args=(transcriber, voiceover),
            daemon=True
        )
        thread.start()

    def _generate_srt_worker(self, transcriber, audio_file):
        """Worker thread for SRT generation"""
        try:
            srt_file = transcriber.transcribe_to_srt(audio_file)
            if srt_file:
                self.srt_var.set(str(srt_file))
                messagebox.showinfo("Success!", f"SRT generated!\n\n{srt_file}")
            else:
                messagebox.showerror("Error", "SRT generation failed! Check log.")
        except Exception as e:
            self.log(f"❌ SRT generation error: {e}", "ERROR", self.phase3_log)
            messagebox.showerror("Error", f"SRT generation failed:\n\n{e}")

    def render_video(self):
        """Render video for selected section"""
        section_name = self.section_var.get()
        if not section_name:
            messagebox.showerror("Error", "Please select a section!")
            return

        section_folder = self.output_folder / section_name
        image_files = sorted(list(section_folder.glob("*.png")) + list(section_folder.glob("*.jpg")))

        if not image_files:
            messagebox.showerror("Error", f"No images found in {section_name}!")
            return

        self.log(f"🎬 Rendering {section_name}...", "INFO", self.phase3_log)

        # Create renderer
        renderer = VideoRenderer(logger=lambda msg, level: self.log(msg, level, self.phase3_log))

        # Output file
        videos_folder = Path.cwd() / "videos"
        videos_folder.mkdir(exist_ok=True)
        output_file = videos_folder / f"{section_name}.mp4"

        # Render in thread
        thread = threading.Thread(
            target=self._render_worker,
            args=(renderer, image_files, output_file),
            daemon=True
        )
        thread.start()

    def _render_worker(self, renderer, image_files, output_file):
        """Worker thread for rendering"""
        success = renderer.render_video(
            image_files=image_files,
            output_file=output_file,
            duration=self.duration_var.get(),
            transition=self.transition_var.get(),
            transition_duration=self.transition_duration_var.get(),
            resolution=self.resolution_var.get(),
            fps=self.fps_var.get(),
            voiceover=self.voiceover_var.get() or None,
            music=self.music_var.get() or None,
            music_volume=self.music_volume_var.get() / 100.0,
            srt=None  # Disabled due to path issues
        )

        if success:
            self.last_rendered_video = output_file
            messagebox.showinfo("Success!", f"Video rendered!\n\n{output_file}")
        else:
            messagebox.showerror("Error", "Rendering failed! Check log.")

    def open_videos_folder(self):
        """Open the videos output folder"""
        import os
        import subprocess

        videos_folder = Path.cwd() / "videos"
        if videos_folder.exists():
            if os.name == 'nt':  # Windows
                os.startfile(str(videos_folder))
            elif os.sys.platform == 'darwin':  # macOS
                subprocess.run(['open', str(videos_folder)])
            else:  # Linux
                subprocess.run(['xdg-open', str(videos_folder)])
        else:
            messagebox.showinfo("Info", "Videos folder will be created when you render your first video.")

    def open_last_video(self):
        """Open the last rendered video"""
        import os
        import subprocess

        if hasattr(self, 'last_rendered_video') and Path(self.last_rendered_video).exists():
            video_path = str(self.last_rendered_video)
            if os.name == 'nt':  # Windows
                os.startfile(video_path)
            elif os.sys.platform == 'darwin':  # macOS
                subprocess.run(['open', video_path])
            else:  # Linux
                subprocess.run(['xdg-open', video_path])
        else:
            messagebox.showinfo("Info", "No video has been rendered yet, or the last video was deleted.")

    # ========== PHASE 4: MULTI-LANGUAGE SRT ==========

    def create_phase4_tab(self):
        """Create Phase 4 UI - Multi-language SRT"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🌍 Phase 4: Multi-Language SRT")

        ttk.Label(frame, text="Phase 4: Translate Subtitles",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # SRT selector
        srt_frame = ttk.LabelFrame(frame, text="Select SRT", padding="10")
        srt_frame.pack(fill=tk.X, pady=5)

        row = ttk.Frame(srt_frame)
        row.pack(fill=tk.X)
        self.phase4_srt_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.phase4_srt_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_phase4_srt).pack(side=tk.LEFT)
        ttk.Button(row, text="Use Phase 3 SRT", command=self.use_phase3_srt).pack(side=tk.LEFT, padx=5)

        # Language selection
        lang_frame = ttk.LabelFrame(frame, text="Target Languages", padding="10")
        lang_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        languages = [
            ('de', 'German 🇩🇪'), ('es', 'Spanish 🇪🇸'), ('fr', 'French 🇫🇷'),
            ('it', 'Italian 🇮🇹'), ('pt', 'Portuguese 🇵🇹'), ('ja', 'Japanese 🇯🇵'),
            ('ko', 'Korean 🇰🇷'), ('zh', 'Chinese 🇨🇳'), ('ru', 'Russian 🇷🇺'), ('ar', 'Arabic 🇸🇦')
        ]

        self.lang_vars = {}
        for i, (code, name) in enumerate(languages):
            var = tk.BooleanVar(value=True)
            self.lang_vars[code] = var
            ttk.Checkbutton(lang_frame, text=name, variable=var).grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)

        # Translate button
        ttk.Button(frame, text="🌍 Translate to All Languages",
                  command=self.translate_srt).pack(pady=10)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Translation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.phase4_log = scrolledtext.ScrolledText(log_frame, height=8, state='disabled')
        self.phase4_log.pack(fill=tk.BOTH, expand=True)

    def browse_phase4_srt(self):
        """Browse for SRT file"""
        filename = filedialog.askopenfilename(
            title="Select SRT File",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if filename:
            self.phase4_srt_var.set(filename)

    def use_phase3_srt(self):
        """Use SRT from Phase 3"""
        srt = self.srt_var.get()
        if srt and Path(srt).exists():
            self.phase4_srt_var.set(srt)
        else:
            messagebox.showerror("Error", "No SRT file from Phase 3!")

    def translate_srt(self):
        """Translate SRT to multiple languages"""
        srt_file = self.phase4_srt_var.get()
        if not srt_file or not Path(srt_file).exists():
            messagebox.showerror("Error", "Please select an SRT file!")
            return

        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter OpenAI API key in Phase 3!")
            return

        selected_langs = [code for code, var in self.lang_vars.items() if var.get()]
        if not selected_langs:
            messagebox.showerror("Error", "Please select at least one language!")
            return

        self.log(f"🌍 Translating to {len(selected_langs)} languages...", "INFO", self.phase4_log)

        translator = SRTTranslator(api_key, logger=lambda msg, level: self.log(msg, level, self.phase4_log))

        thread = threading.Thread(
            target=lambda: translator.translate_srt(srt_file, selected_langs),
            daemon=True
        )
        thread.start()

    # ========== UTILITY METHODS ==========

    def log(self, message, level='INFO', target_widget=None):
        """Log message to console or widget"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {level}: {message}\n"

        if target_widget:
            target_widget.config(state='normal')
            target_widget.insert(tk.END, log_message)
            target_widget.see(tk.END)
            target_widget.config(state='disabled')
            self.root.update()
        else:
            print(log_message, end='')

    def log_to_tts(self, message, level='INFO'):
        """Helper to log to TTS log widget"""
        if hasattr(self, 'tts_log'):
            self.log(message, level, self.tts_log)

    def refresh_project_list(self):
        """Refresh project dropdowns"""
        projects = self.project_manager.list_projects()
        self.phase2_project_combo['values'] = projects
        self.phase3_project_combo['values'] = projects

    # ========== SLEEP VIDEOS TAB ==========

    def create_sleep_videos_notebook(self):
        """Create Sleep Videos tab with nested notebook for phases"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="😴 Sleep Videos")

        # Create nested notebook for phases
        self.sleep_notebook = ttk.Notebook(frame)
        self.sleep_notebook.pack(fill=tk.BOTH, expand=True)

        # Add all phase tabs to the nested notebook
        self._create_phase1_in_sleep_tab()
        self._create_phase2_in_sleep_tab()
        self._create_phase25_in_sleep_tab()
        self._create_phase3_in_sleep_tab()
        self._create_phase4_in_sleep_tab()

    def _create_phase1_in_sleep_tab(self):
        """Create Phase 1 inside Sleep Videos tab"""
        frame = ttk.Frame(self.sleep_notebook, padding="10")
        self.sleep_notebook.add(frame, text="📝 Story Chunking")

        # Copy the content from create_phase1_tab
        self._populate_phase1_content(frame)

    def _create_phase2_in_sleep_tab(self):
        """Create Phase 2 inside Sleep Videos tab"""
        frame = ttk.Frame(self.sleep_notebook, padding="10")
        self.sleep_notebook.add(frame, text="🎨 Generate Images")

        # Copy the content from create_phase2_tab
        self._populate_phase2_content(frame)

    def _create_phase25_in_sleep_tab(self):
        """Create Phase 2.5 inside Sleep Videos tab"""
        frame = ttk.Frame(self.sleep_notebook, padding="10")
        self.sleep_notebook.add(frame, text="🎙️ Narration")

        # Copy the content from create_phase25_tab
        self._populate_phase25_content(frame)

    def _create_phase3_in_sleep_tab(self):
        """Create Phase 3 inside Sleep Videos tab"""
        frame = ttk.Frame(self.sleep_notebook, padding="10")
        self.sleep_notebook.add(frame, text="🎬 Create Videos")

        # Copy the content from create_phase3_tab
        self._populate_phase3_content(frame)

    def _create_phase4_in_sleep_tab(self):
        """Create Phase 4 inside Sleep Videos tab"""
        frame = ttk.Frame(self.sleep_notebook, padding="10")
        self.sleep_notebook.add(frame, text="🌍 Translations")

        # Copy the content from create_phase4_tab
        self._populate_phase4_content(frame)

    def _populate_phase1_content(self, frame):
        """Populate Phase 1 content - Story Chunking UI"""
        ttk.Label(frame, text="Phase 1: Chunk Your Story",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Story input
        story_frame = ttk.LabelFrame(frame, text="Your Story", padding="10")
        story_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_row = ttk.Frame(story_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_row, text="📂 Load File", command=self.load_story_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="📋 Copy to Clipboard", command=self.copy_story).pack(side=tk.LEFT, padx=5)

        self.story_text = scrolledtext.ScrolledText(story_frame, height=12, width=90)
        self.story_text.pack(fill=tk.BOTH, expand=True)

        # Chunking options
        chunk_frame = ttk.LabelFrame(frame, text="Chunking Options", padding="10")
        chunk_frame.pack(fill=tk.X, pady=5)

        ttk.Button(chunk_frame, text="🤖 Chunk via API (Automatic)",
                  command=self.chunk_via_api).pack(side=tk.LEFT, padx=5)
        ttk.Button(chunk_frame, text="📋 Copy Prompt (Manual)",
                  command=self.copy_chunking_prompt).pack(side=tk.LEFT, padx=5)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.phase1_log = scrolledtext.ScrolledText(log_frame, height=6, state='disabled')
        self.phase1_log.pack(fill=tk.BOTH, expand=True)

        # Instructions
        ttk.Label(frame, text="• API: Automatic chunking using GPT-4o-mini\n• Manual: Copy prompt, paste to ChatGPT, then go to Phase 2",
                 foreground='gray').pack(pady=5)

    def _populate_phase2_content(self, frame):
        """Populate Phase 2 content - Image Generation UI"""
        ttk.Label(frame, text="Phase 2: Auto-Generate Image Prompts",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Project selector and sections
        selector_frame = ttk.LabelFrame(frame, text="Load Project", padding="10")
        selector_frame.pack(fill=tk.X, pady=5)

        row = ttk.Frame(selector_frame)
        row.pack(fill=tk.X)

        ttk.Label(row, text="Project:").pack(side=tk.LEFT, padx=5)
        self.phase2_project_var = tk.StringVar()
        self.phase2_project_combo = ttk.Combobox(row, textvariable=self.phase2_project_var,
                                                  width=40, state='readonly')
        self.phase2_project_combo.pack(side=tk.LEFT, padx=5)
        self.phase2_project_combo.bind('<<ComboboxSelected>>', self.load_project_phase2)
        ttk.Button(row, text="🔄", command=self.refresh_project_list, width=3).pack(side=tk.LEFT)

        # Sections display
        sections_frame = ttk.LabelFrame(frame, text="Sections", padding="10")
        sections_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.sections_text = scrolledtext.ScrolledText(sections_frame, height=10)
        self.sections_text.pack(fill=tk.BOTH, expand=True)

        # Automation controls
        control_frame = ttk.LabelFrame(frame, text="Automation Settings", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Images per section:").pack(side=tk.LEFT, padx=5)
        self.images_per_section = tk.IntVar(value=4)
        ttk.Spinbox(row1, from_=1, to=10, textvariable=self.images_per_section,
                   width=5).pack(side=tk.LEFT)

        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Delay after prompt (seconds):").pack(side=tk.LEFT, padx=5)
        self.delay_after_prompt = tk.IntVar(value=150)
        ttk.Spinbox(row2, from_=30, to=600, textvariable=self.delay_after_prompt,
                   width=8).pack(side=tk.LEFT)

        # Start/Stop buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="▶️ Start Automation", command=self.start_automation).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⏹️ Stop", command=self.stop_automation).pack(side=tk.LEFT, padx=5)

        # Progress
        progress_frame = ttk.Frame(frame)
        progress_frame.pack(fill=tk.X, pady=5)
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack()

    def _populate_phase25_content(self, frame):
        """Populate Phase 2.5 content - TTS Narration UI"""
        ttk.Label(frame, text="AI Voiceover Generation",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Project selection
        project_frame = ttk.LabelFrame(frame, text="Project", padding="10")
        project_frame.pack(fill=tk.X, pady=10)

        proj_row = ttk.Frame(project_frame)
        proj_row.pack(fill=tk.X)
        ttk.Label(proj_row, text="Current Project:", width=15).pack(side=tk.LEFT, padx=5)
        self.tts_project_label = ttk.Label(proj_row, text="No project loaded", foreground='red')
        self.tts_project_label.pack(side=tk.LEFT, padx=5)

        # Voice settings
        voice_frame = ttk.LabelFrame(frame, text="Voice Settings", padding="10")
        voice_frame.pack(fill=tk.X, pady=10)

        # Reference audio
        ref_row = ttk.Frame(voice_frame)
        ref_row.pack(fill=tk.X, pady=5)
        ttk.Label(ref_row, text="Reference Voice:", width=15).pack(side=tk.LEFT, padx=5)
        self.tts_ref_path_var = tk.StringVar(value="")
        ttk.Entry(ref_row, textvariable=self.tts_ref_path_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(ref_row, text="Browse", command=self.browse_reference_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(ref_row, text="Clear", command=lambda: self.tts_ref_path_var.set("")).pack(side=tk.LEFT)

        ttk.Label(voice_frame, text="Leave empty for default voice. Upload 3-15s audio for voice cloning.",
                 font=('Arial', 8), foreground='gray').pack(anchor=tk.W, padx=5)

        # TTS Parameters
        params_frame = ttk.LabelFrame(frame, text="Voice Parameters", padding="10")
        params_frame.pack(fill=tk.X, pady=10)

        # Exaggeration
        exp_row = ttk.Frame(params_frame)
        exp_row.pack(fill=tk.X, pady=5)
        ttk.Label(exp_row, text="Exaggeration:", width=15).pack(side=tk.LEFT)
        self.tts_exaggeration_var = tk.DoubleVar(value=0.5)
        ttk.Scale(exp_row, from_=0.25, to=2.0, variable=self.tts_exaggeration_var,
                 orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=5)
        ttk.Label(exp_row, textvariable=self.tts_exaggeration_var, width=5).pack(side=tk.LEFT)
        ttk.Label(exp_row, text="(0.5 = neutral)", font=('Arial', 8), foreground='gray').pack(side=tk.LEFT, padx=5)

        # Temperature
        temp_row = ttk.Frame(params_frame)
        temp_row.pack(fill=tk.X, pady=5)
        ttk.Label(temp_row, text="Temperature:", width=15).pack(side=tk.LEFT)
        self.tts_temperature_var = tk.DoubleVar(value=0.8)
        ttk.Scale(temp_row, from_=0.05, to=2.0, variable=self.tts_temperature_var,
                 orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=5)
        ttk.Label(temp_row, textvariable=self.tts_temperature_var, width=5).pack(side=tk.LEFT)

        # CFG Weight
        cfg_row = ttk.Frame(params_frame)
        cfg_row.pack(fill=tk.X, pady=5)
        ttk.Label(cfg_row, text="CFG/Pace:", width=15).pack(side=tk.LEFT)
        self.tts_cfg_var = tk.DoubleVar(value=0.5)
        ttk.Scale(cfg_row, from_=0.0, to=1.0, variable=self.tts_cfg_var,
                 orient=tk.HORIZONTAL, length=300).pack(side=tk.LEFT, padx=5)
        ttk.Label(cfg_row, textvariable=self.tts_cfg_var, width=5).pack(side=tk.LEFT)

        # Generation options
        options_frame = ttk.LabelFrame(frame, text="Generation Options", padding="10")
        options_frame.pack(fill=tk.X, pady=10)

        self.tts_combine_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Combine all sections into single audio file",
                       variable=self.tts_combine_var).pack(anchor=tk.W)

        # Generate button
        gen_frame = ttk.Frame(frame)
        gen_frame.pack(fill=tk.X, pady=20)

        self.tts_generate_btn = ttk.Button(gen_frame, text="🎙️ Generate Narration",
                                          command=self.generate_narration, style='Accent.TButton')
        self.tts_generate_btn.pack(side=tk.LEFT, padx=5)

        self.tts_status_label = ttk.Label(gen_frame, text="", foreground='blue')
        self.tts_status_label.pack(side=tk.LEFT, padx=10)

        # Progress log
        log_frame = ttk.LabelFrame(frame, text="Generation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tts_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.tts_log.pack(fill=tk.BOTH, expand=True)

    def _populate_phase3_content(self, frame):
        """Populate Phase 3 content - Video Production UI"""
        ttk.Label(frame, text="Phase 3: Render Videos with FFmpeg",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Project/Section selector
        selector_frame = ttk.LabelFrame(frame, text="Select Content", padding="10")
        selector_frame.pack(fill=tk.X, pady=5)

        # Project row
        proj_row = ttk.Frame(selector_frame)
        proj_row.pack(fill=tk.X, pady=2)
        ttk.Label(proj_row, text="Project:").pack(side=tk.LEFT, padx=5)
        self.phase3_project_var = tk.StringVar()
        self.phase3_project_combo = ttk.Combobox(proj_row, textvariable=self.phase3_project_var,
                                                  width=35, state='readonly')
        self.phase3_project_combo.pack(side=tk.LEFT, padx=5)
        self.phase3_project_combo.bind('<<ComboboxSelected>>', self.load_project_phase3)
        ttk.Button(proj_row, text="🔄", command=self.refresh_project_list, width=3).pack(side=tk.LEFT)

        # Section row
        sect_row = ttk.Frame(selector_frame)
        sect_row.pack(fill=tk.X, pady=2)
        ttk.Label(sect_row, text="Section:").pack(side=tk.LEFT, padx=5)
        self.section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(sect_row, textvariable=self.section_var,
                                          width=50, state='readonly')
        self.section_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Video settings
        settings_frame = ttk.LabelFrame(frame, text="Video Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        # Video parameters
        params_frame = ttk.Frame(settings_frame)
        params_frame.pack(fill=tk.X, pady=5)

        # Row 1: Duration and Transition
        row1 = ttk.Frame(params_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Image Duration (sec):").pack(side=tk.LEFT, padx=5)
        self.duration_var = tk.IntVar(value=5)
        ttk.Spinbox(row1, from_=1, to=30, textvariable=self.duration_var, width=5).pack(side=tk.LEFT)

        ttk.Label(row1, text="Transition:").pack(side=tk.LEFT, padx=(20, 5))
        self.transition_var = tk.StringVar(value='crossfade')
        ttk.Combobox(row1, textvariable=self.transition_var, values=['crossfade', 'none'],
                    width=10, state='readonly').pack(side=tk.LEFT)

        ttk.Label(row1, text="Duration (sec):").pack(side=tk.LEFT, padx=(10, 5))
        self.transition_duration_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(row1, from_=0.1, to=5.0, increment=0.1, textvariable=self.transition_duration_var,
                   width=5).pack(side=tk.LEFT)

        # Row 2: Resolution and FPS
        row2 = ttk.Frame(params_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Resolution:").pack(side=tk.LEFT, padx=5)
        self.resolution_var = tk.StringVar(value='1920x1080')
        ttk.Combobox(row2, textvariable=self.resolution_var,
                    values=['1920x1080', '1280x720', '3840x2160'],
                    width=12, state='readonly').pack(side=tk.LEFT)

        ttk.Label(row2, text="FPS:").pack(side=tk.LEFT, padx=(20, 5))
        self.fps_var = tk.IntVar(value=30)
        ttk.Spinbox(row2, from_=15, to=60, textvariable=self.fps_var, width=5).pack(side=tk.LEFT)

        ttk.Label(row2, text="Music Volume:").pack(side=tk.LEFT, padx=(20, 5))
        self.music_volume_var = tk.IntVar(value=30)
        ttk.Spinbox(row2, from_=0, to=100, textvariable=self.music_volume_var, width=5).pack(side=tk.LEFT)
        ttk.Label(row2, text="%").pack(side=tk.LEFT)

        # Audio files
        audio_frame = ttk.LabelFrame(settings_frame, text="Audio", padding="5")
        audio_frame.pack(fill=tk.X, pady=5)

        self.voiceover_var = tk.StringVar()
        self.srt_var = tk.StringVar()
        self.music_var = tk.StringVar()

        # Voiceover
        row = ttk.Frame(audio_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Voiceover:", width=15).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.voiceover_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_voiceover).pack(side=tk.LEFT)
        ttk.Button(row, text="🗜️ Compress", command=self.compress_audio).pack(side=tk.LEFT, padx=5)

        # SRT Subtitles
        row = ttk.Frame(audio_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="SRT Subtitles:", width=15).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.srt_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_srt).pack(side=tk.LEFT)
        ttk.Button(row, text="🎤 Generate from Voiceover", command=self.generate_srt).pack(side=tk.LEFT, padx=5)

        # Background Music
        row = ttk.Frame(audio_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Background Music:", width=15).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.music_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_music).pack(side=tk.LEFT)

        # Render button
        render_btn_frame = ttk.Frame(settings_frame)
        render_btn_frame.pack(pady=10)
        ttk.Button(render_btn_frame, text="🎬 Render Video", command=self.render_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(render_btn_frame, text="📂 Open Videos Folder", command=self.open_videos_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(render_btn_frame, text="▶️ Open Last Video", command=self.open_last_video).pack(side=tk.LEFT, padx=5)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Render Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.phase3_log = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.phase3_log.pack(fill=tk.BOTH, expand=True)

    def _populate_phase4_content(self, frame):
        """Populate Phase 4 content - Multi-language SRT UI"""
        ttk.Label(frame, text="Phase 4: Translate Subtitles",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # SRT selector
        srt_frame = ttk.LabelFrame(frame, text="Select SRT", padding="10")
        srt_frame.pack(fill=tk.X, pady=5)

        row = ttk.Frame(srt_frame)
        row.pack(fill=tk.X)
        self.phase4_srt_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.phase4_srt_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Browse", command=self.browse_phase4_srt).pack(side=tk.LEFT)
        ttk.Button(row, text="Use Phase 3 SRT", command=self.use_phase3_srt).pack(side=tk.LEFT, padx=5)

        # Language selection
        lang_frame = ttk.LabelFrame(frame, text="Target Languages", padding="10")
        lang_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        languages = [
            ('de', 'German 🇩🇪'), ('es', 'Spanish 🇪🇸'), ('fr', 'French 🇫🇷'),
            ('it', 'Italian 🇮🇹'), ('pt', 'Portuguese 🇵🇹'), ('ja', 'Japanese 🇯🇵'),
            ('ko', 'Korean 🇰🇷'), ('zh', 'Chinese 🇨🇳'), ('ru', 'Russian 🇷🇺'), ('ar', 'Arabic 🇸🇦')
        ]

        self.lang_vars = {}
        for i, (code, name) in enumerate(languages):
            var = tk.BooleanVar(value=True)
            self.lang_vars[code] = var
            ttk.Checkbutton(lang_frame, text=name, variable=var).grid(row=i//2, column=i%2, sticky='w', padx=10, pady=2)

        # Translate button
        ttk.Button(frame, text="🌍 Translate to All Languages",
                  command=self.translate_srt).pack(pady=10)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Translation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.phase4_log = scrolledtext.ScrolledText(log_frame, height=8, state='disabled')
        self.phase4_log.pack(fill=tk.BOTH, expand=True)

    def create_sleep_videos_tab_OLD(self):
        """Create consolidated Sleep Videos tab with all story/image/video phases"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="😴 Sleep Videos")

        ttk.Label(frame, text="Sleep Video Creation Workflow",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(frame, text="Create AI-generated sleep videos with stories, images, and narration",
                 font=('Arial', 9)).pack(pady=(0, 20))

        # Call the existing phase creation methods
        # Phase 1: Story Chunking
        phase1_frame = ttk.LabelFrame(frame, text="📝 Step 1: Story Chunking", padding="10")
        phase1_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self._add_phase1_content(phase1_frame)

        # Phase 2: Generate Images
        phase2_frame = ttk.LabelFrame(frame, text="🎨 Step 2: Generate Images", padding="10")
        phase2_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self._add_phase2_content(phase2_frame)

        # Phase 2.5: Narration
        phase25_frame = ttk.LabelFrame(frame, text="🎙️ Step 3: Generate Narration", padding="10")
        phase25_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self._add_phase25_content(phase25_frame)

        # Phase 3: Create Videos
        phase3_frame = ttk.LabelFrame(frame, text="🎬 Step 4: Render Video", padding="10")
        phase3_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self._add_phase3_content(phase3_frame)

    def _add_phase1_content(self, parent):
        """Add Phase 1 content to parent frame"""
        ttk.Label(parent, text="Story chunking functionality - Coming soon!").pack(pady=20)

    def _add_phase2_content(self, parent):
        """Add Phase 2 content to parent frame"""
        ttk.Label(parent, text="Image generation functionality - Coming soon!").pack(pady=20)

    def _add_phase25_content(self, parent):
        """Add Phase 2.5 content to parent frame"""
        ttk.Label(parent, text="Narration generation functionality - Coming soon!").pack(pady=20)

    def _add_phase3_content(self, parent):
        """Add Phase 3 content to parent frame"""
        ttk.Label(parent, text="Video rendering functionality - Coming soon!").pack(pady=20)

    # ========== ACTOR FILMOGRAPHY TAB ==========

    def create_actor_filmography_tab(self):
        """Create unified Actor Wages tab with research, posters, and carousel"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="💰 Actor Wages")

        ttk.Label(frame, text="Actor Wages & Filmography Analyzer",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(frame, text="Research actors, download posters, analyze earnings, and create carousel videos",
                 font=('Arial', 9)).pack(pady=(0, 20))

        # Step 1: Research & Download
        research_frame = ttk.LabelFrame(frame, text="📊 Step 1: Research Filmography & Download Posters", padding="10")
        research_frame.pack(fill=tk.X, pady=5)

        ttk.Label(research_frame, text="Actor/Subject Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.actor_name_var = tk.StringVar()
        ttk.Entry(research_frame, textvariable=self.actor_name_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(research_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.actor_output_var = tk.StringVar(value="output/actor_analysis")
        ttk.Entry(research_frame, textvariable=self.actor_output_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(research_frame, text="Browse", command=self.browse_actor_output).grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(research_frame, text="🔍 Research & Download Posters",
                  command=self.research_and_download_filmography,
                  style='Accent.TButton').grid(row=2, column=0, columnspan=3, pady=10)

        # Step 1.5: Enrich Data (Optional)
        enrich_frame = ttk.LabelFrame(frame, text="💎 Step 1.5: Enrich Data (Optional)", padding="10")
        enrich_frame.pack(fill=tk.X, pady=5)

        ttk.Label(enrich_frame, text="CSV File (from Step 1):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.enrich_csv_var = tk.StringVar()
        ttk.Entry(enrich_frame, textvariable=self.enrich_csv_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(enrich_frame, text="Browse", command=self.browse_enrich_csv).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(enrich_frame, text="Add IMDB ratings, Rotten Tomatoes scores, budgets, and salary data",
                 font=('Arial', 9, 'italic')).grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=5, pady=2)

        ttk.Button(enrich_frame, text="💎 Enrich Actor Data",
                  command=self.enrich_actor_data,
                  style='Accent.TButton').grid(row=2, column=0, columnspan=3, pady=10)

        # Step 2: Generate Carousel Video
        carousel_frame = ttk.LabelFrame(frame, text="🎥 Step 2: Generate Carousel Video", padding="10")
        carousel_frame.pack(fill=tk.X, pady=5)

        ttk.Label(carousel_frame, text="CSV File (from Step 1):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.carousel_csv_var = tk.StringVar()
        ttk.Entry(carousel_frame, textvariable=self.carousel_csv_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(carousel_frame, text="Browse", command=self.browse_carousel_csv).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(carousel_frame, text="Scroll Speed (px/s):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.carousel_speed_var = tk.IntVar(value=120)
        ttk.Scale(carousel_frame, from_=50, to=300, variable=self.carousel_speed_var, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(carousel_frame, textvariable=self.carousel_speed_var).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(carousel_frame, text="Poster Spacing (px):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.carousel_spacing_var = tk.IntVar(value=40)
        ttk.Scale(carousel_frame, from_=10, to=100, variable=self.carousel_spacing_var, orient=tk.HORIZONTAL).grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(carousel_frame, textvariable=self.carousel_spacing_var).grid(row=2, column=2, padx=5, pady=5)

        # Voice/Narration Settings
        ttk.Label(carousel_frame, text="Voice Preset:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.voice_preset_var = tk.StringVar(value='documentary')
        voice_options = ['None (No Voice)']
        if TTS_AVAILABLE and VoicePreset:
            voice_options = ['None (No Voice)'] + VoicePreset.get_preset_names()
        voice_combo = ttk.Combobox(carousel_frame, textvariable=self.voice_preset_var,
                                   values=voice_options, state='readonly', width=37)
        voice_combo.grid(row=3, column=1, padx=5, pady=5)
        if not TTS_AVAILABLE:
            voice_combo.configure(state='disabled')

        ttk.Label(carousel_frame, text="Custom Voice File (optional):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.custom_voice_var = tk.StringVar()
        ttk.Entry(carousel_frame, textvariable=self.custom_voice_var, width=40).grid(row=4, column=1, padx=5, pady=5)
        voice_browse_btn = ttk.Button(carousel_frame, text="Browse", command=self.browse_custom_voice)
        voice_browse_btn.grid(row=4, column=2, padx=5, pady=5)
        if not TTS_AVAILABLE:
            voice_browse_btn.configure(state='disabled')

        ttk.Button(carousel_frame, text="🎬 Generate Carousel Video",
                  command=self.generate_carousel_video,
                  style='Accent.TButton').grid(row=5, column=0, columnspan=3, pady=10)

        # Review Panel Button
        ttk.Button(carousel_frame, text="📹 Review Carousel Videos",
                  command=self.open_video_review_panel,
                  style='Accent.TButton').grid(row=6, column=0, columnspan=3, pady=5)

        # Log output
        log_frame = ttk.LabelFrame(frame, text="📋 Progress Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=5)

        self.actor_log = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.actor_log.pack(fill=tk.BOTH, expand=True)

    def browse_actor_output(self):
        """Browse for actor output folder"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.actor_output_var.set(folder)

    def browse_carousel_csv(self):
        """Browse for carousel CSV file"""
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file:
            self.carousel_csv_var.set(file)

    def browse_custom_voice(self):
        """Browse for custom voice audio file"""
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            title="Select Voice Audio File",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.flac"),
                ("WAV Files", "*.wav"),
                ("MP3 Files", "*.mp3"),
                ("FLAC Files", "*.flac"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.custom_voice_var.set(file)

    def open_video_review_panel(self):
        """Open video review panel in new window"""
        import os
        from story_illustrator.utils.video_review_panel import VideoReviewPanel

        # Use absolute path with proper Windows format
        output_dir = os.path.abspath(os.path.join(os.getcwd(), "output", "actor_analysis"))

        if not os.path.exists(output_dir):
            messagebox.showwarning(
                "No Videos Found",
                f"Actor carousel directory not found:\n{output_dir}\n\n"
                "Please generate some carousel videos first."
            )
            return

        # Create new window for review panel
        review_window = tk.Toplevel(self.root)
        review_window.title("Video Review Panel - Actor Carousels")
        review_window.geometry("1200x800")

        # Add review panel
        panel = VideoReviewPanel(review_window, output_dir)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Bind mousewheel to window for global scroll
        def _window_scroll(event):
            if hasattr(panel, 'canvas') and panel.canvas:
                if hasattr(event, 'delta') and event.delta != 0:
                    panel.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif hasattr(event, 'num'):
                    if event.num == 4:
                        panel.canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        panel.canvas.yview_scroll(1, "units")

        review_window.bind("<MouseWheel>", _window_scroll)
        review_window.bind("<Button-4>", _window_scroll)
        review_window.bind("<Button-5>", _window_scroll)

        self.log(f"Opened video review panel for: {output_dir}", "INFO", self.actor_log)

    def browse_enrich_csv(self):
        """Browse for CSV file to enrich"""
        from tkinter import filedialog
        file = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file:
            self.enrich_csv_var.set(file)
            # Auto-fill Step 2 with the same CSV (will be replaced after enrichment)
            self.carousel_csv_var.set(file)

    def enrich_actor_data(self):
        """Enrich actor filmography data with IMDB ratings, RT scores, budgets, and salaries"""
        csv_path = self.enrich_csv_var.get().strip()
        if not csv_path:
            messagebox.showerror("Error", "Please select a CSV file to enrich")
            return

        def run_enrichment():
            try:
                import sys
                from io import StringIO

                class GUILogger:
                    def __init__(self, log_func):
                        self.log_func = log_func

                    def write(self, text):
                        if text.strip():
                            self.log_func(text.strip())

                    def flush(self):
                        pass

                old_stdout = sys.stdout

                def log_to_actor(msg):
                    self.actor_log.insert(tk.END, msg + "\n")
                    self.actor_log.see(tk.END)
                    self.actor_log.update()

                sys.stdout = GUILogger(log_to_actor)

                try:
                    log_to_actor(f"Starting enrichment for: {csv_path}")

                    from story_illustrator.utils.perplexity_researcher import PerplexityResearcher
                    from pathlib import Path
                    import pandas as pd

                    researcher = PerplexityResearcher()
                    csv_file = Path(csv_path)

                    # Load CSV
                    df = pd.read_csv(csv_file)
                    log_to_actor(f"Loaded {len(df)} movies from CSV")

                    # Add new columns if they don't exist
                    for col in ['imdb_rating', 'rotten_tomatoes', 'budget']:
                        if col not in df.columns:
                            df[col] = ''

                    # Enrich each movie
                    for idx, row in df.iterrows():
                        log_to_actor(f"[{idx+1}/{len(df)}] Enriching {row['title']} ({row['year']})...")

                        query = f"""
                        For the movie "{row['title']}" ({row['year']}):
                        1. IMDB rating (e.g. 7.5)
                        2. Rotten Tomatoes score (e.g. 85%)
                        3. Production budget (e.g. $50 million)

                        Return as JSON: {{"imdb_rating": "7.5", "rotten_tomatoes": "85%", "budget": "$50 million"}}
                        """

                        result = researcher.research(query)

                        # Parse JSON from result
                        import json
                        import re
                        json_match = re.search(r'\{.*\}', result, re.DOTALL)
                        if json_match:
                            try:
                                data = json.loads(json_match.group())
                                df.at[idx, 'imdb_rating'] = data.get('imdb_rating', '')
                                df.at[idx, 'rotten_tomatoes'] = data.get('rotten_tomatoes', '')
                                df.at[idx, 'budget'] = data.get('budget', '')
                            except json.JSONDecodeError:
                                log_to_actor(f"  Could not parse JSON response")

                    # Save enriched CSV
                    enriched_csv = csv_file.parent / f"{csv_file.stem}_enriched.csv"
                    df.to_csv(enriched_csv, index=False)

                    log_to_actor("=" * 50)
                    log_to_actor("✓ ENRICHMENT COMPLETE!")
                    log_to_actor(f"Enriched data saved to: {enriched_csv}")
                    log_to_actor("=" * 50)

                    # Auto-fill Step 2 with enriched CSV
                    self.carousel_csv_var.set(str(enriched_csv))

                    messagebox.showinfo("Success", f"Enrichment complete!\nSaved to: {enriched_csv}")

                finally:
                    sys.stdout = old_stdout

            except Exception as e:
                log_to_actor(f"ERROR: {str(e)}")
                messagebox.showerror("Error", f"Enrichment failed: {str(e)}")

        threading.Thread(target=run_enrichment, daemon=True).start()

    def research_and_download_filmography(self):
        """Research actor filmography and download posters"""
        actor_name = self.actor_name_var.get().strip()
        if not actor_name:
            messagebox.showerror("Error", "Please enter an actor/subject name")
            return

        def run_research():
            try:
                import sys
                from io import StringIO

                class GUILogger:
                    def __init__(self, log_func):
                        self.log_func = log_func

                    def write(self, text):
                        if text.strip():
                            self.log_func(text.strip())

                    def flush(self):
                        pass

                old_stdout = sys.stdout

                # Create a simple log function for this tab
                def log_to_actor(msg):
                    self.actor_log.insert(tk.END, msg + "\n")
                    self.actor_log.see(tk.END)
                    self.actor_log.update()

                sys.stdout = GUILogger(log_to_actor)

                try:
                    log_to_actor(f"Starting research for: {actor_name}")

                    # Import research utilities
                    from story_illustrator.utils.perplexity_researcher import PerplexityResearcher
                    from story_illustrator.utils.movie_poster_downloader import MoviePosterDownloader
                    from pathlib import Path
                    import pandas as pd
                    import json
                    import re

                    researcher = PerplexityResearcher()

                    # Research with Perplexity
                    query = f"""
                    List ALL {actor_name} movies chronologically from their career start to present.

                    Return the data as a JSON array where each movie object has these fields:
                    - title: exact movie title
                    - year: release year (integer)
                    - character: their character name
                    - box_office: worldwide box office gross
                    - salary: their salary (if known)

                    Format: [{{"title": "Movie Name", "year": 1986, "character": "Character Name", "box_office": "$xxx million", "salary": "$xxx million"}}, ...]

                    Include ONLY theatrical releases, not TV movies or documentaries.
                    """

                    result = researcher.research(query)
                    log_to_actor("Research complete!")

                    # Parse results
                    movies = self.parse_movies_from_text(result)
                    log_to_actor(f"Found {len(movies)} movies")

                    # Download posters
                    log_to_actor("Downloading movie posters from TMDB...")

                    downloader = MoviePosterDownloader()
                    output_dir = Path(self.actor_output_var.get()) / actor_name.lower().replace(' ', '_')
                    poster_dir = output_dir / "posters"
                    poster_dir.mkdir(parents=True, exist_ok=True)

                    poster_paths = {}
                    for i, movie in enumerate(movies, 1):
                        log_to_actor(f"[{i}/{len(movies)}] {movie['title']} ({movie['year']})...")
                        poster_path = downloader.download_poster(
                            movie['title'],
                            movie['year'],
                            str(poster_dir)
                        )
                        poster_paths[movie['title']] = poster_path

                    # Save to CSV
                    df_data = []
                    for movie in movies:
                        df_data.append({
                            'title': movie['title'],
                            'year': movie['year'],
                            'character': movie.get('character', ''),
                            'box_office': movie.get('box_office', ''),
                            'salary': movie.get('salary', ''),
                            'poster_path': poster_paths.get(movie['title'], '')
                        })

                    df = pd.DataFrame(df_data)
                    output_csv = output_dir / f"{actor_name.lower().replace(' ', '_')}_complete_filmography_with_posters.csv"
                    df.to_csv(output_csv, index=False)

                    log_to_actor("=" * 50)
                    log_to_actor("✓ SUCCESS!")
                    log_to_actor(f"Complete filmography saved to: {output_csv}")
                    log_to_actor(f"{len(movies)} movies, {len([p for p in poster_paths.values() if p])} posters downloaded")
                    log_to_actor("=" * 50)

                    # Auto-fill CSV paths for Step 1.5 and Step 2
                    self.enrich_csv_var.set(str(output_csv))
                    self.carousel_csv_var.set(str(output_csv))

                    messagebox.showinfo("Success", f"Research complete!\n{len(movies)} movies found\n{output_csv}")

                finally:
                    sys.stdout = old_stdout

            except Exception as e:
                log_to_actor(f"ERROR: {str(e)}")
                messagebox.showerror("Error", f"Research failed: {str(e)}")

        threading.Thread(target=run_research, daemon=True).start()

    # ========== CAROUSEL TAB (DEPRECATED - KEEPING FOR COMPATIBILITY) ==========

    def create_carousel_tab(self):
        """Create Carousel Video tab for data-driven slideshows"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🎬 Carousel Video")

        ttk.Label(frame, text="Carousel Video Creator",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(frame, text="Create horizontal scrolling videos from CSV data with movie posters",
                 font=('Arial', 9)).pack(pady=(0, 20))

        # CSV Input
        csv_frame = ttk.LabelFrame(frame, text="Data Source (CSV)", padding="10")
        csv_frame.pack(fill=tk.X, pady=5)

        row1 = ttk.Frame(csv_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Label(row1, text="CSV File:", width=15).pack(side=tk.LEFT, padx=5)
        self.carousel_csv_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.carousel_csv_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1, text="Browse", command=self.browse_carousel_csv).pack(side=tk.LEFT)

        ttk.Label(csv_frame, text="CSV should contain: title, year, character, box_office, salary, poster_path",
                 font=('Arial', 8), foreground='gray').pack(pady=(5, 0))

        # Research Options
        research_frame = ttk.LabelFrame(frame, text="Research & Download Posters", padding="10")
        research_frame.pack(fill=tk.X, pady=5)

        row2 = ttk.Frame(research_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Label(row2, text="Actor/Subject:", width=15).pack(side=tk.LEFT, padx=5)
        self.carousel_actor_var = tk.StringVar(value="Tom Cruise")
        ttk.Entry(row2, textvariable=self.carousel_actor_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2, text="🔍 Research & Download",
                  command=self.research_and_download).pack(side=tk.LEFT, padx=5)

        # Video Settings
        settings_frame = ttk.LabelFrame(frame, text="Video Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        row3 = ttk.Frame(settings_frame)
        row3.pack(fill=tk.X, pady=5)

        ttk.Label(row3, text="Scroll Speed (px/s):", width=20).pack(side=tk.LEFT, padx=5)
        self.carousel_speed_var = tk.IntVar(value=120)
        ttk.Entry(row3, textvariable=self.carousel_speed_var, width=10).pack(side=tk.LEFT, padx=5)

        ttk.Label(row3, text="Spacing (px):", width=15).pack(side=tk.LEFT, padx=5)
        self.carousel_spacing_var = tk.IntVar(value=40)
        ttk.Entry(row3, textvariable=self.carousel_spacing_var, width=10).pack(side=tk.LEFT, padx=5)

        row4 = ttk.Frame(settings_frame)
        row4.pack(fill=tk.X, pady=5)

        ttk.Label(row4, text="Output Folder:", width=20).pack(side=tk.LEFT, padx=5)
        self.carousel_output_var = tk.StringVar(value="output/carousel")
        ttk.Entry(row4, textvariable=self.carousel_output_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(row4, text="Browse", command=self.browse_carousel_output).pack(side=tk.LEFT)

        # Generate Button
        ttk.Button(frame, text="🎬 Generate Carousel Video",
                  command=self.generate_carousel_video,
                  style='Accent.TButton').pack(pady=15)

        # Log
        log_frame = ttk.LabelFrame(frame, text="Progress Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.carousel_log = scrolledtext.ScrolledText(log_frame, height=12, state='disabled')
        self.carousel_log.pack(fill=tk.BOTH, expand=True)

    def browse_carousel_csv(self):
        """Browse for CSV file"""
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.carousel_csv_var.set(filename)

    def browse_carousel_output(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.carousel_output_var.set(folder)

    def research_and_download(self):
        """Research filmography and download posters"""
        actor_name = self.carousel_actor_var.get().strip()
        if not actor_name:
            messagebox.showerror("Error", "Please enter an actor/subject name")
            return

        def run_research():
            try:
                self.log(f"Starting research for: {actor_name}", widget=self.carousel_log)

                # Import research utilities
                from story_illustrator.utils.perplexity_researcher import PerplexityResearcher
                from story_illustrator.utils.movie_poster_downloader import MoviePosterDownloader
                import pandas as pd
                import json

                # Research with Perplexity
                self.log("Researching filmography with Perplexity API...", widget=self.carousel_log)
                researcher = PerplexityResearcher()

                query = f"""
                List ALL {actor_name} movies chronologically from their career start to present.

                Return the data as a JSON array where each movie object has these fields:
                - title: exact movie title
                - year: release year (integer)
                - character: their character name
                - box_office: worldwide box office gross
                - salary: their salary (if known)

                Format: [{{"title": "Movie Name", "year": 1986, "character": "Character Name", "box_office": "$xxx million", "salary": "$xxx million"}}, ...]

                Include ONLY theatrical releases, not TV movies or documentaries.
                """

                result = researcher.research(query)
                self.log("Research complete!", widget=self.carousel_log)

                # Parse movies
                movies = self.parse_movies_from_text(result)
                self.log(f"Found {len(movies)} movies", widget=self.carousel_log)

                # Download posters
                self.log("Downloading posters from TMDB...", widget=self.carousel_log)
                downloader = MoviePosterDownloader()

                actor_folder = actor_name.lower().replace(" ", "_")
                output_dir = Path(f"output/{actor_folder}/posters")
                output_dir.mkdir(parents=True, exist_ok=True)

                poster_paths = {}
                for i, movie in enumerate(movies, 1):
                    self.log(f"[{i}/{len(movies)}] {movie['title']} ({movie['year']})...", widget=self.carousel_log)
                    poster_path = downloader.download_poster(
                        movie['title'],
                        movie['year'],
                        str(output_dir)
                    )
                    poster_paths[movie['title']] = poster_path

                # Save CSV
                df_data = []
                for movie in movies:
                    df_data.append({
                        'title': movie['title'],
                        'year': movie['year'],
                        'character': movie.get('character', ''),
                        'box_office': movie.get('box_office', ''),
                        'salary': movie.get('salary', ''),
                        'poster_path': poster_paths.get(movie['title'], '')
                    })

                df = pd.DataFrame(df_data)
                output_csv = Path(f"output/{actor_folder}/complete_filmography_with_posters.csv")
                df.to_csv(output_csv, index=False)

                # Update CSV path
                self.carousel_csv_var.set(str(output_csv))
                self.carousel_output_var.set(f"output/{actor_folder}")

                self.log(f"✓ Complete! CSV saved to: {output_csv}", widget=self.carousel_log)
                self.log(f"✓ {len(movies)} movies, {len([p for p in poster_paths.values() if p])} posters downloaded", widget=self.carousel_log)

            except Exception as e:
                self.log(f"ERROR: {str(e)}", widget=self.carousel_log)
                messagebox.showerror("Error", f"Research failed: {str(e)}")

        threading.Thread(target=run_research, daemon=True).start()

    def parse_movies_from_text(self, text: str) -> list:
        """Parse movie titles and years from Perplexity response"""
        import json
        import re

        movies = []

        # Try to extract JSON array
        try:
            json_match = re.search(r'\[\s*\{[^\]]+\]\s*', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_json = json.loads(json_str)

                for movie in parsed_json:
                    if 'title' in movie and 'year' in movie:
                        movies.append({
                            'title': movie['title'],
                            'year': int(movie['year']),
                            'character': movie.get('character', ''),
                            'box_office': movie.get('box_office', ''),
                            'salary': movie.get('salary', '')
                        })

                if movies:
                    movies.sort(key=lambda x: x['year'])
                    return movies
        except:
            pass

        # Fallback to text parsing
        pattern1 = r'(?:^|\n)[•\-*]?\s*([A-Z][^(\n]+?)\s+\((\d{4})\)'
        matches = re.findall(pattern1, text)

        for title, year in matches:
            title = title.strip().strip('-*•').strip()
            movies.append({
                'title': title,
                'year': int(year),
                'character': '',
                'box_office': '',
                'salary': ''
            })

        movies.sort(key=lambda x: x['year'])
        return movies

    def generate_carousel_video(self):
        """Generate carousel video from CSV"""
        csv_path = self.carousel_csv_var.get().strip()
        if not csv_path or not Path(csv_path).exists():
            messagebox.showerror("Error", "Please select a valid CSV file")
            return

        def run_generation():
            try:
                import pandas as pd
                import sys

                # Create a simple log function for this tab
                def log_to_actor(msg):
                    self.actor_log.insert(tk.END, msg + "\n")
                    self.actor_log.see(tk.END)
                    self.actor_log.update()

                class GUILogger:
                    def __init__(self, log_func):
                        self.log_func = log_func

                    def write(self, text):
                        if text.strip():
                            self.log_func(text.strip())

                    def flush(self):
                        pass

                old_stdout = sys.stdout
                sys.stdout = GUILogger(log_to_actor)

                try:
                    log_to_actor("Starting carousel video generation...")

                    # Read CSV
                    df = pd.read_csv(csv_path)
                    df = df.sort_values('year')
                    log_to_actor(f"Loaded {len(df)} movies from {df['year'].min()} to {df['year'].max()}")

                    # Create output directories
                    output_base = Path(csv_path).parent
                    enhanced_dir = output_base / "enhanced_posters"
                    enhanced_dir.mkdir(parents=True, exist_ok=True)

                    # Import carousel modules
                    from story_illustrator.utils.carousel_poster_enhancer import CarouselPosterEnhancer
                    from story_illustrator.utils.carousel_video_generator import CarouselVideoGenerator

                    # Create enhanced posters
                    log_to_actor("Creating enhanced posters with overlays...")

                    enhancer = CarouselPosterEnhancer()
                    posters = enhancer.batch_enhance_posters(
                        csv_path=csv_path,
                        output_dir=enhanced_dir
                    )

                    log_to_actor(f"Created {len(posters)} enhanced posters")

                    if len(posters) == 0:
                        raise Exception("No posters created!")

                    # Generate carousel video using the modular generator
                    log_to_actor("Generating carousel video...")

                    generator = CarouselVideoGenerator()
                    generator.scroll_speed = self.carousel_speed_var.get()

                    # Get actor name from CSV filename or user input
                    actor_name = Path(csv_path).stem.replace('_', ' ').replace('complete filmography with posters', '').strip()
                    if not actor_name:
                        actor_name = "Actor"

                    output_file = output_base / "carousel_video.mp4"

                    # Prepare voice parameters
                    voice_params = None
                    voice_preset = self.voice_preset_var.get()
                    custom_voice = self.custom_voice_var.get().strip()

                    if TTS_AVAILABLE and VoiceManager and voice_preset != 'None (No Voice)':
                        vm = VoiceManager()

                        # Use custom voice if provided, otherwise use preset
                        if custom_voice and Path(custom_voice).exists():
                            log_to_actor(f"Using custom voice: {custom_voice}")
                            voice_params = vm.get_tts_params(
                                preset_name=voice_preset if voice_preset != 'documentary' else None,
                                voice_clone_path=custom_voice
                            )
                        elif voice_preset:
                            log_to_actor(f"Using voice preset: {voice_preset}")
                            voice_params = vm.get_tts_params(preset_name=voice_preset)

                    # Use the complete workflow
                    success = generator.create_carousel_from_posters(
                        poster_paths=posters,
                        actor_name=actor_name,
                        output_path=output_file,
                        voice_params=voice_params
                    )

                    if success:
                        log_to_actor("=" * 50)
                        log_to_actor("✓ SUCCESS! Carousel video created!")
                        log_to_actor(f"Output: {output_file}")
                        log_to_actor(f"Movies: {len(posters)}")
                        log_to_actor("=" * 50)
                        messagebox.showinfo("Success", f"Carousel video created!\n{output_file}")
                    else:
                        raise Exception("Video generation failed")
                finally:
                    sys.stdout = old_stdout

            except Exception as e:
                log_to_actor(f"ERROR: {str(e)}")
                messagebox.showerror("Error", f"Video generation failed: {str(e)}")

        threading.Thread(target=run_generation, daemon=True).start()

    # ========== DENGEAI PROMPT BUILDER TAB ==========

    def create_dengeai_prompt_builder_tab(self):
        """Create DengeAI Prompt Builder tab for cinematic AI video prompts"""
        if not DENGEAI_AVAILABLE:
            return

        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🎬 Prompt Builder")

        # Title
        ttk.Label(frame, text="DengeAI Cinematic Prompt Builder",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        ttk.Label(frame, text="Build professional AI video prompts with 20+ cinematographic categories",
                 font=('Arial', 10)).pack(pady=(0, 20))

        # Initialize prompt builder and image mapper
        self.prompt_builder = DengeAIPromptBuilder()
        self.image_mapper = PromptImageMapper()

        # Create main container with two sections
        main_container = ttk.Frame(frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left side: Categories and controls
        left_frame = ttk.Frame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right side: Image display
        right_frame = ttk.LabelFrame(main_container, text="📸 Visual Reference", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # Image display area
        self.example_image_label = ttk.Label(right_frame, text="Select an option\nto see example",
                                            font=('Arial', 10, 'italic'),
                                            foreground='#666',
                                            justify=tk.CENTER)
        self.example_image_label.pack(pady=20)

        # Store current photo reference (prevent garbage collection)
        self.current_photo = None

        # Create scrollable frame in left side
        canvas = tk.Canvas(left_frame)
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store dropdown variables
        self.prompt_dropdowns = {}

        # Create category selection UI
        categories_frame = ttk.Frame(scrollable_frame)
        categories_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Define categories to display
        categories = [
            ("Shot Size", "SHOT_SIZES"),
            ("Camera Angle", "CAMERA_ANGLES"),
            ("Camera Movement", "CAMERA_MOVEMENTS"),
            ("Composition", "COMPOSITION"),
            ("Lens Type", "LENS_TYPES"),
            ("Focus Technique", "FOCUS_TECHNIQUES"),
            ("Lighting Type", "LIGHTING_TYPES"),
            ("Light Source", "LIGHT_SOURCES"),
            ("Time of Day", "TIME_OF_DAY"),
            ("Color Tone", "COLOR_TONES"),
            ("Motion Type", "MOTION_TYPES"),
            ("Visual Effect", "VISUAL_EFFECTS"),
            ("Visual Style", "VISUAL_STYLES"),
            ("Character Emotion", "CHARACTER_EMOTIONS"),
            ("Advanced Camera", "ADVANCED_CAMERA"),
            ("Aspect Ratio", "ASPECT_RATIOS")
        ]

        row = 0
        for label, category_key in categories:
            # Category label
            ttk.Label(categories_frame, text=f"{label}:",
                     font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)

            # Dropdown
            var = tk.StringVar(value="(none)")
            options = ["(none)"] + self.prompt_builder.get_category_options(category_key)
            dropdown = ttk.Combobox(categories_frame, textvariable=var,
                                   values=options, state="readonly", width=50)
            dropdown.grid(row=row, column=1, padx=5, pady=5, sticky=tk.W)
            dropdown.bind("<<ComboboxSelected>>",
                         lambda e, k=category_key: self.on_category_selected(k))

            self.prompt_dropdowns[category_key] = var

            # Random button
            ttk.Button(categories_frame, text="🎲",
                      command=lambda k=category_key: self.random_category_selection(k),
                      width=3).grid(row=row, column=2, padx=2, pady=5)

            row += 1

        # Preset section
        preset_frame = ttk.LabelFrame(scrollable_frame, text="📋 Professional Presets", padding="10")
        preset_frame.pack(fill=tk.X, padx=5, pady=10)

        # Preset descriptions with visual cues
        preset_info = {
            "cinematic_portrait": "👤 Portrait | Close-up faces, natural lighting, shallow focus",
            "epic_landscape": "🏔️ Landscape | Wide vistas, aerial views, dramatic scenery",
            "noir_detective": "🕵️ Film Noir | Dark shadows, mystery, black & white classic",
            "cyberpunk_city": "🌃 Cyberpunk | Neon lights, futuristic cityscapes, high-tech",
            "horror_scene": "😱 Horror | Suspense, tilted angles, dark atmosphere",
            "action_sequence": "💥 Action | Fast motion, dynamic movement, intensity",
            "dreamy_fantasy": "✨ Fantasy | Magical, ethereal, soft and surreal",
            "product_commercial": "📦 Product | Clean showcase, professional lighting",
            "documentary_real": "📹 Documentary | Realistic, natural, observational",
            "music_video": "🎵 Music Video | Stylized, colorful, rhythm-driven"
        }

        ttk.Label(preset_frame, text="Quick Load:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.preset_var = tk.StringVar(value="(none)")
        preset_options = ["(none)"] + self.prompt_builder.get_preset_names()
        preset_dropdown = ttk.Combobox(preset_frame, textvariable=self.preset_var,
                                      values=preset_options, state="readonly", width=35)
        preset_dropdown.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        preset_dropdown.bind("<<ComboboxSelected>>", self.on_preset_selected)

        ttk.Button(preset_frame, text="Load Preset",
                  command=self.load_dengeai_preset).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(preset_frame, text="Clear All",
                  command=self.clear_all_dengeai_selections).grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(preset_frame, text="🎲 Randomize All",
                  command=self.randomize_all_categories).grid(row=0, column=5, padx=5, pady=5)

        # Preset description label
        self.preset_description_label = ttk.Label(preset_frame, text="",
                                                 font=('Arial', 9, 'italic'),
                                                 foreground='#666')
        self.preset_description_label.grid(row=1, column=0, columnspan=6, sticky=tk.W, padx=5, pady=(0, 5))

        # Store preset info for quick access
        self.preset_info = preset_info

        # Preview section
        preview_frame = ttk.LabelFrame(scrollable_frame, text="📝 Generated Prompt", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        # Description toggle
        self.include_descriptions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(preview_frame, text="Include full descriptions",
                       variable=self.include_descriptions_var,
                       command=self.update_prompt_preview).pack(anchor=tk.W, pady=5)

        # Prompt preview text
        self.prompt_preview_text = scrolledtext.ScrolledText(preview_frame, height=8, wrap=tk.WORD)
        self.prompt_preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Action buttons
        button_frame = ttk.Frame(preview_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="📋 Copy to Clipboard",
                  command=self.copy_dengeai_prompt).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="💾 Save to File",
                  command=self.save_dengeai_prompt).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="🎬 Use with WAN",
                  command=self.use_prompt_with_wan).pack(side=tk.LEFT, padx=5)

        # Visual reference guide
        guide_frame = ttk.LabelFrame(scrollable_frame, text="💡 Quick Reference Guide", padding="10")
        guide_frame.pack(fill=tk.X, padx=5, pady=10)

        guide_text = """
Shot Sizes: ECU (eyes) → CU (face) → MCU (chest up) → MS (waist up) → WS (full body) → EWS (environment)
Camera Angles: High (looking down) | Eye Level (neutral) | Low (looking up) | Dutch (tilted)
Lighting: Natural (daylight) | Golden Hour (sunset) | Soft (flattering) | Hard (dramatic) | Low-Key (moody)
Styles: Cinematic (film-like) | Documentary (realistic) | Noir (B&W mystery) | Cyberpunk (neon future)
Motion: Slow Motion (dramatic) | Normal (real-time) | Time-Lapse (sped up) | Freeze Frame (paused)

Best Practices:
• Start with a preset and modify as needed
• Match lighting in prompt to your source image
• Use 4-6 categories for best results
• Static camera + subtle motion = most stable results
• Combine Shot Size + Angle + Lighting + Style for complete control
        """

        guide_label = ttk.Label(guide_frame, text=guide_text.strip(),
                               font=('Courier', 8), justify=tk.LEFT)
        guide_label.pack(anchor=tk.W, padx=5, pady=5)

        # Initial preview
        self.update_prompt_preview()

    def random_category_selection(self, category_key):
        """Randomly select option for a category"""
        option = self.prompt_builder.select_random(category_key)
        if option:
            self.prompt_dropdowns[category_key].set(option)
            self.on_category_selected(category_key)

    def on_category_selected(self, category_key):
        """Handle category selection - update both prompt preview and image display"""
        # Update prompt preview
        self.update_prompt_preview()

        # Update image display
        option = self.prompt_dropdowns[category_key].get()
        if option and option != "(none)":
            self.display_example_image(category_key, option)
        else:
            self.clear_example_image()

    def display_example_image(self, category_key, option_name):
        """Display example image for selected option"""
        try:
            # Get image path from mapper
            image_path = self.image_mapper.get_image_path(category_key, option_name)

            if image_path and image_path.exists():
                # Load and resize image
                pil_image = Image.open(image_path)

                # Resize to fit display area (max 400x300)
                max_width, max_height = 400, 300
                pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(pil_image)

                # Update label
                self.example_image_label.config(image=photo, text="")
                self.current_photo = photo  # Keep reference to prevent garbage collection

            else:
                # No image available for this option
                self.example_image_label.config(
                    image="",
                    text=f"No preview available\nfor this option",
                    font=('Arial', 9, 'italic'),
                    foreground='#999'
                )
                self.current_photo = None

        except Exception as e:
            print(f"Error displaying image: {e}")
            self.example_image_label.config(
                image="",
                text="Error loading\npreview image",
                font=('Arial', 9, 'italic'),
                foreground='#ff0000'
            )
            self.current_photo = None

    def clear_example_image(self):
        """Clear the example image display"""
        self.example_image_label.config(
            image="",
            text="Select an option\nto see example",
            font=('Arial', 10, 'italic'),
            foreground='#666'
        )
        self.current_photo = None

    def randomize_all_categories(self):
        """Randomly select options for all categories"""
        for category_key in self.prompt_dropdowns.keys():
            self.random_category_selection(category_key)

    def on_preset_selected(self, event=None):
        """Update preset description when selection changes"""
        preset_name = self.preset_var.get()
        if preset_name == "(none)":
            self.preset_description_label.config(text="")
        elif preset_name in self.preset_info:
            self.preset_description_label.config(text=self.preset_info[preset_name])
        else:
            self.preset_description_label.config(text="")

    def load_dengeai_preset(self):
        """Load selected preset"""
        preset_name = self.preset_var.get()
        if preset_name == "(none)":
            return

        if self.prompt_builder.load_preset(preset_name):
            # Update dropdowns
            for category_key, var in self.prompt_dropdowns.items():
                if category_key in self.prompt_builder.selected_options:
                    var.set(self.prompt_builder.selected_options[category_key])
                else:
                    var.set("(none)")

            self.update_prompt_preview()
            # Update description
            if preset_name in self.preset_info:
                self.preset_description_label.config(text=self.preset_info[preset_name])
            messagebox.showinfo("Success", f"Loaded preset: {preset_name}")
        else:
            messagebox.showerror("Error", f"Failed to load preset: {preset_name}")

    def clear_all_dengeai_selections(self):
        """Clear all category selections"""
        self.prompt_builder.clear_selections()
        for var in self.prompt_dropdowns.values():
            var.set("(none)")
        self.update_prompt_preview()

    def update_prompt_preview(self):
        """Update prompt preview based on selections"""
        # Update prompt builder with current selections
        self.prompt_builder.clear_selections()
        for category_key, var in self.prompt_dropdowns.items():
            option = var.get()
            if option != "(none)":
                self.prompt_builder.select_category(category_key, option)

        # Generate prompt
        include_descriptions = self.include_descriptions_var.get()
        prompt = self.prompt_builder.build_prompt(include_descriptions=include_descriptions)

        # Update preview
        self.prompt_preview_text.delete('1.0', tk.END)
        if prompt:
            self.prompt_preview_text.insert('1.0', prompt)
        else:
            self.prompt_preview_text.insert('1.0', "(No options selected)")

    def copy_dengeai_prompt(self):
        """Copy prompt to clipboard"""
        prompt = self.prompt_preview_text.get('1.0', tk.END).strip()
        if prompt and prompt != "(No options selected)":
            pyperclip.copy(prompt)
            messagebox.showinfo("Success", "Prompt copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No prompt to copy")

    def save_dengeai_prompt(self):
        """Save prompt to file"""
        prompt = self.prompt_preview_text.get('1.0', tk.END).strip()
        if not prompt or prompt == "(No options selected)":
            messagebox.showwarning("Warning", "No prompt to save")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Prompt",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                Path(file_path).write_text(prompt, encoding='utf-8')
                messagebox.showinfo("Success", f"Prompt saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save prompt: {e}")

    def use_prompt_with_wan(self):
        """Use generated prompt with WAN animator"""
        prompt = self.prompt_preview_text.get('1.0', tk.END).strip()
        if not prompt or prompt == "(No options selected)":
            messagebox.showwarning("Warning", "No prompt generated")
            return

        # TODO: Integrate with WAN animator
        # For now, just copy to clipboard and notify
        pyperclip.copy(prompt)
        messagebox.showinfo("Ready for WAN",
                          "Prompt copied to clipboard!\n\n"
                          "You can now use this prompt with:\n"
                          "- WAN 2.2 Image-to-Video\n"
                          "- ComfyUI workflows\n"
                          "- Other AI video tools")

    def on_closing(self):
        """Handle window close"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Process is running. Stop and quit?"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = StoryIllustratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
