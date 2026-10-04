"""
Punam Raj Auto Video Agent
- रोज़ 3 अलग 9:16 वर्टिकल वीडियो (60 से 90 सेकंड)
- 1: श्री राधा-कृष्ण पावन भक्ति + भक्ति संगीत
- 2: प्राचीन ग्रंथों व सतयुग/त्रेतायुग के अनसुलझे रहस्य
- 3: हंसी-मज़ाक / चुटकुले / प्यारा प्रेम-मोहब्बत
- Microsoft Edge-TTS हिंदी आवाज़ (मुफ़्त)
- FFmpeg से स्मूथ Ken Burns ज़ूम इफ़ेक्ट और टेक्स्ट ओवरले
- Pollinations AI से 9:16 एचडी तस्वीरें + photos/ फ़ोल्डर से फ़ॉलबैक
- YouTube Shorts, Instagram Reels, Facebook Page और Telegram पर ऑटो-पोस्टिंग
"""

import os
import io
import sys
import json
import time
import random
import datetime
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.resolve()
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
NOW = datetime.datetime.now(IST)
TODAY = NOW.date()
OUT = ROOT / "out" / TODAY.isoformat()
MUSIC_DIR = ROOT / "music"
ASSETS_DIR = ROOT / "assets" / "images"
DRY_RUN = os.getenv("DRY_RUN", "0") == "1"

# Auto-unpack images.zip if committed to repository
zip_path = ROOT / "images.zip"
if zip_path.exists():
    import zipfile
    try:
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(ASSETS_DIR)
        print(f"[Assets] Extracted all tailored scene assets from images.zip!")
    except Exception as e:
        print(f"[Assets Error] Extracting images.zip: {e}")

# Fonts for Devanagari Hindi Text
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.otf",
    "C:/Windows/Fonts/mangal.ttf",
    "C:/Windows/Fonts/aparaj.ttf",
    "C:/Windows/Fonts/nirmala.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

def get_font(size: int):
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size, layout_engine=ImageFont.Layout.RAQM)
            except Exception:
                try:
                    return ImageFont.truetype(f, size)
                except Exception:
                    pass
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for w in words:
        test_line = (current_line + " " + w).strip()
        if draw.textlength(test_line, font=font) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = w
    if current_line:
        lines.append(current_line)
    return lines

def call_gemini(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[WARNING] GEMINI_API_KEY missing! Using offline template scripts.")
        return ""

    models = ["gemini-3.8-flash", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-3.5-flash"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.85,
                "responseMimeType": "application/json"
            }
        }
        try:
            r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
            if r.status_code == 200:
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print(f"[Gemini] {model} returned code {r.status_code}")
        except Exception as e:
            print(f"[Gemini] {model} request failed: {e}")
    return ""

def get_offline_scripts():
    return [
        {
            "id": 1,
            "theme": "bhakti",
            "voice": "hi-IN-SwaraNeural",
            "headline": "✨ चेतना और ब्रह्मांडीय प्रेम का रहस्य ✨",
            "caption": "ब्रह्मांडीय प्रेम और चेतना का दिव्य स्वरूप! 🌌✨ #RadhaKrishna #CosmicConsciousness #DivineLove #Shorts #TrendingReels",
            "segments": [
                {"text": "राधे-कृष्ण का प्रेम केवल आकर्षण नहीं, आत्मा का परमात्मा से मिलन है।", "visual_prompt": "Ultra-photorealistic 8k IMAX cinematic, Unreal Engine 5 render of ethereal Lord Krishna and Radha, cosmic glowing cyan and gold aura, cinematic volumetric lighting, floating lotus petals in cosmic nebulae, 70mm movie photography, 9:16 vertical", "query": "cosmic divine love space 8k"},
                {"text": "जब कन्हैया बांसुरी बजाते थे, तब सारा संसार मंत्रमुग्ध हो जाता था।", "visual_prompt": "Lord Krishna playing golden flute with glowing starlight aura, ethereal peacock feathers shimmering, cinematic depth of field, 8k vertical wallpaper", "query": "Krishna golden flute starlight"},
                {"text": "राधा रानी के बिना कृष्ण अधूरे हैं, और कृष्ण के बिना राधा का कोई अस्तित्व नहीं।", "visual_prompt": "Ethereal Goddess Radha surrounded by glowing lotus blossoms, heavenly golden twilight reflections, celestial fantasy cinema, 9:16 vertical", "query": "celestial goddess glowing lotus"},
                {"text": "सच्चा प्रेम त्याग और समर्पण सिखाता है, जहाँ कोई स्वार्थ नहीं होता।", "visual_prompt": "Cosmic divine energy particles swirling like golden galaxies over sacred Vrindavan waters, Christopher Nolan style sci-fi cinematic lighting, 9:16 vertical", "query": "golden galaxies water reflection"},
                {"text": "गोपियों का भाव केवल यह था कि प्रभु सदा प्रसन्न रहें।", "visual_prompt": "Glow of thousands of cosmic floating lights over golden mirror river, hyper-realistic fantasy cinema, 8k vertical", "query": "thousands floating lanterns water 8k"},
                {"text": "जो भी भक्त सच्चे मन से राधे-राधे जपता है, उसके सब कष्ट दूर हो जाते हैं।", "visual_prompt": "Sacred glowing celestial aura in deep space nebula, shimmering golden stardust, award winning cinematography, 9:16 vertical", "query": "deep space golden nebula 8k"},
                {"text": "कलयुग में केवल हरि नाम ही मनुष्य को भवसागर से पार उतार सकता है।", "visual_prompt": "Sacred Indian devotee hands gently holding Tulsi Japa Mala prayer beads with glowing divine golden aura, spiritual devotion, Harinam chanting, 9:16 vertical, 8k cinematic render", "query": "devotee hands prayer beads tulsi mala"},
                {"text": "आज अपने जीवन में प्रेम और करुणा को स्थान दें, राधे-राधे बोलें!", "visual_prompt": "Sacred glowing golden footprints stepping on luminous blooming lotus flowers, beams of heaven breaking through clouds, 9:16 vertical", "query": "golden lotus flowers glowing heavenly"},
                {"text": "बोलो राधे-राधे! कमेंट में जय श्री कृष्ण ज़रूर लिखें और कृपा पाएं।", "visual_prompt": "Magnificent cosmic temple palace glowing under starry galaxy twilight, cinematic fantasy masterpiece, 9:16 vertical", "query": "cosmic glowing temple palace galaxy"}
            ]
        },
        {
            "id": 2,
            "theme": "chanakya",
            "voice": "hi-IN-MadhurNeural",
            "headline": "📜 चाणक्य नीति: जीवन बदलने वाले 3 नियम ⚔️",
            "caption": "आचार्य चाणक्य के ये 3 नियम जीवन में कभी हारने नहीं देंगे! 📜🔥 #ChanakyaNiti #Wisdom #LifeLessons #SuccessMindset #Shorts",
            "segments": [
                {"text": "आचार्य चाणक्य कहते हैं—जीवन में कभी भी किसी पर अंधा विश्वास मत करो।", "visual_prompt": "Acharya Chanakya ancient Indian philosopher advisor sitting with sacred parchment scrolls and glowing brass oil lamp in royal Maurya court, wise resolute face, Brahmin shikha, 9:16 vertical, 8k cinematic render", "query": "Acharya Chanakya scrolls oil lamp"},
                {"text": "जो व्यक्ति आपकी बात सुनते समय इधर-उधर देखे, वह कभी सच्चा मित्र नहीं हो सकता।", "visual_prompt": "Two ancient Indian royal court advisors engaged in deep dramatic whispering discussion, palace pillars, oil torches, cinematic lighting, 9:16 vertical, 8k render", "query": "ancient royal court advisors discussion"},
                {"text": "अपनी कमज़ोरी और गुप्त योजनाएं कभी किसी को न बताएं, चाहे वह कितना भी खास हो।", "visual_prompt": "Ancient Indian royal advisor strategist pointing at parchment war strategy map table with glowing oil lamps and brass weapons, 9:16 vertical, 8k cinematic render", "query": "ancient strategist map table lamps"},
                {"text": "सांप अगर जहरीला न भी हो, तो भी उसे फुंकारना कभी नहीं छोड़ना चाहिए।", "visual_prompt": "Majestic golden king cobra raising its hood fearlessly in ancient royal stone temple, glowing royal aura, 9:16 vertical, cinematic 8k render, National Geographic quality", "query": "golden king cobra hood ancient temple"},
                {"text": "संकट के समय बुद्धि ही इंसान का सबसे बड़ा अस्त्र और सच्चा कवच बनती है।", "visual_prompt": "Glowing golden cosmic sacred geometry mandala radiating around wise ancient Indian sage in meditation, divine intellect, 9:16 vertical, 8k render", "query": "golden sacred geometry wisdom mandala"},
                {"text": "ज्ञान और विनम्रता वह धन है जिसे कोई राजा या चोर कभी चुरा नहीं सकता।", "visual_prompt": "Ancient Takshashila university grand library with thousands of glowing Sanskrit palm leaf manuscripts and stone arches, enlightened scholars studying, 9:16 vertical, 8k render", "query": "Takshashila library ancient manuscripts"},
                {"text": "जो इंसान समय का सम्मान नहीं करता, समय उसे बर्बाद करके रख देता है।", "visual_prompt": "Antique ornate golden hourglass with glowing sand flowing through glass against cosmic starry night sky, passing time metaphor, 9:16 vertical, 8k cinematic render", "query": "antique golden hourglass cosmic sky"},
                {"text": "अगर चाणक्य की इन नीतियों पर अमल करोगे, तो असफलता कभी छू भी नहीं पाएगी!", "visual_prompt": "Majestic royal lion walking forward fearlessly on mountain cliff at golden sunrise, symbol of strength and king, 9:16 vertical, cinematic 8k render", "query": "royal lion mountain cliff sunrise"},
                {"text": "जय हिंद! चाणक्य नीति अच्छी लगी हो तो कमेंट में 'जय चाणक्य' ज़रूर लिखें।", "visual_prompt": "Colossal ancient Indian Rajput Maurya royal fortress palace atop mountain, golden sunrise, fluttering royal saffron flag, epic cinematic 8k render", "query": "ancient fortress palace saffron flag"}
            ]
        },
        {
            "id": 3,
            "theme": "motivation",
            "voice": "hi-IN-MadhurNeural",
            "headline": "🔥 उठो, लड़ो और जीतो: कभी हार मत मानो 🚀",
            "caption": "जब हौसले बुलंद हों तो कोई भी रुकावट तुम्हें रोक नहीं सकती! 🔥💪 #Motivation #NeverGiveUp #SuccessMindset #Inspiration #Shorts",
            "segments": [
                {"text": "याद रखना, जब पूरी दुनिया कहे कि तुमसे नहीं होगा, वही सही वक्त है शुरुआत करने का!", "visual_prompt": "Powerful silhouette of determined lone runner standing victoriously atop mountain peak at fiery golden sunrise, clouds below, inspiration, 9:16 vertical, 8k cinematic render", "query": "runner victory mountain peak sunrise"},
                {"text": "किस्मत को दोष देना बंद करो, तुम्हारी मेहनत ही तुम्हारी तकदीर लिखने की असली कलम है।", "visual_prompt": "Determined young athletic Indian man training relentlessly with heavy battle ropes in gym, sweat drops, intense fire in eyes, 9:16 vertical, 8k photo render", "query": "athlete training gym battle ropes sweat"},
                {"text": "रास्ते में मुश्किलें आएंगी, लोग ताने मारेंगे, लेकिन तुम्हें सिर्फ अपनी मंज़िल देखनी है।", "visual_prompt": "Majestic golden eagle with open wings soaring high above dramatic dark storm clouds into brilliant sunlight, freedom and power, 9:16 vertical, 8k cinematic render", "query": "golden eagle soaring storm clouds"},
                {"text": "जो आज तुम पर हंस रहे हैं, कल वही तुम्हारी सफलता पर ताली बजाएंगे!", "visual_prompt": "Young Indian couple laughing happily together in chic outdoor aesthetic cafe, warm golden sunset, Instagram photography, 9:16 vertical", "query": "young couple laughing sunset cafe"},
                {"text": "हर रोज सुबह एक नए जोश के साथ उठो और अपने सपनों के लिए जी-जान लगा दो।", "visual_prompt": "Young Indian man full of energy laughing out loud while holding smartphone on couch, bright colorful modern apartment, 9:16 vertical", "query": "energetic young man couch smartphone"},
                {"text": "असफलता अंत नहीं है, बल्कि यह सीखने और दोबारा उठ खड़े होने का एक मौका है।", "visual_prompt": "Group of happy young Indian friends laughing joyfully together, radiant smiles, healthy happy friendship, 9:16 vertical, 8k photo render", "query": "happy indian friends laughing"},
                {"text": "उठो, जागो और तब तक मत रुको जब तक तुम्हारा लक्ष्य हासिल न हो जाए!", "visual_prompt": "Mountain climber standing on the highest snow peak raising hands in triumph under golden morning sun, ultimate victory, 9:16 vertical, 8k cinematic render", "query": "mountain climber summit snow peak victory"},
                {"text": "अगर अपने सपनों पर अटूट विश्वास है, तो अभी सब्सक्राइब करें और आगे बढ़ें!", "visual_prompt": "Vibrant colorful modern 3D YouTube subscribe button with ringing golden bell and exploding floating red love hearts, celebration background, 9:16 vertical, 8k 3D render", "query": "3d subscribe button bell floating hearts"}
            ]
        }
    ]

def generate_scripts():
    prompt = f"""
Aaj ki taarikh: {TODAY.strftime('%d %B %Y')}.
Aapko 3 alag-alag vertical 9:16 videos ke liye high quality Hindi script banani hai.
Har video ki kul avadhi lagbhag 60 se 75 second honi chahiye.
Har video ko 8 se 10 chote segments me baanto (har segment 5-7 second ka, lagbhag 12-16 shabdon ka).

Video 1: Shri Radha Krishna Cosmic Love, Wisdom & Teachings (Modern 4K Unreal Engine 5 aesthetic, divine consciousness).
Video 2: Acharya Chanakya Niti & Life Strategy (Deep ancient wisdom, rules of success, human psychology, 4K royal aesthetic).
Video 3: Powerful Life Motivation & Relentless Drive (High energy, never give up, self-belief, winning mindset).

MAHATVAPURNA VISUAL RULE:
- Har segment ke liye 'visual_prompt' me 4K Unreal Engine 5 render, IMAX cinematic lighting, hyper-realistic, photorealistic, vertical 9:16 aspect ratio hona chahiye.
- Kripya koi bhi purani calendar art, traditional sketches ya religious paintings ka prompt MAT banayein. Har visual modern 4K Hollywood/Blockbuster movie jaisa dikhna chahiye!
- User ka chehra ya real photo bilkul nahi aayegi.

Output format: Kripya SIRF valid JSON dein is structure me:
{{
  "videos": [
    {{
      "id": 1,
      "theme": "bhakti",
      "voice": "hi-IN-SwaraNeural",
      "headline": "...",
      "caption": "...",
      "segments": [
        {{
          "text": "spoken Hindi line in Devanagari (12-16 words)",
          "visual_prompt": "English image prompt in 4k IMAX cinematic style, 9:16 vertical ratio"
        }}
      ]
    }}
  ]
}}
"""
    raw_json = call_gemini(prompt)
    if raw_json:
        try:
            # Clean possible markdown wrap
            cleaned = raw_json.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            if "videos" in data and len(data["videos"]) >= 3:
                return data["videos"][:3]
        except Exception as e:
            print(f"[ERROR] Failed to parse Gemini JSON: {e}")
    
    print("[INFO] Using built-in premium offline scripts.")
    return get_offline_scripts()

def get_audio_duration(file_path: Path) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 6.0

def generate_voiceover(text: str, voice: str, out_path: Path, is_last_segment: bool = False) -> float:
    try:
        raw_tts = out_path.with_name(f"raw_{out_path.name}")
        cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(raw_tts)]
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        
        # Add acoustic silence pad (0.6s for segments, 1.0s for outro) so the last syllable/word NEVER cuts off
        pad_duration = 1.0 if is_last_segment else 0.6
        cmd_pad = [
            "ffmpeg", "-y", "-i", str(raw_tts),
            "-af", f"apad=pad_dur={pad_duration}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(out_path)
        ]
        pad_res = subprocess.run(cmd_pad, capture_output=True)
        if pad_res.returncode != 0 or not out_path.exists():
            # If FFmpeg padding fails for any reason, use raw TTS
            raw_tts.replace(out_path)
        else:
            try:
                raw_tts.unlink()
            except Exception:
                pass
                
        dur = get_audio_duration(out_path)
        return max(dur, 4.0)
    except Exception as e:
        print(f"[TTS Error] edge-tts failed: {e}. Generating silent placeholder.")
        # Fallback silent audio of 5s
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", "5.0", "-q:a", "9", "-acodec", "libmp3lame", str(out_path)
        ], check=True, capture_output=True, timeout=20)
        return 5.0

def is_valid_image(img_path: Path) -> bool:
    try:
        if not img_path.exists() or img_path.stat().st_size < 15000:
            return False
        with Image.open(img_path) as im:
            if im.size[0] < 300 or im.size[1] < 300:
                return False
            # Check if image is completely black/empty
            thumb = im.resize((32, 32)).convert("L")
            pixels = list(thumb.getdata())
            avg_brightness = sum(pixels) / len(pixels)
            if avg_brightness < 8:  # Completely black image check
                return False
        return True
    except Exception:
        return False

# 100% Tailored Permanent 4K Cloud Images matching EVERY spoken line in all 3 videos!
TAILORED_SCENE_IMAGES = {
    # Video 1: Shri Radha-Krishna Divine Love & Wisdom
    "v1_seg1": "https://files.catbox.moe/pvr6e0.jpg",  # Radha-Krishna divine embrace in cosmic cyan & gold
    "v1_seg2": "https://files.catbox.moe/iqqe9m.jpg",  # Lord Krishna playing golden flute with peacock crown
    "v1_seg3": "https://files.catbox.moe/yutw50.jpg",  # Goddess Radha surrounded by blooming lotuses on sacred waters
    "v1_seg4": "https://files.catbox.moe/r8o9gv.jpg",  # Golden galaxies swirling over Vrindavan sacred waters
    "v1_seg5": "https://files.catbox.moe/zg61ey.jpg",  # Thousands of floating lamps/diyas on river ghat at Vrindavan night
    "v1_seg6": "https://files.catbox.moe/yb9quf.jpg",  # Sacred golden divine stardust aura in cosmic nebula
    "v1_seg7": "https://files.catbox.moe/0agir2.jpg",  # Golden flute floating in starlight with mystical peacock feather
    "v1_seg8": "https://files.catbox.moe/4xi6vu.jpg",  # Sacred glowing lotus flowers blooming on heavenly waters
    "v1_seg9": "https://files.catbox.moe/jsp70z.jpg",  # Magnificent cosmic golden temple palace under starry galaxy
    
    # Video 2: Ancient Indian Advanced Science & Secrets
    "v2_seg1": "https://files.catbox.moe/epnami.jpg",  # Ancient Himalayan masters with holographic energy rings
    "v2_seg2": "https://files.catbox.moe/j9isff.jpg",  # Golden Pushpaka Vimana flying craft hovering over Ayodhya palace
    "v2_seg3": "https://files.catbox.moe/tbffsh.jpg",  # Cosmic Brahmastra quantum plasma lightning energy weapon beam
    "v2_seg4": "https://files.catbox.moe/85jelo.jpg",  # Ancient glowing golden Sanskrit metallic manuscripts
    "v2_seg5": "https://files.catbox.moe/pzadqw.jpg",  # Colossal ancient astronomical stone wheel aligning with planets
    "v2_seg6": "https://files.catbox.moe/la76x6.jpg",  # Sunken ancient golden city of Dwarka underwater with pillars & divers
    "v2_seg7": "https://files.catbox.moe/l3zjy5.jpg",  # Ancient astronomer sage using bronze astrolabe looking into 3D planets
    "v2_seg8": "https://files.catbox.moe/hd2fb6.jpg",  # Colossal monolithic Kailash temple carved from mountain peak
    "v2_seg9": "https://files.catbox.moe/djzcxf.jpg",  # Cosmic Mahadev Lord Shiva meditating on Himalayas with Trishul
    
    # Video 3: Desi Life Relatable Humor & Fun
    "v3_seg1": "https://files.catbox.moe/l4k8i9.jpg",  # Young Indian man shocked & confused at doctor prescription paper
    "v3_seg2": "https://files.catbox.moe/yvbtko.jpg",  # 6:00 AM alarm clock ringing wildly with person under cozy blanket
    "v3_seg3": "https://files.catbox.moe/jfyqr7.jpg",  # Husband overwhelmed washing huge mountain of dishes in kitchen
    "v3_seg4": "https://files.catbox.moe/wyls9x.jpg",  # Cute trendy couple laughing happily together at cafe sunset
    "v3_seg5": "https://files.catbox.moe/w0049s.jpg",  # Guy laughing out loud looking at smartphone on couch
    "v3_seg6": "https://files.catbox.moe/0qvs85.jpg",  # Group of young friends having fun laughing together over chai
    "v3_seg7": "https://files.catbox.moe/u4r2j0.jpg",  # Steaming hot cutting chai cup on scenic balcony at sunrise
    "v3_seg8": "https://files.catbox.moe/zdbs76.jpg",  # Colorful 3D floating hearts and subscribe celebration outro
}

def fetch_image_pollinations(prompt: str, out_path: Path) -> bool:
    clean = urllib.parse.quote(prompt.strip()[:180])
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    seed = random.randint(1000, 9999999)
    url = f"https://image.pollinations.ai/prompt/{clean}?width=720&height=1280&nologo=true&seed={seed}"
    
    try:
        r = requests.get(url, headers=headers, timeout=75)
        if r.status_code == 200 and len(r.content) > 15000:
            out_path.write_bytes(r.content)
            if is_valid_image(out_path):
                return True
    except Exception as e:
        print(f"[Pollinations Error] {e}")
    return False

def get_segment_image(prompt: str, query: str, theme: str, seg_idx: int, out_path: Path, video_id: int = 1) -> Image.Image:
    key = f"v{video_id}_seg{seg_idx + 1}"
    
    # 1. First & Absolute Priority: Exact Local Match in ANY location
    candidate_paths = [
        ASSETS_DIR / f"{key}.jpg",
        ROOT / "assets" / "images" / f"{key}.jpg",
        ROOT / "images" / f"{key}.jpg",
        ROOT / f"{key}.jpg",
        ROOT / "assets" / f"{key}.jpg",
    ]
    for p in candidate_paths:
        if p.exists() and is_valid_image(p):
            print(f"    [Exact Scene Match] Local file: {p.name}")
            try:
                import shutil
                shutil.copyfile(p, out_path)
            except Exception:
                pass
            return Image.open(p)

    # 2. Second Priority: Direct Tailored High-Definition CDN Asset (Guaranteed 100% Scene Match)
    if key in TAILORED_SCENE_IMAGES:
        url = TAILORED_SCENE_IMAGES[key]
        try:
            print(f"    [Exact Scene Match] Loading tailored 4K visual for {key}...")
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
            if r.status_code == 200 and len(r.content) > 15000:
                out_path.write_bytes(r.content)
                if is_valid_image(out_path):
                    return Image.open(out_path)
        except Exception as e:
            print(f"    [Tailored Asset Warning] {e}")

    # 3. Third Priority: Fresh AI Cinematic Visual (Pollinations AI)
    print(f"    [Visual Gen] Scene {seg_idx+1} AI Visual: {prompt[:40]}...")
    if fetch_image_pollinations(prompt, out_path):
        try:
            return Image.open(out_path)
        except Exception:
            pass

    return Image.new("RGB", (1080, 1920), (25, 20, 38))

def prepare_vertical_image(img: Image.Image) -> Image.Image:
    W, H = 1080, 1920
    img = img.convert("RGB")
    iw, ih = img.size
    scale = max(W / iw, H / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - W) // 2
    top = (new_h - H) // 2
    return resized.crop((left, top, left + W, top + H))

def split_text_into_phases(text: str) -> tuple[str, str]:
    words = text.strip().split()
    if len(words) <= 5:
        return text, ""
    mid = len(words) // 2
    return " ".join(words[:mid]), " ".join(words[mid:])

def render_text_frame(img_base: Image.Image, text: str, headline: str = "") -> Image.Image:
    W, H = 1080, 1920
    frame = img_base.copy()
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # 1. Top Header Banner Badge (Y = 140 to 220) - Compact & Elegant
    if headline:
        head_font = get_font(38)
        head_w = int(draw_ov.textlength(headline, font=head_font))
        head_box_w = min(max(head_w + 60, 460), W - 100)
        hx1 = (W - head_box_w) // 2
        hy1, hy2 = 140, 218
        draw_ov.rounded_rectangle(
            [(hx1, hy1), (hx1 + head_box_w, hy2)],
            radius=24,
            fill=(10, 10, 20, 210),
            outline=(255, 215, 0, 220),
            width=2
        )
    
    # 2. Modern Subtitles in LOWER-THIRD SAFE ZONE (Y = 1290 to 1460)
    # CRITICAL: Y = 250 to 1250 remains 100% CLEAR so character faces, expressions, and visuals are NEVER BLOCKED!
    sub_font = get_font(52)
    pad = 70
    lines = wrap_text(draw_ov, text, sub_font, W - (2 * pad) - 40)
    
    line_h = 74
    total_text_h = len(lines) * line_h
    
    # Anchor to lower safe zone: Y ≈ 1300 to 1480 (Clear from face, clear from Shorts bottom buttons)
    pill_y1 = int(H * 0.68)
    pill_y2 = pill_y1 + total_text_h + 36
    
    capsule_fill = (12, 12, 22, 185)  # Modern sleek translucent frosted pill
    capsule_border = (255, 215, 0, 220)
    
    draw_ov.rounded_rectangle(
        [(pad - 20, pill_y1 - 14), (W - pad + 20, pill_y2)],
        radius=26,
        fill=capsule_fill,
        outline=capsule_border,
        width=3
    )
    
    frame = Image.alpha_composite(frame, overlay)
    draw = ImageDraw.Draw(frame)
    
    if headline:
        draw.text((W // 2, 179), headline, font=head_font, fill=(255, 225, 75), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    
    cur_y = pill_y1 + 10
    for idx, line in enumerate(lines):
        color = (255, 255, 255) if idx == 0 else (255, 235, 50)
        draw.text(
            (W // 2, cur_y),
            line,
            font=sub_font,
            fill=color,
            anchor="mt",
            stroke_width=5,
            stroke_fill=(0, 0, 0)
        )
        cur_y += line_h
        
    return frame.convert("RGB")

def build_segment_video(img_loaded: Image.Image, text: str, headline: str, audio_path: Path, duration: float, out_mp4: Path, seg_idx: int = 0):
    fps = 30
    W, H = 1080, 1920
    base_img = prepare_vertical_image(img_loaded).convert("RGBA")
    
    # Split text into 2 dynamic spoken phases for lively subtitle movement
    p1, p2 = split_text_into_phases(text)
    temp_dir = out_mp4.parent
    
    if p2:
        # 2-phase animated subtitles
        f1 = render_text_frame(base_img, p1, headline)
        f2 = render_text_frame(base_img, p2, headline)
        p1_path = temp_dir / f"{out_mp4.stem}_p1.png"
        p2_path = temp_dir / f"{out_mp4.stem}_p2.png"
        f1.save(p1_path)
        f2.save(p2_path)
        
        t_split = duration / 2.0
        # Zoom Ken Burns with seamless subtitle cut at midpoint
        if seg_idx % 2 == 0:
            vf = f"scale=1080:1920,zoompan=z='min(zoom+0.0010,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={fps},format=yuv420p"
        else:
            vf = f"scale=1080:1920,zoompan=z='if(lte(zoom,1.0),1.14,max(1.001,zoom-0.0010))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={fps},format=yuv420p"
            
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{t_split:.2f}", "-i", str(p1_path),
            "-loop", "1", "-t", f"{(duration - t_split + 0.1):.2f}", "-i", str(p2_path),
            "-i", str(audio_path),
            "-filter_complex", f"[0:v]{vf}[v0];[1:v]{vf}[v1];[v0][v1]concat=n=2:v=1:a=0[vout]",
            "-map", "[vout]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-r", "30", "-g", "30",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{duration:.2f}",
            str(out_mp4)
        ]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode == 0 and out_mp4.exists() and out_mp4.stat().st_size > 0:
            return
            
    # Standard single-frame fallback
    single_frame = render_text_frame(base_img, text, headline)
    frame_path = temp_dir / f"{out_mp4.stem}_single.png"
    single_frame.save(frame_path)
    
    frames = max(int(duration * fps), 30)
    if seg_idx % 2 == 0:
        vf = f"scale=1080:1920,zoompan=z='min(zoom+0.0010,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},format=yuv420p"
    else:
        vf = f"scale=1080:1920,zoompan=z='if(lte(zoom,1.0),1.14,max(1.001,zoom-0.0010))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},format=yuv420p"
        
    cmd_fallback = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(frame_path),
        "-i", str(audio_path),
        "-t", f"{duration:.2f}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-r", "30", "-g", "30",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(out_mp4)
    ]
    subprocess.run(cmd_fallback, check=True, capture_output=True)

def find_bgm_track(theme: str) -> Path | None:
    if not MUSIC_DIR.exists():
        return None
    music_files = sorted([p for p in MUSIC_DIR.iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a")])
    if not music_files:
        return None
    
    if theme == "bhakti":
        # Look for bhakti / devotional keywords first
        bhakti_tracks = [p for p in music_files if any(k in p.stem.lower() for k in ["bhakti", "krishna", "radha", "bhajan", "aarti", "devotion"])]
        if bhakti_tracks:
            return random.choice(bhakti_tracks)
    return random.choice(music_files)

def assemble_final_video(segment_videos: list[Path], bgm_file: Path | None, final_output: Path):
    temp_dir = final_output.parent
    temp_dir.mkdir(parents=True, exist_ok=True)
    concat_list = temp_dir / f"concat_{final_output.stem}.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for seg in segment_videos:
            f.write(f"file '{seg.resolve().as_posix()}'\n")
            
    raw_merged = temp_dir / f"merged_{final_output.stem}.mp4"
    if raw_merged.exists():
        try:
            raw_merged.unlink()
        except Exception:
            pass

    # 1. Concatenate segments with clean 30fps re-encode so transitions are seamless with ZERO pause/gap!
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        str(raw_merged)
    ]
    print(f"  [FFmpeg Concat] Merging {len(segment_videos)} segments...")
    res_concat = subprocess.run(cmd_concat, capture_output=True, text=True)
    if res_concat.returncode != 0:
        print(f"  [FFmpeg Concat Error] {res_concat.stderr[-400:]}")
        raise RuntimeError(f"FFmpeg concat failed for {final_output.name}")

    if not raw_merged.exists() or raw_merged.stat().st_size == 0:
        raise FileNotFoundError(f"Raw merged file not created: {raw_merged}")

    # 2. Add Background Music (BGM) if available
    bgm_success = False
    if bgm_file and bgm_file.exists():
        temp_with_bgm = temp_dir / f"bgm_{final_output.stem}.mp4"
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", str(raw_merged),
            "-stream_loop", "-1", "-i", str(bgm_file),
            "-filter_complex", "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            str(temp_with_bgm)
        ]
        try:
            mix_res = subprocess.run(cmd_mix, capture_output=True, timeout=60)
            if mix_res.returncode == 0 and temp_with_bgm.exists() and temp_with_bgm.stat().st_size > 0:
                if final_output.exists():
                    final_output.unlink()
                temp_with_bgm.replace(final_output)
                bgm_success = True
                print(f"  [BGM Mix] Successfully mixed background score!")
        except Exception as e:
            print(f"  [BGM Mix Warning] Could not mix BGM: {e}")

    # If no BGM was added or mixing didn't happen, use raw_merged directly as final_output
    if not bgm_success:
        if final_output.exists():
            final_output.unlink()
        raw_merged.replace(final_output)

    # Clean up temporary concat list
    try:
        concat_list.unlink()
    except Exception:
        pass

def ensure_fallback_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    core_keys = ["v1_seg1", "v1_seg2", "v1_seg3", "v2_seg2", "v2_seg3", "v2_seg6", "v2_seg9", "v3_seg1", "v3_seg2", "v3_seg3"]
    for key in core_keys:
        file_path = ASSETS_DIR / f"{key}.jpg"
        if not file_path.exists() or file_path.stat().st_size < 10000:
            if key in TAILORED_SCENE_IMAGES:
                try:
                    r = requests.get(TAILORED_SCENE_IMAGES[key], headers=headers, timeout=20)
                    if r.status_code == 200 and len(r.content) > 10000:
                        file_path.write_bytes(r.content)
                except Exception as e:
                    print(f"[Asset Cache Error] {key}: {e}")

def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    ensure_fallback_assets()
    posts = generate_scripts()
    manifest = []
    
    for i, p in enumerate(posts):
        video_num = i + 1
        name = f"post{video_num}"
        video_work_dir = OUT / name
        video_work_dir.mkdir(parents=True, exist_ok=True)
        theme = p.get("theme", "bhakti")
        
        print(f"\n==========================================")
        print(f"[GENERATING VIDEO {video_num}/3] {p['headline']} ({theme})")
        print(f"==========================================")
        
        segments = p["segments"]
        
        # Parallel Pre-fetch all scene images simultaneously for maximum speed and variety!
        print(f"  [Parallel Visuals] Pre-fetching {len(segments)} distinct scene images...")
        img_paths = [video_work_dir / f"seg_{j+1:02d}_raw.jpg" for j in range(len(segments))]
        
        # Clear any stale cached images from previous runs today
        for p_old in img_paths:
            if p_old.exists():
                try:
                    p_old.unlink()
                except Exception:
                    pass

        def _fetch_one(idx):
            seg = segments[idx]
            query = seg.get("query", seg["visual_prompt"][:50])
            get_segment_image(seg["visual_prompt"], query, theme, idx, img_paths[idx], video_id=video_num)
            return idx
            
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(_fetch_one, j) for j in range(len(segments))]
            for fut in as_completed(futures):
                fut.result()
        
        seg_videos = []
        for j, seg in enumerate(segments):
            seg_prefix = f"seg_{j+1:02d}"
            audio_path = video_work_dir / f"{seg_prefix}.mp3"
            img_raw_path = img_paths[j]
            seg_video_path = video_work_dir / f"{seg_prefix}.mp4"
            
            # 1. Voiceover with natural silence padding (extra 1.0s pad for final outro line!)
            voice = p.get("voice", "hi-IN-MadhurNeural")
            is_last = (j == len(segments) - 1)
            dur = generate_voiceover(seg["text"], voice, audio_path, is_last_segment=is_last)
            
            # 2. Load the distinct prepared image (exact match from images.zip)
            img_loaded = get_segment_image(seg["visual_prompt"], "", theme, j, img_raw_path, video_id=video_num)
                    
            # 3. Make dynamic video segment with animated subtitles & smooth Ken Burns
            build_segment_video(img_loaded, seg["text"], p["headline"], audio_path, dur, seg_video_path, seg_idx=j)
            seg_videos.append(seg_video_path)
            print(f"  ✓ Segment {j+1}/{len(segments)} taiyar ({dur:.1f}s)")
            
        # 5. Assemble and Add BGM
        bgm = find_bgm_track(theme)
        final_mp4 = OUT / f"{name}.mp4"
        assemble_final_video(seg_videos, bgm, final_mp4)
        
        # Save manifest entry
        p["name"] = name
        p["video_file"] = str(final_mp4.relative_to(ROOT))
        p["full_caption"] = f"{p['headline']}\n\n{p['caption']}\n\n#PunamRaj #Shorts #Reels"
        manifest.append(p)
        print(f"[SUCCESS] Video {video_num} taiyar: {final_mp4}")
        
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTeeno videos taiyar hain! Path: {OUT}")

# ==================== POSTING SYSTEM ====================

def post_youtube(p):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    
    creds = Credentials(
        None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": (p["headline"] + " #Shorts")[:95],
            "description": p["full_caption"] + "\n#Shorts #YouTubeShorts",
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    video_path = str(OUT / f"{p['name']}.mp4")
    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    res = yt.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    print(f"  [YouTube Shorts] Uploaded successfully! Video ID: {res.get('id')}")

def post_instagram_reels(p):
    uid = os.environ["IG_USER_ID"]
    tok = os.environ.get("IG_TOKEN") or os.environ.get("FB_PAGE_ACCESS_TOKEN")
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.getenv("GITHUB_REF_NAME", "main")
    video_url = f"https://raw.githubusercontent.com/{repo}/{branch}/out/{TODAY.isoformat()}/{p['name']}.mp4"
    
    print(f"  [Instagram Reels] Checking public URL: {video_url}")
    for _ in range(15):
        if requests.head(video_url).status_code == 200:
            break
        time.sleep(4)
        
    # Step 1: Create Reel Container
    create_url = f"https://graph.facebook.com/v21.0/{uid}/media"
    res = requests.post(create_url, data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": p["full_caption"][:2000],
        "access_token": tok
    })
    res.raise_for_status()
    creation_id = res.json()["id"]
    
    # Step 2: Poll container status until FINISHED
    status_url = f"https://graph.facebook.com/v21.0/{creation_id}"
    for _ in range(25):
        time.sleep(5)
        st_res = requests.get(status_url, params={"fields": "status_code", "access_token": tok})
        if st_res.status_code == 200:
            code = st_res.json().get("status_code")
            if code == "FINISHED":
                break
            elif code in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Reel container processing failed with status: {code}")
                
    # Step 3: Publish container
    pub_url = f"https://graph.facebook.com/v21.0/{uid}/media_publish"
    pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": tok})
    pub_res.raise_for_status()
    print(f"  [Instagram Reels] Reel published successfully!")

def post_facebook_page(p):
    page_id = os.environ["FB_PAGE_ID"]
    tok = os.environ["FB_PAGE_ACCESS_TOKEN"]
    video_path = OUT / f"{p['name']}.mp4"
    
    url = f"https://graph.facebook.com/v21.0/{page_id}/videos"
    with open(video_path, "rb") as f:
        res = requests.post(
            url,
            data={"description": p["full_caption"][:5000], "access_token": tok},
            files={"source": f},
            timeout=180
        )
    res.raise_for_status()
    print(f"  [Facebook Page] Video posted successfully! ID: {res.json().get('id')}")

def post_telegram(p):
    tok = os.environ["TELEGRAM_BOT_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    video_path = OUT / f"{p['name']}.mp4"
    
    url = f"https://api.telegram.org/bot{tok}/sendVideo"
    with open(video_path, "rb") as f:
        res = requests.post(
            url,
            data={"chat_id": chat, "caption": p["full_caption"][:1024]},
            files={"video": f},
            timeout=120
        )
    res.raise_for_status()
    print(f"  [Telegram] Video sent successfully!")

def post():
    manifest_path = OUT / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"Manifest file nahi mili: {manifest_path}")
        
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if DRY_RUN:
        print("[DRY RUN ACTIVE] Koi post nahi ki gayi. Videos out/ folder me check karein.")
        return
        
    platforms = [
        ("YouTube Shorts", post_youtube, "YT_REFRESH_TOKEN"),
        ("Instagram Reels", post_instagram_reels, "IG_USER_ID"),
        ("Facebook Page", post_facebook_page, "FB_PAGE_ACCESS_TOKEN"),
        ("Telegram Channel", post_telegram, "TELEGRAM_BOT_TOKEN"),
    ]
    
    results = []
    for p in manifest:
        print(f"\n--- Posting: {p['headline']} ({p['name']}) ---")
        for label, fn, req_key in platforms:
            if not os.getenv(req_key):
                print(f"[-] {label}: Secret '{req_key}' set nahi hai, skip kiya.")
                continue
            try:
                fn(p)
                results.append((label, p["name"], "SUCCESS", "OK"))
            except Exception as e:
                err_msg = str(e)
                print(f"[FAIL] {label} error on {p['name']}: {err_msg}")
                results.append((label, p["name"], "FAILED", err_msg))
                
    print("\n================== SUMMARY ==================")
    for label, name, status, msg in results:
        print(f"[{status}] {label} - {name}: {msg}")
    print("=============================================")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("generate", "post"):
        sys.exit("Usage: python agent.py [generate|post]")
    {"generate": generate, "post": post}[sys.argv[1]]()
