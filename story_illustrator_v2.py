#!/usr/bin/env python3
"""
Story Illustrator V3 - Three-Phase Workflow
Phase 1: Send story to ChatGPT for chunking
Phase 2: Paste chunks back, then auto-generate images for each section
Phase 3: Create videos from images with transitions, voiceover, music, and SRT subtitles
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pyautogui
import pyperclip
import threading
import time
import json
import re
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

class StoryIllustratorV2:
    def __init__(self, root):
        self.root = root
        self.root.title("📖 Story Illustrator V2 - ChatGPT Workflow")
        self.root.geometry("1000x950")
        self.root.resizable(True, True)

        # State
        self.is_running = False
        self.thread = None
        self.current_section_index = 0
        self.current_image_count = 0
        self.sections = []
        self.current_project_name = None
        self.config_file = Path(__file__).parent / "story_illustrator_v2_config.json"
        self.projects_folder = Path(__file__).parent / "projects"
        self.output_folder = Path(__file__).parent / "story_images"

        # Load config
        self.load_config()

        # Create folders
        self.output_folder.mkdir(exist_ok=True)
        self.projects_folder.mkdir(exist_ok=True)

        # Create UI
        self.create_ui()

        # Load project list
        self.refresh_project_list()

        # Bind close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Notebook for phases
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # PHASE 1 TAB
        phase1_frame = ttk.Frame(notebook, padding="10")
        notebook.add(phase1_frame, text="📝 Phase 1: Send Story to ChatGPT")

        ttk.Label(phase1_frame, text="Phase 1: Get ChatGPT to Chunk Your Story",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Story input
        story_frame = ttk.LabelFrame(phase1_frame, text="Your Story", padding="10")
        story_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(story_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(btn_frame, text="📂 Load Story File", command=self.load_story_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Copy Story to Clipboard", command=self.copy_story).pack(side=tk.LEFT, padx=5)

        self.story_text = scrolledtext.ScrolledText(story_frame, height=12, width=90)
        self.story_text.pack(fill=tk.BOTH, expand=True)

        # Chunking prompt
        prompt_frame = ttk.LabelFrame(phase1_frame, text="Prompt to Send ChatGPT", padding="10")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_row = ttk.Frame(prompt_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(btn_row, text="📋 Copy This Prompt", command=self.copy_phase1_prompt).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row, text="🤖 Chunk via API", command=self.chunk_via_api).pack(side=tk.LEFT, padx=5)
        ttk.Label(btn_row, text="(Automatic - no manual copying!)", foreground='gray').pack(side=tk.LEFT, padx=5)

        self.phase1_prompt_text = scrolledtext.ScrolledText(prompt_frame, height=10, width=90)
        self.phase1_prompt_text.pack(fill=tk.BOTH, expand=True)
        default_prompt = self.config.get('phase1_prompt',
"""Please read this story and divide it into logical sections for illustration. For each section:
1. Give it a descriptive title (e.g., "Section 1: The Awakening")
2. Include the full text of that section
3. Format each section clearly so I can easily copy them

Here's the story:

{story}

Please divide this into sections and format your response like this:
=== SECTION 1: [Title] ===
[Full text of section 1]

=== SECTION 2: [Title] ===
[Full text of section 2]

And so on.""")
        self.phase1_prompt_text.insert('1.0', default_prompt)

        # Phase 1 Log
        phase1_log_frame = ttk.LabelFrame(phase1_frame, text="API Log", padding="10")
        phase1_log_frame.pack(fill=tk.X, pady=5)

        self.phase1_log_text = scrolledtext.ScrolledText(phase1_log_frame, height=4, width=90, state='disabled')
        self.phase1_log_text.pack(fill=tk.X)

        instructions = ttk.Label(phase1_frame,
            text="Instructions:\n• Manual: Copy prompt → Paste into ChatGPT → Copy response → Go to Phase 2\n• API: Click 'Chunk via API' for automatic processing (requires OpenAI API key)",
            font=('Arial', 10), foreground='#569cd6', wraplength=900, justify=tk.LEFT)
        instructions.pack(pady=10)

        # PHASE 2 TAB
        phase2_frame = ttk.Frame(notebook, padding="10")
        notebook.add(phase2_frame, text="🎨 Phase 2: Generate Images")

        ttk.Label(phase2_frame, text="Phase 2: Auto-Generate Images for Each Section",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Paste sections
        sections_frame = ttk.LabelFrame(phase2_frame, text="Paste ChatGPT's Chunked Response Here", padding="10")
        sections_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame2 = ttk.Frame(sections_frame)
        btn_frame2.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(btn_frame2, text="📋 Paste from Clipboard", command=self.paste_sections).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame2, text="✂️ Parse Sections", command=self.parse_sections).pack(side=tk.LEFT, padx=5)
        self.sections_count_label = ttk.Label(btn_frame2, text="Sections found: 0")
        self.sections_count_label.pack(side=tk.LEFT, padx=20)

        # Project history selector
        ttk.Label(btn_frame2, text="Project:").pack(side=tk.LEFT, padx=(20, 5))
        self.phase2_project_var = tk.StringVar()
        self.phase2_project_selector = ttk.Combobox(btn_frame2, textvariable=self.phase2_project_var,
                                                     width=30, state='readonly')
        self.phase2_project_selector.pack(side=tk.LEFT, padx=5)
        self.phase2_project_selector.bind('<<ComboboxSelected>>', self.load_selected_project)
        ttk.Button(btn_frame2, text="🔄", command=self.refresh_project_list, width=3).pack(side=tk.LEFT, padx=2)

        self.sections_text = scrolledtext.ScrolledText(sections_frame, height=10, width=90)
        self.sections_text.pack(fill=tk.BOTH, expand=True)

        # Settings
        settings_frame = ttk.LabelFrame(phase2_frame, text="Image Generation Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        row = 0
        ttk.Label(settings_frame, text="Images per section:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.images_per_section_var = tk.StringVar(value=str(self.config.get('images_per_section', 4)))
        ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.images_per_section_var, width=10).grid(row=row, column=1, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Continue command:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.continue_command_var = tk.StringVar(value=self.config.get('continue_command', 'go on'))
        ttk.Entry(settings_frame, textvariable=self.continue_command_var, width=30).grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(settings_frame, text="Interval between commands (seconds):").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        self.interval_var = tk.StringVar(value=str(self.config.get('interval', 60)))
        ttk.Spinbox(settings_frame, from_=10, to=300, textvariable=self.interval_var, width=10).grid(row=row, column=1, sticky=tk.W)

        row += 1
        ttk.Label(settings_frame, text="Startup delay (seconds):").grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.startup_delay_var = tk.StringVar(value=str(self.config.get('startup_delay', 10)))
        ttk.Spinbox(settings_frame, from_=0, to=60, textvariable=self.startup_delay_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(settings_frame, text="Output folder:").grid(row=row, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(settings_frame, text=str(self.output_folder), foreground='gray').grid(row=row, column=1, sticky=tk.W)
        ttk.Button(settings_frame, text="📂 Open Folder", command=self.open_output_folder).grid(row=row, column=2, padx=5)


        # Image prompt template
        template_frame = ttk.LabelFrame(phase2_frame, text="Image Generation Prompt Template", padding="10")
        template_frame.pack(fill=tk.X, pady=5)

        ttk.Label(template_frame, text="Use {title} and {text} as placeholders:").pack(anchor=tk.W, pady=(0, 5))

        self.image_prompt_template_text = scrolledtext.ScrolledText(template_frame, height=4, width=90)
        self.image_prompt_template_text.pack(fill=tk.X)
        default_template = self.config.get('image_prompt_template',
"""Create 4 detailed, cinematic images for this section of the story:

{title}

{text}

Each image should capture a key moment or atmosphere from this section. Make them visually striking and thematically consistent.""")
        self.image_prompt_template_text.insert('1.0', default_template)

        # Control buttons
        control_frame = ttk.Frame(phase2_frame)
        control_frame.pack(pady=10)

        self.start_button = ttk.Button(control_frame, text="▶ Start Image Generation",
                                       command=self.start_process, width=20)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="⬛ Stop",
                                     command=self.stop_process, width=15, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="💾 Save Config",
                  command=self.save_config, width=15).pack(side=tk.LEFT, padx=5)

        # Status & Log
        status_frame = ttk.LabelFrame(phase2_frame, text="Status & Log", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.status_label = ttk.Label(status_frame, text="⚫ Ready",
                                     font=('Arial', 10, 'bold'))
        self.status_label.pack(anchor=tk.W, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(status_frame, height=8, width=90, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.progress_label = ttk.Label(status_frame, text="Section: 0/0 | Image: 0/0", font=('Arial', 9))
        self.progress_label.pack(anchor=tk.W, pady=(5, 0))

        instructions2 = ttk.Label(phase2_frame,
            text="💡 Tip: After each section finishes, you can manually download the images from ChatGPT\nand save them to the folder shown above. Each section will create a subfolder.",
            font=('Arial', 9), foreground='#4ec9b0', wraplength=900, justify=tk.LEFT)
        instructions2.pack(pady=5)

        # PHASE 3 TAB - VIDEO PRODUCTION
        phase3_frame = ttk.Frame(notebook, padding="10")
        notebook.add(phase3_frame, text="🎬 Phase 3: Video Production")

        ttk.Label(phase3_frame, text="Phase 3: Create Videos with FFmpeg",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Section selector
        selector_frame = ttk.LabelFrame(phase3_frame, text="Select Section", padding="10")
        selector_frame.pack(fill=tk.X, pady=5)

        # Project selector row
        project_row = ttk.Frame(selector_frame)
        project_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(project_row, text="Project:").pack(side=tk.LEFT, padx=5)
        self.phase3_project_var = tk.StringVar()
        self.phase3_project_selector = ttk.Combobox(project_row, textvariable=self.phase3_project_var,
                                                     width=40, state='readonly')
        self.phase3_project_selector.pack(side=tk.LEFT, padx=5)
        self.phase3_project_selector.bind('<<ComboboxSelected>>', self.phase3_load_project)
        ttk.Button(project_row, text="🔄", command=self.refresh_project_list, width=3).pack(side=tk.LEFT, padx=2)

        # Section selector row
        section_row = ttk.Frame(selector_frame)
        section_row.pack(fill=tk.X)

        ttk.Label(section_row, text="Section:").pack(side=tk.LEFT, padx=5)
        self.section_selector_var = tk.StringVar()
        self.section_selector = ttk.Combobox(section_row, textvariable=self.section_selector_var,
                                            width=50, state='readonly')
        self.section_selector.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.section_selector.bind('<<ComboboxSelected>>', self.on_section_selected)

        ttk.Button(section_row, text="🔄 Refresh Sections",
                  command=self.refresh_video_sections).pack(side=tk.LEFT, padx=5)

        # Video settings
        video_settings_frame = ttk.LabelFrame(phase3_frame, text="Video Settings", padding="10")
        video_settings_frame.pack(fill=tk.X, pady=5)

        row = 0
        ttk.Label(video_settings_frame, text="Duration per image (seconds):").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.image_duration_var = tk.StringVar(value="5")
        ttk.Spinbox(video_settings_frame, from_=1, to=30, textvariable=self.image_duration_var, width=10).grid(row=row, column=1, sticky=tk.W)

        ttk.Label(video_settings_frame, text="Transition:").grid(row=row, column=2, sticky=tk.W, padx=(20, 5))
        self.transition_var = tk.StringVar(value="crossfade")
        transitions = ["crossfade", "fade", "wipe", "slide", "none"]
        ttk.Combobox(video_settings_frame, textvariable=self.transition_var, values=transitions,
                    width=15, state='readonly').grid(row=row, column=3, sticky=tk.W)

        row += 1
        ttk.Label(video_settings_frame, text="Transition duration (seconds):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.transition_duration_var = tk.StringVar(value="1")
        ttk.Spinbox(video_settings_frame, from_=0.1, to=5, increment=0.1, textvariable=self.transition_duration_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5)

        ttk.Label(video_settings_frame, text="Resolution:").grid(row=row, column=2, sticky=tk.W, padx=(20, 5), pady=5)
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolutions = ["1920x1080", "1280x720", "3840x2160", "1024x1024"]
        ttk.Combobox(video_settings_frame, textvariable=self.resolution_var, values=resolutions,
                    width=15, state='readonly').grid(row=row, column=3, sticky=tk.W, pady=5)

        row += 1
        ttk.Label(video_settings_frame, text="FPS:").grid(row=row, column=0, sticky=tk.W, padx=5)
        self.fps_var = tk.StringVar(value="30")
        ttk.Spinbox(video_settings_frame, from_=24, to=60, textvariable=self.fps_var, width=10).grid(row=row, column=1, sticky=tk.W)

        # Audio settings
        audio_frame = ttk.LabelFrame(phase3_frame, text="Audio & Subtitles", padding="10")
        audio_frame.pack(fill=tk.X, pady=5)

        row = 0
        ttk.Label(audio_frame, text="Voiceover:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.voiceover_path_var = tk.StringVar()
        ttk.Entry(audio_frame, textvariable=self.voiceover_path_var, width=40).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(audio_frame, text="📂 Browse", command=self.browse_voiceover).grid(row=row, column=2, padx=5, pady=5)
        ttk.Button(audio_frame, text="🎤 Generate SRT", command=self.generate_srt).grid(row=row, column=3, padx=5, pady=5)

        row += 1
        ttk.Label(audio_frame, text="SRT Subtitles:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.srt_path_var = tk.StringVar()
        ttk.Entry(audio_frame, textvariable=self.srt_path_var, width=40).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(audio_frame, text="📂 Browse", command=self.browse_srt).grid(row=row, column=2, padx=5, pady=5)
        ttk.Button(audio_frame, text="📝 Edit SRT", command=self.edit_srt).grid(row=row, column=3, padx=5, pady=5)

        row += 1
        ttk.Label(audio_frame, text="Background Music:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.music_path_var = tk.StringVar()
        ttk.Entry(audio_frame, textvariable=self.music_path_var, width=40).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(audio_frame, text="📂 Browse", command=self.browse_music).grid(row=row, column=2, padx=5, pady=5)

        row += 1
        ttk.Label(audio_frame, text="Music volume (%):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.music_volume_var = tk.StringVar(value="30")
        ttk.Spinbox(audio_frame, from_=0, to=100, textvariable=self.music_volume_var, width=10).grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1
        ttk.Label(audio_frame, text="OpenAI API Key:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.openai_api_key_var = tk.StringVar(value=self.config.get('openai_api_key', ''))
        ttk.Entry(audio_frame, textvariable=self.openai_api_key_var, width=40, show='*').grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(audio_frame, text="(Required for Whisper SRT generation)", foreground='gray').grid(row=row, column=2, columnspan=2, sticky=tk.W, padx=5)

        # Render button
        render_frame = ttk.Frame(phase3_frame)
        render_frame.pack(pady=10)

        self.render_button = ttk.Button(render_frame, text="🎬 Render Video",
                                       command=self.render_video, width=20)
        self.render_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(render_frame, text="📂 Open Videos Folder",
                  command=self.open_videos_folder, width=20).pack(side=tk.LEFT, padx=5)

        # Video log
        video_log_frame = ttk.LabelFrame(phase3_frame, text="Render Log", padding="10")
        video_log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.video_log_text = scrolledtext.ScrolledText(video_log_frame, height=12, width=90, state='disabled')
        self.video_log_text.pack(fill=tk.BOTH, expand=True)

        instructions3 = ttk.Label(phase3_frame,
            text="💡 Tip: Make sure ffmpeg is installed! Download from ffmpeg.org\nVoiceover and music are optional. SRT subtitles can be auto-generated or manually created.",
            font=('Arial', 9), foreground='#ce9178', wraplength=900, justify=tk.LEFT)
        instructions3.pack(pady=5)

        # PHASE 4 TAB - MULTI-LANGUAGE SRT
        phase4_frame = ttk.Frame(notebook, padding="10")
        notebook.add(phase4_frame, text="🌍 Phase 4: Multi-Language SRT")

        ttk.Label(phase4_frame, text="Phase 4: Generate Multi-Language Subtitles",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Original SRT selection
        srt_select_frame = ttk.LabelFrame(phase4_frame, text="Original SRT File", padding="10")
        srt_select_frame.pack(fill=tk.X, pady=5)

        self.phase4_srt_var = tk.StringVar()
        ttk.Entry(srt_select_frame, textvariable=self.phase4_srt_var, width=70).pack(side=tk.LEFT, padx=5)
        ttk.Button(srt_select_frame, text="📂 Browse", command=self.browse_phase4_srt).pack(side=tk.LEFT, padx=5)
        ttk.Button(srt_select_frame, text="📋 Use from Phase 3", command=self.use_phase3_srt).pack(side=tk.LEFT, padx=5)

        # Language selection
        lang_frame = ttk.LabelFrame(phase4_frame, text="Target Languages", padding="10")
        lang_frame.pack(fill=tk.X, pady=5)

        self.lang_vars = {}
        languages = [
            ('de', 'German 🇩🇪'), ('es', 'Spanish 🇪🇸'), ('fr', 'French 🇫🇷'),
            ('it', 'Italian 🇮🇹'), ('pt', 'Portuguese 🇵🇹'), ('ja', 'Japanese 🇯🇵'),
            ('ko', 'Korean 🇰🇷'), ('zh', 'Chinese 🇨🇳'), ('ru', 'Russian 🇷🇺'), ('ar', 'Arabic 🇸🇦')
        ]

        for i, (code, name) in enumerate(languages):
            row, col = divmod(i, 2)
            var = tk.BooleanVar()
            self.lang_vars[code] = var
            ttk.Checkbutton(lang_frame, text=name, variable=var).grid(row=row, column=col, sticky=tk.W, padx=20, pady=2)

        # Generate button
        ttk.Button(phase4_frame, text="🌍 Generate Multi-Language SRT Files",
                  command=self.generate_multilang_srt, width=40).pack(pady=10)

        # Output list
        output_frame = ttk.LabelFrame(phase4_frame, text="Generated SRT Files", padding="10")
        output_frame.pack(fill=tk.X, pady=5)

        self.phase4_listbox = tk.Listbox(output_frame, height=6)
        self.phase4_listbox.pack(fill=tk.X, expand=False, padx=5, pady=5)

        ttk.Button(output_frame, text="📂 Open SRT Folder", command=self.open_srt_folder).pack(pady=5)

        # Phase 4 Log
        phase4_log_frame = ttk.LabelFrame(phase4_frame, text="Translation Log", padding="10")
        phase4_log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.phase4_log_text = scrolledtext.ScrolledText(phase4_log_frame, height=8, width=90, state='disabled')
        self.phase4_log_text.pack(fill=tk.BOTH, expand=True)

        instructions4 = ttk.Label(phase4_frame,
            text="💡 Tip: Upload all generated SRT files to YouTube as multi-language captions!\nEach file is ready to use - just upload them in YouTube Studio > Subtitles section.",
            font=('Arial', 9), foreground='#4ec9b0', wraplength=900, justify=tk.LEFT)
        instructions4.pack(pady=5)

    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def load_story_file(self):
        filename = filedialog.askopenfilename(
            title="Select Story File",
            filetypes=[("Text files", "*.txt"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    story = f.read()
                self.story_text.delete('1.0', tk.END)
                self.story_text.insert('1.0', story)
                messagebox.showinfo("Success", f"Loaded {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def copy_story(self):
        story = self.story_text.get('1.0', tk.END).strip()
        if story:
            pyperclip.copy(story)
            messagebox.showinfo("Copied!", "Story copied to clipboard!\nNow copy the prompt below and paste both into ChatGPT.")
        else:
            messagebox.showerror("Error", "No story to copy!")

    def copy_phase1_prompt(self):
        story = self.story_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("Error", "Please load a story first!")
            return

        prompt_template = self.phase1_prompt_text.get('1.0', tk.END).strip()
        full_prompt = prompt_template.replace('{story}', story)

        pyperclip.copy(full_prompt)
        messagebox.showinfo("Copied!",
            "Full prompt (with your story) copied to clipboard!\n\n" +
            "Next steps:\n" +
            "1. Paste into ChatGPT\n" +
            "2. Wait for response\n" +
            "3. Copy ChatGPT's response\n" +
            "4. Go to Phase 2 tab\n" +
            "5. Click 'Paste from Clipboard'")

    def phase1_log(self, message, level='INFO'):
        """Log messages to Phase 1 log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.phase1_log_text.config(state='normal')
        self.phase1_log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.phase1_log_text.see(tk.END)
        self.phase1_log_text.config(state='disabled')
        self.root.update()

    def chunk_via_api(self):
        """Chunk story via OpenAI API"""
        story = self.story_text.get('1.0', tk.END).strip()
        if not story:
            messagebox.showerror("Error", "Please load a story first!")
            return

        api_key = self.openai_api_key_var.get().strip()
        if not api_key:
            response = messagebox.askyesno("API Key Required",
                "OpenAI API key required for automatic chunking.\n\n" +
                "You can enter it in Phase 3, or click Yes to enter it now.\n\n" +
                "Get your API key at: https://platform.openai.com/api-keys")
            if response:
                # Switch to Phase 3 tab (where API key input is)
                messagebox.showinfo("Enter API Key", "Please enter your API key in Phase 3 (Audio & Subtitles section)")
            return

        self.phase1_log("🤖 Starting API chunking...", "INFO")

        # Run in thread
        thread = threading.Thread(target=self._chunk_via_api_worker, args=(story, api_key), daemon=True)
        thread.start()

    def _chunk_via_api_worker(self, story, api_key):
        """Worker thread for API chunking"""
        try:
            from openai import OpenAI
            import httpx

            # Create client with timeout (5 min for large responses)
            client = OpenAI(
                api_key=api_key,
                timeout=httpx.Timeout(300.0, connect=10.0)
            )

            prompt_template = self.phase1_prompt_text.get('1.0', tk.END).strip()
            full_prompt = prompt_template.replace('{story}', story)

            self.phase1_log("📤 Sending story to OpenAI API...", "INFO")
            self.phase1_log(f"Story length: {len(story)} characters", "DEBUG")
            self.phase1_log("⏱️ Timeout: 5 minutes", "DEBUG")

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            chunked_text = response.choices[0].message.content

            self.phase1_log(f"✅ Received response ({len(chunked_text)} chars)", "SUCCESS")

            # Parse sections directly
            self.phase1_log("✂️ Parsing sections...", "INFO")

            # Use the same parsing logic as Phase 2
            pattern = r'(?:===\s*)?SECTION\s+\d+:\s*([^\n=]+?)(?:\s*===)?\s*\n(.*?)(?=(?:===\s*)?SECTION\s+\d+:|$)'
            matches = re.findall(pattern, chunked_text, re.DOTALL | re.IGNORECASE)

            if not matches:
                # Try alternative format
                pattern = r'(?:#+\s*)?Section\s+\d+[:\-]\s*([^\n]+)\s*\n(.*?)(?=(?:#+\s*)?Section\s+\d+[:\-]|$)'
                matches = re.findall(pattern, chunked_text, re.DOTALL | re.IGNORECASE)

            if not matches:
                self.phase1_log("❌ Could not parse sections from API response", "ERROR")
                messagebox.showerror("Parse Error",
                    "Could not parse sections from API response!\n\n" +
                    "The response has been copied to Phase 2 - you can parse it manually.")
                # Copy to Phase 2 anyway
                self.sections_text.delete('1.0', tk.END)
                self.sections_text.insert('1.0', chunked_text)
                return

            # Create sections
            self.sections = []
            for title, content in matches:
                self.sections.append({
                    'title': title.strip(),
                    'text': content.strip()
                })

            # Create folders
            for i, section in enumerate(self.sections, 1):
                folder_name = f"section_{i:02d}_{self.sanitize_filename(section['title'])}"
                section_folder = self.output_folder / folder_name
                section_folder.mkdir(exist_ok=True)
                section['folder'] = section_folder

            self.phase1_log(f"✅ Parsed {len(self.sections)} sections!", "SUCCESS")

            # Save project
            self.save_current_project()

            # Update Phase 2 display
            self.sections_text.delete('1.0', tk.END)
            self.sections_text.insert('1.0', chunked_text)

            self.sections_count_label.config(text=f"Sections found: {len(self.sections)}")
            self.update_progress()

            self.phase1_log("💾 Project saved! Ready for Phase 2.", "SUCCESS")

            messagebox.showinfo("Success!",
                f"✅ Story chunked via API!\n\n" +
                f"Found {len(self.sections)} sections\n\n" +
                "Project saved. You can now:\n" +
                "• Go to Phase 2 to generate images\n" +
                "• Or go to Phase 3 to create videos")

        except Exception as e:
            self.phase1_log(f"❌ API error: {e}", "ERROR")

            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                messagebox.showerror("API Error",
                    f"Invalid API Key!\n\n{e}\n\n" +
                    "Get your API key at: https://platform.openai.com/api-keys\n\n" +
                    "Enter it in Phase 3 (Audio & Subtitles section)")
            else:
                messagebox.showerror("Error", f"API chunking failed:\n\n{e}")

    def paste_sections(self):
        try:
            clipboard_content = pyperclip.paste()
            self.sections_text.delete('1.0', tk.END)
            self.sections_text.insert('1.0', clipboard_content)
            messagebox.showinfo("Pasted!", "ChatGPT's response pasted!\n\nNow click 'Parse Sections' to extract the sections.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste: {e}")

    def parse_sections(self):
        text = self.sections_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showerror("Error", "No text to parse!")
            return

        # Parse sections using regex
        # Looking for patterns like "=== SECTION 1: Title ===" or "SECTION 1: Title"
        pattern = r'(?:===\s*)?SECTION\s+\d+:\s*([^\n=]+?)(?:\s*===)?\s*\n(.*?)(?=(?:===\s*)?SECTION\s+\d+:|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        if not matches:
            # Try alternative format
            pattern = r'(?:#+\s*)?Section\s+\d+[:\-]\s*([^\n]+)\s*\n(.*?)(?=(?:#+\s*)?Section\s+\d+[:\-]|$)'
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        if not matches:
            messagebox.showerror("Error",
                "Could not parse sections!\n\n" +
                "Make sure ChatGPT formatted the response with clear section markers like:\n" +
                "=== SECTION 1: Title ===\n" +
                "or\n" +
                "Section 1: Title")
            return

        self.sections = []
        for title, content in matches:
            self.sections.append({
                'title': title.strip(),
                'text': content.strip()
            })

        self.sections_count_label.config(text=f"Sections found: {len(self.sections)}")
        self.log(f"✓ Parsed {len(self.sections)} sections successfully!", "SUCCESS")
        self.update_progress()

        # Create folders for each section
        for i, section in enumerate(self.sections, 1):
            folder_name = f"section_{i:02d}_{self.sanitize_filename(section['title'])}"
            section_folder = self.output_folder / folder_name
            section_folder.mkdir(exist_ok=True)
            section['folder'] = section_folder

        # Save project
        self.save_current_project()

        messagebox.showinfo("Success!",
            f"Parsed {len(self.sections)} sections!\n\n" +
            f"Created folders in:\n{self.output_folder}\n\n" +
            "Project saved! You can load it later from any phase.\n\n" +
            "Ready to start image generation!")

    def sanitize_filename(self, name):
        # Remove invalid filename characters
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        name = name.replace(' ', '_')
        return name[:50]  # Limit length

    def update_progress(self):
        total_sections = len(self.sections)
        images_per = int(self.images_per_section_var.get())
        self.progress_label.config(
            text=f"Section: {self.current_section_index}/{total_sections} | Image: {self.current_image_count}/{images_per}"
        )

    def open_output_folder(self):
        import os
        import subprocess
        if self.output_folder.exists():
            if os.name == 'nt':  # Windows
                os.startfile(self.output_folder)
            elif os.name == 'posix':  # Mac/Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(self.output_folder)])
        else:
            messagebox.showinfo("Info", "Output folder will be created when you start the process.")

    def process_thread_func(self):
        try:
            interval = float(self.interval_var.get())
            startup_delay = float(self.startup_delay_var.get())
            images_per_section = int(self.images_per_section_var.get())
            continue_command = self.continue_command_var.get()

            # Startup delay
            if startup_delay > 0:
                self.log(f"Starting in {startup_delay} seconds... Switch to ChatGPT!", "INFO")
                for i in range(int(startup_delay), 0, -1):
                    if not self.is_running:
                        return
                    self.log(f"Starting in {i}...", "INFO")
                    time.sleep(1)

            self.log("🎬 Process started!", "SUCCESS")

            # Process each section
            for section_idx, section in enumerate(self.sections):
                if not self.is_running:
                    break

                self.current_section_index = section_idx + 1
                self.current_image_count = 0
                self.update_progress()

                title = section['title']
                text = section['text']
                folder = section['folder']

                self.log(f"━━━ Processing Section {section_idx + 1}/{len(self.sections)}: {title} ━━━", "INFO")
                self.log(f"📁 Images will go in: {folder.name}", "INFO")

                # Generate the prompt
                template = self.image_prompt_template_text.get('1.0', tk.END).strip()
                prompt = template.format(title=title, text=text)

                # Copy prompt to clipboard and paste (more reliable than typing)
                self.log("⌨️  Pasting section prompt via clipboard...", "INFO")
                pyperclip.copy(prompt)
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'v')  # Paste
                time.sleep(1)  # Wait for paste to complete
                pyautogui.press('enter')
                self.log("✓ Section prompt sent!", "SUCCESS")

                # Wait for first image
                self.current_image_count = 1
                self.update_progress()
                self.log(f"⏳ Waiting {interval}s for first image...", "INFO")
                sleep_end = time.time() + interval
                while self.is_running and time.time() < sleep_end:
                    time.sleep(0.1)

                # Send continue commands for remaining images
                for img_num in range(2, images_per_section + 1):
                    if not self.is_running:
                        break

                    self.current_image_count = img_num
                    self.update_progress()

                    self.log(f"⌨️  Requesting image {img_num}/{images_per_section}...", "INFO")
                    pyautogui.write(continue_command)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    self.log(f"✓ Continue command sent", "SUCCESS")

                    # Wait for next image
                    self.log(f"⏳ Waiting {interval}s for image generation...", "INFO")
                    sleep_end = time.time() + interval
                    while self.is_running and time.time() < sleep_end:
                        time.sleep(0.1)

                self.current_image_count = images_per_section
                self.update_progress()
                self.log(f"✅ Completed section {section_idx + 1}: {title}", "SUCCESS")
                self.log(f"💾 Reminder: Save the {images_per_section} images to: {folder}", "INFO")

                # Pause before next section
                if section_idx < len(self.sections) - 1:
                    self.log("⏸️  Pausing 5 seconds before next section...", "INFO")
                    time.sleep(5)

            if self.is_running:
                self.log("🎉 ALL SECTIONS COMPLETED!", "SUCCESS")
                self.log(f"📂 All images should be saved in: {self.output_folder}", "SUCCESS")
                messagebox.showinfo("Complete!",
                    f"Generated images for all {len(self.sections)} sections!\n\n" +
                    f"Don't forget to download and organize the images in:\n{self.output_folder}")

        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
        finally:
            if self.is_running:
                self.stop_process()

    def start_process(self):
        if self.is_running:
            return

        if not self.sections:
            messagebox.showerror("Error", "No sections parsed!\n\nGo to Phase 2 tab and paste ChatGPT's response, then click 'Parse Sections'.")
            return

        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="🟢 Running", foreground='green')

        self.current_section_index = 0
        self.current_image_count = 0

        self.thread = threading.Thread(target=self.process_thread_func, daemon=True)
        self.thread.start()

    def stop_process(self):
        if not self.is_running:
            return

        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="⚫ Stopped", foreground='red')
        self.log("⏹️  Process stopped!", "INFO")

    def save_config(self):
        config = {
            'phase1_prompt': self.phase1_prompt_text.get('1.0', tk.END).strip(),
            'images_per_section': int(self.images_per_section_var.get()),
            'image_prompt_template': self.image_prompt_template_text.get('1.0', tk.END).strip(),
            'continue_command': self.continue_command_var.get(),
            'interval': float(self.interval_var.get()),
            'startup_delay': float(self.startup_delay_var.get())
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log("💾 Configuration saved!", "SUCCESS")
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            self.log(f"❌ Failed to save config: {e}", "ERROR")

    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.config = {}
        else:
            self.config = {}

    def on_closing(self):
        if self.is_running:
            if messagebox.askokcancel("Quit", "Process is still running. Stop and quit?"):
                self.stop_process()
                self.root.destroy()
        else:
            self.root.destroy()

    # ========== PROJECT MANAGEMENT METHODS ==========

    def save_current_project(self):
        """Save current project to projects folder"""
        if not self.sections:
            return

        # Generate project name from first section title or timestamp
        if self.current_project_name:
            project_name = self.current_project_name
        else:
            first_title = self.sections[0]['title'] if self.sections else "Untitled"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{self.sanitize_filename(first_title)}_{timestamp}"
            self.current_project_name = project_name

        project_file = self.projects_folder / f"{project_name}.json"

        # Prepare project data
        project_data = {
            'name': project_name,
            'created': datetime.now().isoformat(),
            'sections': []
        }

        for section in self.sections:
            section_data = {
                'title': section['title'],
                'text': section['text'],
                'folder': str(section.get('folder', ''))
            }
            project_data['sections'].append(section_data)

        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            self.log(f"💾 Project saved: {project_name}", "SUCCESS")
            self.refresh_project_list()
        except Exception as e:
            self.log(f"❌ Failed to save project: {e}", "ERROR")

    def refresh_project_list(self):
        """Refresh the list of available projects"""
        if not self.projects_folder.exists():
            return

        project_files = sorted(self.projects_folder.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        project_names = [f.stem for f in project_files]

        # Update all project selectors
        self.phase2_project_selector['values'] = project_names
        self.phase3_project_selector['values'] = project_names

        if project_names and hasattr(self, 'phase2_project_var'):
            # Auto-select most recent project if nothing selected
            if not self.phase2_project_var.get():
                self.phase2_project_selector.current(0)
            if not self.phase3_project_var.get():
                self.phase3_project_selector.current(0)

    def load_selected_project(self, event=None):
        """Load project selected in Phase 2"""
        project_name = self.phase2_project_var.get()
        if not project_name:
            return

        self.load_project(project_name)

    def phase3_load_project(self, event=None):
        """Load project selected in Phase 3"""
        project_name = self.phase3_project_var.get()
        if not project_name:
            return

        self.load_project(project_name)
        # Refresh sections after loading project
        self.refresh_video_sections()

    def load_project(self, project_name):
        """Load a project from the projects folder"""
        project_file = self.projects_folder / f"{project_name}.json"

        if not project_file.exists():
            messagebox.showerror("Error", f"Project file not found: {project_name}")
            return

        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)

            # Load sections
            self.sections = []
            for section_data in project_data['sections']:
                section = {
                    'title': section_data['title'],
                    'text': section_data['text'],
                    'folder': Path(section_data['folder']) if section_data.get('folder') else None
                }
                self.sections.append(section)

            self.current_project_name = project_name
            self.sections_count_label.config(text=f"Sections found: {len(self.sections)}")
            self.update_progress()

            # Update Phase 2 display
            if hasattr(self, 'sections_text'):
                self.sections_text.delete('1.0', tk.END)
                display_text = ""
                for i, section in enumerate(self.sections, 1):
                    display_text += f"=== SECTION {i}: {section['title']} ===\n{section['text']}\n\n"
                self.sections_text.insert('1.0', display_text.strip())

            self.log(f"✓ Loaded project: {project_name} ({len(self.sections)} sections)", "SUCCESS")
            messagebox.showinfo("Success!", f"Loaded project: {project_name}\n\n{len(self.sections)} sections loaded!")

        except Exception as e:
            self.log(f"❌ Failed to load project: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to load project:\n{e}")

    # ========== PHASE 3: VIDEO PRODUCTION METHODS ==========

    def video_log(self, message, level='INFO'):
        """Log messages to video production log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.video_log_text.config(state='normal')
        self.video_log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.video_log_text.see(tk.END)
        self.video_log_text.config(state='disabled')
        self.root.update()

    def phase4_log(self, message, level='INFO'):
        """Log messages to Phase 4 translation log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.phase4_log_text.config(state='normal')
        self.phase4_log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")
        self.phase4_log_text.see(tk.END)
        self.phase4_log_text.config(state='disabled')
        self.root.update()

    def refresh_video_sections(self):
        """Refresh the list of available sections for video production"""
        if not self.output_folder.exists():
            messagebox.showinfo("Info", "No sections found. Complete Phase 2 first!")
            return

        # Find all section folders
        section_folders = sorted([f for f in self.output_folder.iterdir() if f.is_dir() and f.name.startswith('section_')])

        if not section_folders:
            messagebox.showinfo("Info", "No section folders found. Complete Phase 2 first!")
            return

        # Update combobox
        section_names = [f.name for f in section_folders]
        self.section_selector['values'] = section_names

        if section_names:
            self.section_selector.current(0)
            self.on_section_selected(None)

        self.video_log(f"✓ Found {len(section_names)} sections", "SUCCESS")

    def on_section_selected(self, event):
        """Handle section selection"""
        selection = self.section_selector_var.get()
        if selection:
            self.video_log(f"Selected section: {selection}", "INFO")

    def browse_voiceover(self):
        """Browse for voiceover audio file"""
        filename = filedialog.askopenfilename(
            title="Select Voiceover Audio",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.ogg"), ("All files", "*.*")]
        )
        if filename:
            self.voiceover_path_var.set(filename)
            self.video_log(f"✓ Voiceover selected: {Path(filename).name}", "SUCCESS")

    def browse_srt(self):
        """Browse for SRT subtitle file"""
        filename = filedialog.askopenfilename(
            title="Select SRT Subtitle File",
            filetypes=[("Subtitle files", "*.srt"), ("All files", "*.*")]
        )
        if filename:
            self.srt_path_var.set(filename)
            self.video_log(f"✓ SRT file selected: {Path(filename).name}", "SUCCESS")

    def browse_music(self):
        """Browse for background music file"""
        filename = filedialog.askopenfilename(
            title="Select Background Music",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.ogg"), ("All files", "*.*")]
        )
        if filename:
            self.music_path_var.set(filename)
            self.video_log(f"✓ Music selected: {Path(filename).name}", "SUCCESS")

    def generate_srt(self):
        """Generate SRT subtitles from voiceover using OpenAI Whisper"""
        voiceover = self.voiceover_path_var.get()
        if not voiceover or not Path(voiceover).exists():
            messagebox.showerror("Error", "Please select a voiceover file first!")
            return

        api_key = self.openai_api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your OpenAI API Key first!\n\nGet one at: https://platform.openai.com/api-keys")
            return

        # Run Whisper in thread
        self.video_log(f"🎤 Starting Whisper transcription for: {Path(voiceover).name}", "INFO")
        self.video_log("This may take a minute...", "INFO")

        thread = threading.Thread(target=self._whisper_thread, args=(voiceover, api_key), daemon=True)
        thread.start()

    def _compress_audio(self, audio_path):
        """Compress audio file to meet Whisper's 25 MB limit"""
        try:
            self.video_log("🗜️ Compressing audio with ffmpeg...", "INFO")

            # Check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except:
                self.video_log("❌ ffmpeg not found! Please install ffmpeg.", "ERROR")
                messagebox.showerror("Error",
                    "ffmpeg is required for audio compression!\n\n" +
                    "Download from: https://ffmpeg.org/download.html\n" +
                    "Or try reducing the audio file size manually.")
                return None

            # Create compressed version
            compressed_path = audio_path.with_stem(audio_path.stem + "_compressed")

            # Calculate target bitrate dynamically
            # Get audio duration first
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)]
            try:
                duration_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
                duration_sec = float(duration_result.stdout.strip())

                # Target: 20 MB (leave 5 MB buffer for safety)
                target_size_mb = 20
                target_size_bytes = target_size_mb * 1024 * 1024
                target_bitrate = int((target_size_bytes * 8) / duration_sec)  # bits per second
                target_bitrate_k = max(16, min(64, target_bitrate // 1000))  # Clamp between 16-64 kbps

                self.video_log(f"📊 Audio duration: {duration_sec:.1f}s, target bitrate: {target_bitrate_k}k", "DEBUG")
            except:
                # Fallback to conservative bitrate
                target_bitrate_k = 24
                self.video_log(f"⚠️ Could not determine duration, using {target_bitrate_k}k", "DEBUG")

            cmd = [
                'ffmpeg', '-y', '-i', str(audio_path),
                '-ab', f'{target_bitrate_k}k',  # Dynamic bitrate
                '-ac', '1',     # Mono
                '-ar', '16000', # Lower sample rate (Whisper optimized)
                '-map', '0:a',  # Only audio stream
                str(compressed_path)
            ]

            self.video_log(f"Running: ffmpeg -i input -ab {target_bitrate_k}k -ac 1 -ar 16000 output", "DEBUG")

            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode != 0:
                self.video_log(f"❌ Compression failed: {process.stderr}", "ERROR")
                return None

            self.video_log(f"✓ Compressed audio saved", "SUCCESS")
            return compressed_path

        except Exception as e:
            self.video_log(f"❌ Compression error: {e}", "ERROR")
            return None

    def _whisper_thread(self, audio_file, api_key):
        """Thread function for Whisper API transcription"""
        try:
            from openai import OpenAI

            self.video_log("🔄 Connecting to OpenAI Whisper API...", "INFO")

            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Open audio file
            audio_path = Path(audio_file)
            file_size_mb = audio_path.stat().st_size / (1024 * 1024)
            self.video_log(f"📤 Audio file size: {file_size_mb:.1f} MB", "INFO")

            # Check file size - Whisper API has 25 MB limit
            original_path = audio_path
            if file_size_mb > 25:
                self.video_log(f"⚠️ File too large ({file_size_mb:.1f} MB > 25 MB), compressing...", "INFO")
                audio_path = self._compress_audio(audio_path)
                if audio_path is None:
                    return  # Error message already shown
                file_size_mb = audio_path.stat().st_size / (1024 * 1024)
                self.video_log(f"✓ Compressed to {file_size_mb:.1f} MB", "SUCCESS")

            self.video_log(f"📤 Uploading to Whisper ({file_size_mb:.1f} MB)...", "INFO")

            with open(audio_path, 'rb') as audio:
                # Call Whisper API
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="srt"  # Get SRT format directly!
                )

            # Save SRT file (next to original audio file, not compressed)
            srt_path = original_path.with_suffix('.srt')
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(transcript)

            # Clean up compressed file if it was created
            if audio_path != original_path and audio_path.exists():
                audio_path.unlink()
                self.video_log("🗑️ Cleaned up compressed file", "DEBUG")

            self.srt_path_var.set(str(srt_path))
            self.video_log(f"✅ SRT generated successfully!", "SUCCESS")
            self.video_log(f"📁 Saved to: {srt_path.name}", "SUCCESS")

            # Save API key to config
            config = self.config.copy()
            config['openai_api_key'] = api_key
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            messagebox.showinfo("Success!",
                f"SRT subtitles generated successfully!\n\n" +
                f"File: {srt_path.name}\n\n" +
                "You can now edit the subtitles if needed.")

        except Exception as e:
            self.video_log(f"❌ Whisper failed: {e}", "ERROR")
            error_msg = str(e)

            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                messagebox.showerror("API Error",
                    f"Invalid API Key!\n\n{e}\n\n" +
                    "Get your API key at: https://platform.openai.com/api-keys")
            elif "file" in error_msg.lower() or "format" in error_msg.lower():
                messagebox.showerror("File Error",
                    f"Audio file error!\n\n{e}\n\n" +
                    "Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm")
            else:
                messagebox.showerror("Error", f"Whisper transcription failed:\n\n{e}")

    def open_srt_editor(self, audio_file):
        """Open a simple SRT editor window"""
        editor = tk.Toplevel(self.root)
        editor.title("SRT Subtitle Editor")
        editor.geometry("800x600")

        ttk.Label(editor, text=f"Create subtitles for: {Path(audio_file).name}",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        instructions = ttk.Label(editor,
            text="SRT Format:\n1\n00:00:00,000 --> 00:00:05,000\nFirst subtitle text\n\n2\n00:00:05,000 --> 00:00:10,000\nSecond subtitle text",
            font=('Arial', 9), foreground='gray', justify=tk.LEFT)
        instructions.pack(pady=5)

        text_frame = ttk.Frame(editor)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        srt_text = scrolledtext.ScrolledText(text_frame, width=80, height=25)
        srt_text.pack(fill=tk.BOTH, expand=True)

        # Load existing SRT if available
        srt_path = Path(audio_file).with_suffix('.srt')
        if srt_path.exists():
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_text.insert('1.0', f.read())

        def save_srt():
            content = srt_text.get('1.0', tk.END).strip()
            try:
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.srt_path_var.set(str(srt_path))
                self.video_log(f"✓ SRT saved: {srt_path.name}", "SUCCESS")
                messagebox.showinfo("Success", f"SRT file saved to:\n{srt_path}")
                editor.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save SRT: {e}")

        button_frame = ttk.Frame(editor)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="💾 Save SRT", command=save_srt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=editor.destroy).pack(side=tk.LEFT, padx=5)

    def edit_srt(self):
        """Edit existing SRT file"""
        srt_file = self.srt_path_var.get()
        if not srt_file or not Path(srt_file).exists():
            messagebox.showerror("Error", "Please select an SRT file first!")
            return

        self.open_srt_editor_existing(srt_file)

    def open_srt_editor_existing(self, srt_file):
        """Open SRT editor for existing file"""
        editor = tk.Toplevel(self.root)
        editor.title("Edit SRT Subtitles")
        editor.geometry("800x600")

        ttk.Label(editor, text=f"Editing: {Path(srt_file).name}",
                 font=('Arial', 12, 'bold')).pack(pady=10)

        text_frame = ttk.Frame(editor)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        srt_text = scrolledtext.ScrolledText(text_frame, width=80, height=25)
        srt_text.pack(fill=tk.BOTH, expand=True)

        # Load SRT
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_text.insert('1.0', f.read())

        def save_srt():
            content = srt_text.get('1.0', tk.END).strip()
            try:
                with open(srt_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.video_log(f"✓ SRT updated: {Path(srt_file).name}", "SUCCESS")
                messagebox.showinfo("Success", "SRT file updated!")
                editor.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save SRT: {e}")

        button_frame = ttk.Frame(editor)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="💾 Save", command=save_srt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=editor.destroy).pack(side=tk.LEFT, padx=5)

    def render_video(self):
        """Render video for selected section"""
        section_name = self.section_selector_var.get()
        if not section_name:
            messagebox.showerror("Error", "Please select a section first!")
            return

        section_folder = self.output_folder / section_name

        # Check for images
        image_files = sorted(list(section_folder.glob("*.png")) + list(section_folder.glob("*.jpg")))
        if not image_files:
            messagebox.showerror("Error", f"No images found in {section_name}!\nPlease add images first.")
            return

        self.video_log(f"🎬 Starting render for: {section_name}", "INFO")
        self.video_log(f"Found {len(image_files)} images", "INFO")

        # Run render in thread
        thread = threading.Thread(target=self._render_video_thread, args=(section_folder, image_files), daemon=True)
        thread.start()

    def _render_video_thread(self, section_folder, image_files):
        """Thread function for video rendering"""
        try:
            # Get settings
            duration = float(self.image_duration_var.get())
            transition = self.transition_var.get()
            transition_duration = float(self.transition_duration_var.get())
            resolution = self.resolution_var.get()
            fps = int(self.fps_var.get())
            voiceover = self.voiceover_path_var.get()
            srt = self.srt_path_var.get()
            music = self.music_path_var.get()
            music_volume = int(self.music_volume_var.get()) / 100.0

            # Create videos folder
            videos_folder = self.output_folder.parent / "videos"
            videos_folder.mkdir(exist_ok=True)

            output_file = videos_folder / f"{section_folder.name}.mp4"

            self.video_log("Building ffmpeg command...", "INFO")

            # Build ffmpeg command
            cmd = self._build_ffmpeg_command(
                image_files, duration, transition, transition_duration,
                resolution, fps, voiceover, srt, music, music_volume, output_file
            )

            self.video_log("Running ffmpeg...", "INFO")
            self.video_log(f"Command: {' '.join(cmd[:5])}...", "DEBUG")

            # Run ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor progress and collect all stderr
            stderr_output = []
            for line in process.stderr:
                stderr_output.append(line)
                if "frame=" in line or "time=" in line:
                    self.video_log(line.strip(), "DEBUG")

            process.wait()

            if process.returncode == 0:
                self.video_log(f"✅ Video rendered successfully!", "SUCCESS")
                self.video_log(f"📁 Saved to: {output_file}", "SUCCESS")
                messagebox.showinfo("Success!", f"Video created successfully!\n\n{output_file}")
            else:
                # Join all stderr lines for error message
                full_error = ''.join(stderr_output) if stderr_output else "Unknown error - no output from ffmpeg"
                self.video_log(f"❌ ffmpeg failed with return code {process.returncode}", "ERROR")
                # Log last 20 lines of error for debugging
                error_lines = full_error.strip().split('\n')
                for line in error_lines[-20:]:
                    self.video_log(line, "ERROR")
                messagebox.showerror("Error", f"ffmpeg rendering failed!\n\nReturn code: {process.returncode}\n\nCheck the log for details.")

        except Exception as e:
            self.video_log(f"❌ Render error: {e}", "ERROR")
            messagebox.showerror("Error", f"Rendering failed:\n{e}")

    def _build_ffmpeg_command(self, image_files, duration, transition, transition_duration,
                             resolution, fps, voiceover, srt, music, music_volume, output_file):
        """Build ffmpeg command for video rendering"""
        cmd = ['ffmpeg', '-y']  # -y to overwrite

        # Image inputs with duration
        for img in image_files:
            cmd.extend(['-loop', '1', '-t', str(duration), '-i', str(img)])

        # Audio inputs
        audio_inputs = []
        if voiceover and Path(voiceover).exists():
            cmd.extend(['-i', voiceover])
            audio_inputs.append('voiceover')

        if music and Path(music).exists():
            cmd.extend(['-i', music])
            audio_inputs.append('music')

        # Filter complex for transitions and effects
        filter_parts = []

        # Scale and pad all images to same resolution
        width, height = resolution.split('x')
        for i in range(len(image_files)):
            filter_parts.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{i}]")

        # Apply transitions
        if transition == "crossfade" and len(image_files) > 1:
            # Crossfade between images
            current = "[v0]"
            for i in range(1, len(image_files)):
                if i == 1:
                    filter_parts.append(f"{current}[v{i}]xfade=transition=fade:duration={transition_duration}:offset={duration - transition_duration}[v{i}out]")
                    current = f"[v{i}out]"
                else:
                    offset = (duration - transition_duration) * i
                    filter_parts.append(f"{current}[v{i}]xfade=transition=fade:duration={transition_duration}:offset={offset}[v{i}out]")
                    current = f"[v{i}out]"
            video_output = current
        else:
            # Simple concatenation
            video_inputs = "".join([f"[v{i}]" for i in range(len(image_files))])
            filter_parts.append(f"{video_inputs}concat=n={len(image_files)}:v=1:a=0[vout]")
            video_output = "[vout]"

        # NOTE: Subtitles are disabled for now due to ffmpeg filter_complex issues on Windows
        # with non-ASCII paths (even when copied to temp folder with 8.3 short names).
        #
        # The SRT file is generated and can be:
        # 1. Uploaded separately to YouTube as captions
        # 2. Burned in using a video editor
        # 3. Added using a two-pass ffmpeg approach (future enhancement)
        #
        # Future fix: Use two-pass rendering:
        #   Pass 1: Render video without subtitles
        #   Pass 2: Burn subtitles onto the rendered video using -vf subtitle (not filter_complex)

        # Audio mixing
        if audio_inputs:
            audio_idx = len(image_files)
            if len(audio_inputs) == 2:  # Both voiceover and music
                filter_parts.append(f"[{audio_idx}:a]volume=1.0[voice];[{audio_idx+1}:a]volume={music_volume}[music];[voice][music]amix=inputs=2:duration=longest[aout]")
                cmd.extend(['-filter_complex', ';'.join(filter_parts)])
                cmd.extend(['-map', video_output, '-map', '[aout]'])
            else:  # Just one audio
                cmd.extend(['-filter_complex', ';'.join(filter_parts)])
                cmd.extend(['-map', video_output, '-map', f'{audio_idx}:a'])
        else:
            cmd.extend(['-filter_complex', ';'.join(filter_parts)])
            cmd.extend(['-map', video_output])

        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            str(output_file)
        ])

        return cmd

    def open_videos_folder(self):
        """Open the videos output folder"""
        videos_folder = self.output_folder.parent / "videos"
        if videos_folder.exists():
            if os.name == 'nt':  # Windows
                os.startfile(videos_folder)
            else:
                subprocess.run(['open' if os.sys.platform == 'darwin' else 'xdg-open', str(videos_folder)])
        else:
            messagebox.showinfo("Info", "Videos folder will be created when you render your first video.")

    # ========== PHASE 4: MULTI-LANGUAGE SRT METHODS ==========

    def browse_phase4_srt(self):
        """Browse for SRT file"""
        filename = filedialog.askopenfilename(
            title="Select SRT File",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if filename:
            self.phase4_srt_var.set(filename)
            self.phase4_log(f"✓ SRT selected: {Path(filename).name}", "SUCCESS")

    def use_phase3_srt(self):
        """Use SRT from Phase 3"""
        srt_path = self.srt_path_var.get()
        if srt_path and Path(srt_path).exists():
            self.phase4_srt_var.set(srt_path)
            self.phase4_log(f"✓ Using SRT from Phase 3: {Path(srt_path).name}", "SUCCESS")
        else:
            messagebox.showerror("Error", "No SRT file from Phase 3!\nGenerate one in Phase 3 first.")

    def generate_multilang_srt(self):
        """Generate multi-language SRT files"""
        srt_file = self.phase4_srt_var.get()
        if not srt_file or not Path(srt_file).exists():
            messagebox.showerror("Error", "Please select an SRT file first!")
            return

        api_key = self.openai_api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your OpenAI API Key in Phase 3!")
            return

        selected_langs = [code for code, var in self.lang_vars.items() if var.get()]
        if not selected_langs:
            messagebox.showerror("Error", "Please select at least one target language!")
            return

        self.phase4_log(f"🌍 Translating to {len(selected_langs)} languages...", "INFO")

        thread = threading.Thread(
            target=self._translate_srt_worker,
            args=(srt_file, selected_langs, api_key),
            daemon=True
        )
        thread.start()

    def _translate_srt_worker(self, srt_path, target_langs, api_key):
        """Worker thread for SRT translation"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            self.phase4_log(f"📖 Original SRT: {len(srt_content)} chars", "INFO")

            for lang_code in target_langs:
                self.phase4_log(f"🔄 Translating to {lang_code}...", "INFO")

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"Translate this SRT subtitle file to {lang_code}. Keep timestamps and format exactly the same. Only translate the text."},
                            {"role": "user", "content": srt_content}
                        ]
                    )

                    translated = response.choices[0].message.content

                    output_path = Path(srt_path).with_stem(f"{Path(srt_path).stem}_{lang_code}")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(translated)

                    self.phase4_log(f"✅ {lang_code}: {output_path.name}", "SUCCESS")
                    self.phase4_listbox.insert(tk.END, f"{lang_code}: {output_path.name}")

                except Exception as e:
                    self.phase4_log(f"❌ {lang_code} failed: {e}", "ERROR")

            self.phase4_log("🎉 Translation complete!", "SUCCESS")
            messagebox.showinfo("Success!", f"Generated {len(target_langs)} translated SRT files!")

        except Exception as e:
            self.phase4_log(f"❌ Translation error: {e}", "ERROR")
            messagebox.showerror("Error", f"Translation failed:\n{e}")

    def open_srt_folder(self):
        """Open folder containing SRT files"""
        srt_file = self.phase4_srt_var.get()
        if srt_file and Path(srt_file).exists():
            folder = Path(srt_file).parent
            if os.name == 'nt':
                os.startfile(folder)
            else:
                subprocess.run(['open' if os.sys.platform == 'darwin' else 'xdg-open', str(folder)])
        else:
            messagebox.showinfo("Info", "No SRT file selected yet.")


def main():
    try:
        import pyperclip
    except ImportError:
        print("Installing pyperclip for clipboard support...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pyperclip'])
        import pyperclip

    root = tk.Tk()
    app = StoryIllustratorV2(root)
    root.mainloop()


if __name__ == '__main__':
    main()
