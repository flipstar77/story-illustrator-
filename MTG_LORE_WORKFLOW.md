# Magic: The Gathering Lore Video Workflow
## For "The Dreaming Multiverse" YouTube Channel

### Channel Style Guide
- **Tone**: Calm, immersive, sleep-friendly (like bedtime stories)
- **Length**: 15,000+ words OR 2-3 hour narration
- **Pacing**: Slow, steady, no abrupt shifts
- **Reference**: "The Rise of the Thran" sample (tone only, never copy content)

---

## Complete Workflow (Story Illustrator V3)

### STEP 1: Research & Script Writing

**Research Requirements (BEFORE writing):**
- Perform 9+ cross-references minimum
- Use official sources:
  - MTG Wiki: https://mtg.fandom.com/wiki/
  - Wizards Story Archive: https://magic.wizards.com/en/story
  - Official novels, set stories, character bios
- Secondary sources only for speculation (label clearly)

**Script Guidelines:**
1. **Canon Only**: Factual information from official sources
2. **Label Speculation**: Use "This could imply..." or "Based on what we know..."
3. **Comprehensive Coverage**:
   - Characters
   - Planes
   - Factions
   - Items, artifacts, spells
   - Historical events
   - Lore connections
4. **Structure**: Chronological or thematic
5. **No Repetition**: Vary language, add new perspectives
6. **Soft Transitions**: Connect sections smoothly
7. **Avoid Clichés**: No "It wasn't THIS, it was THAT" or "tapestry of fate"
8. **Numbers**: Spelled out or digits, never Roman numerals
9. **Tone**: Conversational, immersive, atmospheric
10. **Ending**: Soft outro + call-to-action

**Required Deliverables:**
- [ ] 15,000+ word script
- [ ] Mispronunciation list (e.g., Yawgmoth = YAWG-moth)
- [ ] YouTube title (<100 chars): "Magic The Gathering Lore To Sleep To | [Topic]"
- [ ] SEO description with 3 hashtags (#MTGLore #SleepStory #FantasyASMR)
- [ ] 7-12 video tags (comma-separated)
- [ ] Playlist title and description
- [ ] Music direction prompt (65 BPM, ambient fantasy, no percussion)

**Example Music Prompt:**
```
Soft ambient fantasy score, 65 BPM, gentle drones and pads, faint mechanical hums
of ancient magic, ethereal and soothing, no percussion. Inspired by Oblivion OST
and Brian Eno's An Ending (Ascent). Designed to loop under calm narration.
```

---

### STEP 2: Prepare for Story Illustrator

1. **Save script** as `projects/mtg_[topic_name]/story.txt`
2. **Create sections** (use Phase 1 chunking):
   - API Mode: Automatic chunking via GPT-4o-mini
   - Manual Mode: Copy ChatGPT chunking prompt
   - Aim for 20-30 sections for 2-3 hour video

---

### STEP 3: Generate Images (Phase 2)

**Option A: ComfyUI + SDXL (Local)**
- Use MTG-themed prompts
- Style: Dark fantasy, ethereal, atmospheric
- Resolution: 1920x1080 (16:9) for YouTube
- Example prompts:
  - "Ancient Thran cityscape, glowing blue artifice, dark fantasy, cinematic"
  - "Yawgmoth's vat complex, bio-mechanical horror, ethereal atmosphere"
  - "Dominarian landscape at twilight, soft magical glow, serene"

**Option B: Browser Automation (Legacy)**
- Use ChatGPT DALL-E for image generation
- Same prompt style as above

---

### STEP 4: Generate Narration (Phase 3 - TTS)

**Voice Settings:**
- **Preset**: `calm` or `documentary`
- **Exaggeration**: 0.3 (very calm, no drama)
- **Temperature**: 0.5 (consistent, predictable)
- **Speed**: Slow (0.9x playback if too fast)

**TTS Process:**
1. Run Story Illustrator V3
2. Navigate to Phase 3
3. Select "Generate Narration"
4. Choose voice preset: **calm** or **documentary**
5. Generate audio for all sections
6. Combine into single narration file

---

### STEP 5: Video Assembly (Phase 3 - FFmpeg)

**Video Settings:**
- **Duration per image**: 10-15 seconds (longer for sleep content)
- **Transition**: Crossfade (1-2 seconds, very smooth)
- **Resolution**: 1920x1080 (1080p)
- **FPS**: 24 (cinematic, not 60fps gaming)
- **Background Music**: Your ambient fantasy track (65 BPM)
- **Music Volume**: -25dB to -30dB (very quiet under narration)

**Process:**
1. Add background music (loop if needed)
2. Mix narration + music
3. Sync images with narration timing
4. Add crossfade transitions
5. Render final video

---

### STEP 6: Subtitles (Phase 4)

**SRT Generation:**
1. Generate English SRT from narration audio (Whisper API)
2. Translate to 9 languages (optional for accessibility):
   - Spanish, French, German, Portuguese, Italian
   - Japanese, Korean, Russian, Chinese

**Upload to YouTube:**
- Primary: English (auto-generated or manual)
- Additional: Spanish, French, Portuguese for broader reach

---

### STEP 7: YouTube Upload

**Title Format:**
```
Magic The Gathering Lore To Sleep To | The Rise of the Thran
```

**Description Template:**
```
Magic The Gathering Lore | [Topic Name] | Sleep-Friendly Fantasy Storytelling

Drift off to the ancient lore of Magic: The Gathering as we explore [topic].
This calm, immersive narration blends soft ambient music with detailed storytelling,
perfect for relaxation, study, or bedtime listening.

[2-3 sentence summary of the topic]

🎵 Music: [Music Direction Prompt]
📖 Lore Sources: MTG Wiki, Wizards of the Coast Story Archive

If you enjoyed this journey through the Multiverse, consider subscribing for more
tales from Magic: The Gathering's rich history.

#MTGLore #SleepStory #FantasyASMR

Tags: magic the gathering lore, mtg story, fantasy sleep story, thran lore,
phyrexia story, sleep narration, asmr storytelling, mtg history, dominaria lore,
calm fantasy, bedtime story, magic lore explained
```

**Playlist:**
```
Title: Magic The Gathering Lore To Sleep To – The Thran & Phyrexia Saga

Description: A calm storytelling journey through the ancient history of Magic:
The Gathering — from the Thran Empire to the rise of Phyrexia. Each episode
blends soft narration and ambient soundscapes for relaxation, study, or sleep.
```

---

## Quick Command Reference

### Generate MTG Lore Video
```bash
# 1. Create project (manual or API mode)
python story_illustrator_v3.py

# 2. Phase 1: Chunk your 15,000 word script
#    Use API mode with GPT-4o-mini for automatic chunking

# 3. Phase 2: Generate images (ComfyUI or browser automation)

# 4. Phase 3: Generate narration + video
#    Voice: calm (exaggeration=0.3, temperature=0.5)
#    Image duration: 10-15 seconds
#    Transition: crossfade 2s
#    Music: -28dB

# 5. Phase 4: Generate multilingual SRTs (optional)

# 6. Upload to YouTube using youtube_uploader.py
```

---

## Mispronunciation List Template

Create this list for EVERY script to ensure TTS accuracy:

```
Yawgmoth = YAWG-moth
Phyrexia = fuh-REK-see-uh
Dominaria = dah-mih-NAH-ree-uh
Urza = UR-zuh
Mishra = MISH-ruh
Glacian = GLAY-shun
Rebbec = REB-eck
Thran = THRAN (like "ران" in Farsi)
Halcyon = HAL-see-on
Koilos = KOY-lohs
Gix = GIKS
Powerstone = POW-er-stone
Artifice = AR-tih-fiss
Mana = MAH-nuh (not MAN-uh)
Planeswalker = PLAYNZ-waw-ker
```

**TTS Replacement Strategy:**
If TTS mispronounces a term repeatedly, consider:
1. Phonetic spelling in script: "Yawgmoth (YAWG-moth)"
2. Using simpler synonyms: "the dark god" instead of "Yawgmoth"
3. Post-processing: Re-record specific words and splice in

---

## Quality Checklist (Before Upload)

- [ ] Script is 15,000+ words
- [ ] All lore is canon (verified against official sources)
- [ ] Speculation is clearly labeled
- [ ] 9+ cross-references performed
- [ ] Mispronunciation list created
- [ ] Pacing is slow and sleep-friendly
- [ ] No abrupt tone shifts
- [ ] Transitions are smooth
- [ ] Background music is 65 BPM, ambient, no percussion
- [ ] Music volume is -25 to -30dB (very quiet)
- [ ] Video is 2-3 hours long
- [ ] YouTube title is <100 characters
- [ ] Description has SEO keywords + 3 hashtags
- [ ] 7-12 tags included
- [ ] Playlist title and description ready
- [ ] Soft outro + call-to-action included

---

## Pro Tips

1. **Voice Cloning**: Record 10-15 seconds of your own calm narration voice,
   use it with Chatterbox TTS for a personalized channel voice

2. **Batch Production**: Write 3-5 scripts in advance, generate videos in batches

3. **Playlist Series**: Group related topics (e.g., "The Thran Saga", "Phyrexian Arc")

4. **Thumbnail Template**: Create consistent thumbnail style with MTG artwork +
   "LORE TO SLEEP TO" overlay

5. **Upload Schedule**: Post 1-2 videos per week for consistent growth

6. **Community**: Pin comments asking for next lore topic requests

---

## Example Topics for The Dreaming Multiverse

- The Rise of the Thran
- The Brothers' War (Urza vs Mishra)
- The Phyrexian Invasion
- The Weatherlight Saga
- The Mending and the Planeswalker Spark
- Nicol Bolas: The Elder Dragon
- The Gatewatch Formation
- Innistrad: The Gothic Plane
- Ravnica: The Ten Guilds
- Zendikar: The Roil and the Eldrazi
- Mirrodin/New Phyrexia Transformation
- Kamigawa: Ancient vs Neon Dynasty

Each topic = 1 video = 15,000+ words = 2-3 hours narration

---

**This workflow turns your deep MTG research into professional, sleep-friendly
YouTube content using the Story Illustrator V3 pipeline.**
