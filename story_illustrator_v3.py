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

        # Create all phase tabs
        self.create_settings_tab()
        self.create_phase1_tab()
        self.create_phase2_tab()
        self.create_phase3_tab()
        self.create_phase4_tab()

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

        # Instructions
        info_frame = ttk.LabelFrame(frame, text="About API Usage", padding="20")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        info_text = """
• Phase 1 API Chunking: Uses GPT-4o-mini (~$0.001-0.003 per story)
• Phase 3 SRT Generation: Uses Whisper API (~$0.36 per hour of audio)
• Phase 4 Translation: Uses GPT-4o-mini (~$0.002 for 10 languages)

All API calls are logged with costs estimated.
Your API key is stored locally and never shared.
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

    def refresh_project_list(self):
        """Refresh project dropdowns"""
        projects = self.project_manager.list_projects()
        self.phase2_project_combo['values'] = projects
        self.phase3_project_combo['values'] = projects

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
