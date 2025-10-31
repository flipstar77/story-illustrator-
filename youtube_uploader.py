#!/usr/bin/env python3
"""
YouTube Uploader - Phase 4
Upload videos to YouTube with multi-language subtitles
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
import json
import threading
from datetime import datetime

class YouTubeUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("📺 YouTube Uploader - Phase 4")
        self.root.geometry("900x800")

        # Config
        self.config_file = Path("youtube_config.json")
        self.config = self.load_config()

        # State
        self.video_file = None
        self.srt_files = {}  # {language_code: file_path}

        self.create_ui()

    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            'openai_api_key': '',
            'default_category': '22',  # People & Blogs
            'default_privacy': 'unlisted'
        }

    def save_config(self):
        """Save configuration"""
        self.config['openai_api_key'] = self.api_key_var.get()
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        self.log("💾 Configuration saved", "SUCCESS")

    def create_ui(self):
        """Create the user interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # TAB 1: Multi-Language SRT
        srt_frame = ttk.Frame(notebook, padding="10")
        notebook.add(srt_frame, text="🌍 Multi-Language SRT")

        ttk.Label(srt_frame, text="Generate Multi-Language Subtitles",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Original SRT
        original_frame = ttk.LabelFrame(srt_frame, text="Original SRT (English)", padding="10")
        original_frame.pack(fill=tk.X, pady=5)

        self.original_srt_var = tk.StringVar()
        ttk.Entry(original_frame, textvariable=self.original_srt_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(original_frame, text="📂 Browse", command=self.browse_original_srt).pack(side=tk.LEFT, padx=5)

        # Languages
        languages_frame = ttk.LabelFrame(srt_frame, text="Target Languages", padding="10")
        languages_frame.pack(fill=tk.X, pady=5)

        self.language_vars = {}
        languages = [
            ('de', 'German 🇩🇪'),
            ('es', 'Spanish 🇪🇸'),
            ('fr', 'French 🇫🇷'),
            ('it', 'Italian 🇮🇹'),
            ('pt', 'Portuguese 🇵🇹'),
            ('ja', 'Japanese 🇯🇵'),
            ('ko', 'Korean 🇰🇷'),
            ('zh', 'Chinese 🇨🇳'),
            ('ru', 'Russian 🇷🇺'),
            ('ar', 'Arabic 🇸🇦')
        ]

        for i, (code, name) in enumerate(languages):
            row = i // 2
            col = i % 2
            var = tk.BooleanVar()
            self.language_vars[code] = var
            ttk.Checkbutton(languages_frame, text=name, variable=var).grid(
                row=row, column=col, sticky=tk.W, padx=10, pady=2
            )

        # API Key
        api_frame = ttk.LabelFrame(srt_frame, text="OpenAI API Key", padding="10")
        api_frame.pack(fill=tk.X, pady=5)

        self.api_key_var = tk.StringVar(value=self.config.get('openai_api_key', ''))
        ttk.Entry(api_frame, textvariable=self.api_key_var, width=50, show='*').pack(side=tk.LEFT, padx=5)
        ttk.Button(api_frame, text="💾 Save Key", command=self.save_config).pack(side=tk.LEFT, padx=5)

        # Generate button
        ttk.Button(srt_frame, text="🌍 Generate Multi-Language SRT Files",
                  command=self.generate_translations, width=40).pack(pady=10)

        # Generated SRT list
        list_frame = ttk.LabelFrame(srt_frame, text="Generated SRT Files", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.srt_listbox = tk.Listbox(list_frame, height=10)
        self.srt_listbox.pack(fill=tk.BOTH, expand=True)

        # TAB 2: YouTube Upload
        upload_frame = ttk.Frame(notebook, padding="10")
        notebook.add(upload_frame, text="📺 YouTube Upload")

        ttk.Label(upload_frame, text="Upload Video to YouTube",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 10))

        # Video file
        video_frame = ttk.LabelFrame(upload_frame, text="Video File", padding="10")
        video_frame.pack(fill=tk.X, pady=5)

        self.video_file_var = tk.StringVar()
        ttk.Entry(video_frame, textvariable=self.video_file_var, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(video_frame, text="📂 Browse", command=self.browse_video).pack(side=tk.LEFT, padx=5)

        # Metadata
        meta_frame = ttk.LabelFrame(upload_frame, text="Video Metadata", padding="10")
        meta_frame.pack(fill=tk.X, pady=5)

        row = 0
        ttk.Label(meta_frame, text="Title:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(meta_frame, textvariable=self.title_var, width=60).grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        row += 1
        ttk.Label(meta_frame, text="Description:").grid(row=row, column=0, sticky=tk.NW, padx=5, pady=5)
        self.description_text = tk.Text(meta_frame, height=4, width=60)
        self.description_text.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)

        row += 1
        ttk.Label(meta_frame, text="Tags:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.tags_var = tk.StringVar()
        ttk.Entry(meta_frame, textvariable=self.tags_var, width=60).grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Label(meta_frame, text="(comma separated)", foreground='gray').grid(row=row, column=3, sticky=tk.W)

        row += 1
        ttk.Label(meta_frame, text="Category:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar(value="22")
        categories = [
            ("22", "People & Blogs"),
            ("24", "Entertainment"),
            ("20", "Gaming"),
            ("28", "Science & Technology"),
            ("10", "Music"),
            ("15", "Pets & Animals")
        ]
        category_combo = ttk.Combobox(meta_frame, textvariable=self.category_var, width=30, state='readonly')
        category_combo['values'] = [f"{code}: {name}" for code, name in categories]
        category_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)

        row += 1
        ttk.Label(meta_frame, text="Privacy:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.privacy_var = tk.StringVar(value="unlisted")
        privacy_frame = ttk.Frame(meta_frame)
        privacy_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(privacy_frame, text="Public", variable=self.privacy_var, value='public').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(privacy_frame, text="Unlisted", variable=self.privacy_var, value='unlisted').pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(privacy_frame, text="Private", variable=self.privacy_var, value='private').pack(side=tk.LEFT, padx=5)

        # Thumbnail
        row += 1
        ttk.Label(meta_frame, text="Thumbnail:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.thumbnail_var = tk.StringVar()
        ttk.Entry(meta_frame, textvariable=self.thumbnail_var, width=50).grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(meta_frame, text="📂", command=self.browse_thumbnail).grid(row=row, column=3, padx=5, pady=5)

        # Captions
        captions_frame = ttk.LabelFrame(upload_frame, text="Multi-Language Captions", padding="10")
        captions_frame.pack(fill=tk.X, pady=5)

        self.upload_captions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(captions_frame, text="📝 Upload multi-language captions from Tab 1",
                       variable=self.upload_captions_var).pack(anchor=tk.W, pady=5)

        # Upload button
        upload_btn_frame = ttk.Frame(upload_frame)
        upload_btn_frame.pack(pady=10)

        ttk.Button(upload_btn_frame, text="🔐 Authenticate YouTube",
                  command=self.authenticate_youtube, width=25).pack(side=tk.LEFT, padx=5)

        self.upload_button = ttk.Button(upload_btn_frame, text="📺 Upload to YouTube",
                                       command=self.upload_to_youtube, width=25)
        self.upload_button.pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(upload_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Log
        log_frame = ttk.LabelFrame(upload_frame, text="Upload Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure log colors
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("ERROR", foreground="red")

        self.log("✨ YouTube Uploader initialized!", "SUCCESS")
        self.log("⚠️ Note: YouTube API requires OAuth2 authentication", "INFO")

    def log(self, message, level='INFO'):
        """Add message to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()

    def browse_original_srt(self):
        """Browse for original SRT file"""
        filename = filedialog.askopenfilename(
            title="Select Original SRT",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")]
        )
        if filename:
            self.original_srt_var.set(filename)
            self.log(f"✓ Original SRT selected: {Path(filename).name}", "SUCCESS")

    def browse_video(self):
        """Browse for video file"""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.mov *.avi"), ("All files", "*.*")]
        )
        if filename:
            self.video_file_var.set(filename)
            self.video_file = Path(filename)
            # Auto-fill title from filename
            if not self.title_var.get():
                self.title_var.set(self.video_file.stem)
            self.log(f"✓ Video selected: {self.video_file.name}", "SUCCESS")

    def browse_thumbnail(self):
        """Browse for thumbnail image"""
        filename = filedialog.askopenfilename(
            title="Select Thumbnail",
            filetypes=[("Images", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )
        if filename:
            self.thumbnail_var.set(filename)
            self.log(f"✓ Thumbnail selected: {Path(filename).name}", "SUCCESS")

    def generate_translations(self):
        """Generate multi-language SRT files"""
        original_srt = self.original_srt_var.get()
        if not original_srt or not Path(original_srt).exists():
            messagebox.showerror("Error", "Please select an original SRT file!")
            return

        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter your OpenAI API Key!")
            return

        # Get selected languages
        selected_langs = [code for code, var in self.language_vars.items() if var.get()]
        if not selected_langs:
            messagebox.showerror("Error", "Please select at least one target language!")
            return

        self.log(f"🌍 Translating SRT to {len(selected_langs)} languages...", "INFO")

        # Run in thread
        thread = threading.Thread(
            target=self._translate_worker,
            args=(original_srt, selected_langs, api_key),
            daemon=True
        )
        thread.start()

    def _translate_worker(self, srt_path, target_langs, api_key):
        """Worker thread for translation"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # Read original SRT
            with open(srt_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            self.log(f"📖 Read original SRT ({len(srt_content)} chars)", "INFO")

            # Translate to each language
            for lang_code in target_langs:
                self.log(f"🔄 Translating to {lang_code}...", "INFO")

                try:
                    # Use GPT to translate
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": f"Translate the following SRT subtitle file to {lang_code}. Keep the same timestamps and format. Only translate the text, not the numbers or timestamps."},
                            {"role": "user", "content": srt_content}
                        ]
                    )

                    translated = response.choices[0].message.content

                    # Save translated SRT
                    output_path = Path(srt_path).with_stem(f"{Path(srt_path).stem}_{lang_code}")
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(translated)

                    self.srt_files[lang_code] = str(output_path)
                    self.log(f"✅ {lang_code}: {output_path.name}", "SUCCESS")

                    # Update listbox
                    self.srt_listbox.insert(tk.END, f"{lang_code}: {output_path.name}")

                except Exception as e:
                    self.log(f"❌ Failed to translate {lang_code}: {e}", "ERROR")

            self.log("🎉 All translations complete!", "SUCCESS")
            messagebox.showinfo("Success!", f"Generated {len(self.srt_files)} translated SRT files!")

        except Exception as e:
            self.log(f"❌ Translation error: {e}", "ERROR")
            messagebox.showerror("Error", f"Translation failed:\n{e}")

    def authenticate_youtube(self):
        """Authenticate with YouTube"""
        self.log("🔐 YouTube authentication...", "INFO")
        messagebox.showinfo("YouTube Auth",
            "YouTube API authentication requires:\n\n" +
            "1. Google Cloud Project with YouTube Data API v3 enabled\n" +
            "2. OAuth 2.0 credentials (client_secret.json)\n" +
            "3. First-time browser authorization\n\n" +
            "This feature will be implemented in the full version.\n" +
            "For now, you can use the SRT translation feature!")

    def upload_to_youtube(self):
        """Upload video to YouTube"""
        if not self.video_file or not self.video_file.exists():
            messagebox.showerror("Error", "Please select a video file!")
            return

        self.log("📺 YouTube upload...", "INFO")
        messagebox.showinfo("YouTube Upload",
            "YouTube upload feature will be implemented in the full version.\n\n" +
            "You can manually upload to YouTube and add the generated SRT files:\n" +
            "1. Upload your video to YouTube Studio\n" +
            "2. Go to Subtitles section\n" +
            "3. Upload each SRT file for its language\n\n" +
            "The SRT files are ready to use!")


def main():
    root = tk.Tk()
    app = YouTubeUploader(root)
    root.mainloop()


if __name__ == '__main__':
    main()
