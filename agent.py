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
import sys
import json
import time
import random
import datetime
import subprocess
import urllib.parse
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

    models = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-1.5-pro"]
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
            "headline": "श्री राधा कृष्ण दिव्य प्रेम रहस्य",
            "caption": "जय श्री राधा कृष्ण! प्रेम और भक्ति का पावन संदेश। 🙏✨ #RadhaKrishna #Bhakti #Vrindavan #Shorts #DailyDevotion",
            "segments": [
                {"text": "राधे-कृष्ण का प्रेम केवल आकर्षण नहीं, आत्मा का परमात्मा से मिलन है।", "visual_prompt": "Divine Radha and Krishna smiling together in Vrindavan blooming gardens, glowing golden light, 9:16 vertical 8k wallpaper", "query": "Radha Krishna divine"},
                {"text": "जब कन्हैया बांसुरी बजाते थे, तब सारा संसार मंत्रमुग्ध हो जाता था।", "visual_prompt": "Lord Krishna playing golden flute under kadamba tree near Yamuna river, peacock feathers glowing, ultra realistic", "query": "Lord Krishna playing flute"},
                {"text": "राधा रानी के बिना कृष्ण अधूरे हैं, और कृष्ण के बिना राधा का कोई अस्तित्व नहीं।", "visual_prompt": "Shri Radha Rani surrounded by blooming lotus and sacred Vrindavan deer, divine aura, heavenly lights", "query": "Radha Rani divine"},
                {"text": "सच्चा प्रेम त्याग और समर्पण सिखाता है, जहाँ कोई स्वार्थ नहीं होता।", "visual_prompt": "Sacred Vrindavan Yamuna river bank with glowing diyas floating in water, divine twilight atmosphere", "query": "Vrindavan Yamuna river diyas"},
                {"text": "गोपियों का भाव केवल यह था कि प्रभु सदा प्रसन्न रहें।", "visual_prompt": "Vrindavan Yamuna ghat during golden sunset, spiritual peaceful reflection, celestial glowing mist", "query": "Vrindavan ghat sunset"},
                {"text": "जो भी भक्त सच्चे मन से राधे-राधे जपता है, उसके सब कष्ट दूर हो जाते हैं।", "visual_prompt": "Glowing sacred symbol of Radha Krishna in cosmic divine radiance, lotus petals showering", "query": "Radha Krishna temple"},
                {"text": "कलयुग में केवल हरि नाम ही मनुष्य को भवसागर से पार उतार सकता है।", "visual_prompt": "Divine flute on velvet with peacock feather in holy temple altar, soft warm diya light", "query": "Krishna flute peacock feather"},
                {"text": "आज अपने जीवन में प्रेम और करुणा को स्थान दें, राधे-राधे बोलें!", "visual_prompt": "Sacred glowing footprints of Shri Radha Krishna adorned with fresh lotus flowers, celestial light rays", "query": "Radha Krishna lotus flowers"},
                {"text": "बोलो राधे-राधे! कमेंट में जय श्री कृष्ण ज़रूर लिखें और कृपा पाएं।", "visual_prompt": "Vrindavan holy temple with thousands of glowing diyas at twilight, cinematic divine beauty", "query": "Vrindavan temple diyas night"}
            ]
        },
        {
            "id": 2,
            "theme": "mystery",
            "voice": "hi-IN-MadhurNeural",
            "headline": "सतयुग और त्रेतायुग के अनसुलझे रहस्य",
            "caption": "प्रा प्राचीन सनातन विज्ञान और युगों के रहस्य! 🔱🚩 #AncientMysteries #TretaYug #SanatanDharma #VedicScience #Shorts",
            "segments": [
                {"text": "क्या आप जानते हैं कि सतयुग में मनुष्य की आयु एक लाख वर्ष मानी गई थी?", "visual_prompt": "Ancient Himalayan sages meditating in floating energy, golden age golden temples, 9:16 cinematic visual", "query": "ancient Himalayan yogi meditation"},
                {"text": "त्रेतायुग में भगवान श्री राम के काल में पुष्पक विमान जैसी तकनीक थी।", "visual_prompt": "Ancient Vedic vimana golden flying chariot hovering over Ayodhya golden palace, epic cinematic lighting", "query": "ancient vimana flying temple"},
                {"text": "वाल्मीकि रामायण में ऐसे अस्त्रों का वर्णन है जो आधुनिक मिसाइल से भी तीव्र थे।", "visual_prompt": "Glowing cosmic Brahmastra energy weapon releasing mystical light beams in sky, ancient epic visual", "query": "Brahmastra ancient weapon epic"},
                {"text": "ब्रह्मास्त्र, पाशुपतास्त्र और नारायणास्त्र, ध्वनि तरंगों और मंत्रों से संचालित होते थे।", "visual_prompt": "Ancient Vedic manuscripts with glowing golden Sanskrit inscriptions and celestial geometry", "query": "ancient Sanskrit manuscript"},
                {"text": "यह सनातन ज्ञान केवल कल्पना नहीं, बल्कि उच्चतर वैज्ञानिक चेतना का प्रमाण है।", "visual_prompt": "Mysterious ancient Vedic temple astronomical calendar wheel with glowing golden alignments, cinematic look", "query": "Konark Sun temple wheel astronomy"},
                {"text": "द्वारका नगरी के समुद्र में मिले अवशेष इस बात को आज भी प्रमाणित करते हैं।", "visual_prompt": "Submerged ancient stone pillars and palace gates of Dwarka city deep underwater with glowing fish", "query": "Dwarka submerged city underwater"},
                {"text": "ऋषि-मुनियों ने बिना दूरबीन के सौरमंडल और ग्रहों की सटीक दूरी माप ली थी।", "visual_prompt": "Ancient Indian astronomer yogi looking into glowing planetary orbits and stars in night sky", "query": "ancient Indian astronomy planets"},
                {"text": "हमारी प्राचीन धरोहर में छिपे इन रहस्यों को जानना हर भारतीय का कर्तव्य है।", "visual_prompt": "Epic Kailash temple carved from single giant mountain rock, mystical glowing sunrise", "query": "Kailash temple Ellora rock"},
                {"text": "सनातन के इस गौरवशाली इतिहास पर गर्व है तो कमेंट में 'हर हर महादेव' लिखें!", "visual_prompt": "Lord Shiva meditating in snow peaks of Himalayas with glowing trident, cosmic aura", "query": "Lord Shiva Himalayas meditating"}
            ]
        },
        {
            "id": 3,
            "theme": "humor",
            "voice": "hi-IN-MadhurNeural",
            "headline": "ज़िंदगी की मीठी बातें और हंसी का डोज़",
            "caption": "थोड़ा मुस्कुराइए! ज़िंदगी बहुत खूबसूरत है 😂❤️ #DesiHumor #ComedyShorts #LifeJokes #TrendingReels #Shorts",
            "segments": [
                {"text": "जिंदगी में दो चीजें कभी समझ नहीं आतीं—एक डॉक्टर की हैंडराइटिंग और दूसरा...", "visual_prompt": "Funny confused cartoon character scratching head looking at strange prescription paper, comedic style", "query": "funny confused cartoon face"},
                {"text": "कि सुबह 6 बजे अलार्म बजने पर 5 मिनट की नींद 5 घंटे जैसी सुखद क्यों लगती है!", "visual_prompt": "Comical cozy blanket alarm clock ringing loudly, funny sleepy expressions, bright fun lighting", "query": "funny alarm clock waking up cartoon"},
                {"text": "एक भाई ने पूछा—शादी के बाद सुकून कहाँ मिलता है? मैंने कहा—यादों में!", "visual_prompt": "Humorous husband washing huge pile of dishes looking dramatically towards sky, funny expression", "query": "funny married life comedy cartoon"},
                {"text": "वैसे प्यार में सबसे बड़ी ताक़त यह है कि इंसान बिना किसी वजह के मुस्कुराने लगता है।", "visual_prompt": "Cute romantic smiling cartoon couple walking in autumn park, golden warm sunshine, joyful vibe", "query": "cute romantic couple smiling sunset"},
                {"text": "और जब वही इंसान घर आता है, तो मम्मी पूछती हैं—फोन में देखकर क्यों हंस रहा है रे?", "visual_prompt": "Funny cartoon character laughing uncontrollably holding smartphone on couch, bright colorful style", "query": "funny laughing cartoon holding phone"},
                {"text": "दोस्तो, गुस्सा करने से सेहत खराब होती है, और हंसने से चेहरे पर रौनक आती है!", "visual_prompt": "Joyful cartoon characters laughing together over tea, cheerful colorful animation aesthetic", "query": "friends laughing tea party cartoon"},
                {"text": "इसलिए हर दिन थोड़ा वक्त खुद के लिए और अपनों की खुशी के लिए ज़रूर निकालें।", "visual_prompt": "Warm beautiful sunrise view with hot steaming cup of tea on scenic balcony, peaceful morning", "query": "morning cup of tea sunrise balcony"},
                {"text": "अगर आपके चेहरे पर थोड़ी सी भी मुस्कान आई हो, तो चैनल को सब्सक्राइब और शेयर ज़रूर करें!", "visual_prompt": "Bright sparkling emoji hearts and thumbs up floating in fun colorful cinematic background", "query": "emoji thumbs up celebration colorful"}
            ]
        }
    ]

def generate_scripts():
    prompt = f"""
Aaj ki taarikh: {TODAY.strftime('%d %B %Y')}.
Aapko 3 alag-alag vertical 9:16 videos ke liye high quality Hindi script banani hai.
Har video ki kul avadhi lagbhag 60 se 75 second honi chahiye.
Har video ko 9 se 12 chote segments me baanto (har segment 5-7 second ka, lagbhag 12-16 shabdon ka).

Video 1: Shri Radha Krishna Prema Bhakti (Divya leela, prem aur samarpan, bhavuk vichaar).
Video 2: Prachin Granth aur Satya Yug / Treta Yug ke Ankahe Rahasya (Vedic vigyan, vimana, astras, Dwarka, etc).
Video 3: Hasi-Mazak / Desi Chutkula / Zindagi ka Meetha Pyar (Muskurahat laane wali baatein).

Kripya dhyan dein: Kisi bhi segment me user ka chehra ya real photo nahi aayegi. Har segment ke liye thematic visual prompt banayein jo boli gayi line se 100% match kare.

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
          "visual_prompt": "English image prompt describing matching visual in 9:16 vertical ratio, 8k cinematic"
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

def generate_voiceover(text: str, voice: str, out_path: Path) -> float:
    try:
        # Use edge-tts command line directly
        cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(out_path)]
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
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

def fetch_image_pollinations(prompt: str, out_path: Path) -> bool:
    try:
        clean = urllib.parse.quote(prompt[:160])
        seed = random.randint(100, 999999)
        url = f"https://image.pollinations.ai/prompt/{clean}?width=720&height=1280&nologo=true&seed={seed}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=14)
        if r.status_code == 200 and len(r.content) > 10000:
            out_path.write_bytes(r.content)
            return True
    except Exception as e:
        print(f"[Pollinations Error] {e}")
    return False

def fetch_image_ddg(query: str, out_path: Path) -> bool:
    try:
        from duckduckgo_search import DDGS
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.images(keywords=query, max_results=5))
            for item in results:
                img_url = item.get("image")
                if img_url:
                    try:
                        r = requests.get(img_url, headers=headers, timeout=10)
                        if r.status_code == 200 and len(r.content) > 10000:
                            out_path.write_bytes(r.content)
                            return True
                    except Exception:
                        continue
    except Exception as e:
        print(f"[DDG Error] {e}")
    return False

def fetch_image_wikimedia(query: str, out_path: Path) -> bool:
    try:
        enc = urllib.parse.quote(query)
        url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={enc}&gsrnamespace=6&gsrlimit=3&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
        headers = {"User-Agent": "PunamRajAgent/2.0 (https://github.com/pkkuradiya1580-cloud; contact@punamraj.com)"}
        r = requests.get(url, headers=headers, timeout=12)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for _, page in pages.items():
                info = page.get("imageinfo", [])
                if info:
                    thumb = info[0].get("thumburl") or info[0].get("url")
                    if thumb:
                        ir = requests.get(thumb, headers=headers, timeout=15)
                        if ir.status_code == 200 and len(ir.content) > 10000:
                            out_path.write_bytes(ir.content)
                            return True
    except Exception as e:
        print(f"[Wikimedia Error] {e}")
    return False

def get_segment_image(prompt: str, query: str, theme: str, seg_idx: int, out_path: Path) -> Image.Image:
    # 1. First Priority: Fresh AI Cinematic Visual matching exact spoken line (Pollinations AI)
    print(f"    [Visual Gen] Attempting fresh AI visual: {prompt[:40]}...")
    if fetch_image_pollinations(prompt, out_path):
        try:
            return Image.open(out_path)
        except Exception:
            pass

    # 2. Second Priority: Fresh Web Visual via DuckDuckGo
    print(f"    [Visual Gen] Attempting web search for: {query}...")
    if fetch_image_ddg(query, out_path):
        try:
            return Image.open(out_path)
        except Exception:
            pass

    # 3. Third Priority: Wikimedia Commons HD
    if fetch_image_wikimedia(query, out_path):
        try:
            return Image.open(out_path)
        except Exception:
            pass

    # 4. 100% Guaranteed Curated Local HD Pack (No Blank Frames)
    theme_key = theme if theme in ("bhakti", "mystery", "humor") else "bhakti"
    curated_idx = (seg_idx % 3) + 1
    curated_file = ASSETS_DIR / f"{theme_key}_{curated_idx}.jpg"
    if curated_file.exists():
        try:
            print(f"    [Local Pack] Using curated HD visual: {curated_file.name}")
            return Image.open(curated_file)
        except Exception:
            pass

    # 5. Any asset in assets/images/
    if ASSETS_DIR.exists():
        assets = sorted(list(ASSETS_DIR.glob("*.jpg")))
        if assets:
            try:
                chosen = assets[seg_idx % len(assets)]
                print(f"    [Local Pack Fallback] Using: {chosen.name}")
                return Image.open(chosen)
            except Exception:
                pass

    return Image.new("RGB", (1080, 1920), (45, 25, 60))

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

def overlay_hindi_text(img: Image.Image, text: str, headline: str = "") -> Image.Image:
    W, H = 1080, 1920
    # Center-crop & fill 9:16 vertical canvas
    img = prepare_vertical_image(img).convert("RGBA")
    
    # Elegant cinematic vignette & subtitle badge overlay
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # 1. Top Header Banner Badge (Pill Style)
    if headline:
        head_font = get_font(42)
        head_w = int(draw_ov.textlength(headline, font=head_font))
        head_box_w = min(max(head_w + 70, 480), W - 80)
        hx1 = (W - head_box_w) // 2
        hy1, hy2 = 120, 210
        # Rounded glowing header badge
        draw_ov.rounded_rectangle([(hx1, hy1), (hx1 + head_box_w, hy2)], radius=28, fill=(10, 10, 20, 215), outline=(255, 215, 0, 240), width=3)
    
    # 2. Modern Viral Subtitles (Centered at Golden Reel Zone Y: 60-70%)
    sub_font = get_font(52)
    pad = 70
    lines = wrap_text(draw_ov, text, sub_font, W - (2 * pad) - 40)
    
    line_h = 72
    total_text_h = len(lines) * line_h
    pill_y1 = int(H * 0.62)
    pill_y2 = pill_y1 + total_text_h + 44
    
    # Translucent rounded glass capsule with gold edge
    draw_ov.rounded_rectangle(
        [(pad - 20, pill_y1 - 18), (W - pad + 20, pill_y2)],
        radius=26,
        fill=(12, 12, 22, 210),
        outline=(255, 220, 40, 230),
        width=3
    )
    
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    # Render Headline Text
    if headline:
        draw.text((W // 2, 165), headline, font=head_font, fill=(255, 225, 75), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    
    # Render Dynamic Two-Tone Subtitles
    cur_y = pill_y1 + 8
    for idx, line in enumerate(lines):
        # Alternate vibrant highlight: First line radiant white, subsequent lines punchy golden-yellow
        color = (255, 255, 255) if idx == 0 else (255, 230, 0)
        draw.text(
            (W // 2, cur_y),
            line,
            font=sub_font,
            fill=color,
            anchor="mt",
            stroke_width=4,
            stroke_fill=(0, 0, 0)
        )
        cur_y += line_h
        
    return img.convert("RGB")

def build_segment_video(img_path: Path, audio_path: Path, duration: float, out_mp4: Path, seg_idx: int = 0):
    fps = 30
    frames = max(int(duration * fps), 30)
    # Fast cinematic Ken Burns zoom-in and zoom-out
    if seg_idx % 2 == 0:
        # Smooth Zoom-In (1.0 -> 1.15)
        vf = (
            f"scale=1080:1920,"
            f"zoompan=z='min(zoom+0.001,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},"
            f"format=yuv420p"
        )
    else:
        # Smooth Zoom-Out (1.15 -> 1.0)
        vf = (
            f"scale=1080:1920,"
            f"zoompan=z='if(lte(zoom,1.0),1.15,max(1.001,zoom-0.001))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},"
            f"format=yuv420p"
        )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-i", str(audio_path),
        "-t", f"{duration:.2f}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(out_mp4)
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=35)
    except Exception:
        # Fast fallback to clean static 9:16 frame if zoompan hits issue
        simple_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(img_path),
            "-i", str(audio_path),
            "-t", f"{duration:.2f}",
            "-vf", "scale=1080:1920,format=yuv420p",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(out_mp4)
        ]
        subprocess.run(simple_cmd, check=True, capture_output=True, timeout=30)

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
    concat_list = temp_dir / f"concat_{final_output.stem}.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for seg in segment_videos:
            f.write(f"file '{seg.resolve().as_posix()}'\n")
            
    raw_merged = temp_dir / f"merged_{final_output.stem}.mp4"
    # Concatenate segments
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "copy", "-c:a", "aac", str(raw_merged)
    ]
    try:
        subprocess.run(cmd_concat, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"[FFmpeg Concat Warning] {e.stderr[:300] if e.stderr else 'error'}. Retrying with re-encode.")
        cmd_fallback = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
            str(raw_merged)
        ]
        subprocess.run(cmd_fallback, check=True, capture_output=True)
    
    if bgm_file and bgm_file.exists():
        # Mix background music at low volume (15%) with voiceover
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", str(raw_merged),
            "-stream_loop", "-1", "-i", str(bgm_file),
            "-filter_complex", "[1:a]volume=0.15[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            str(final_output)
        ]
        try:
            subprocess.run(cmd_mix, check=True, capture_output=True)
            return
        except Exception as e:
            print(f"[Warning] Failed to mix BGM: {e}. Keeping raw merged video.")
            
    # If no BGM or mix failed, copy directly
    if raw_merged != final_output:
        if final_output.exists():
            final_output.unlink()
        raw_merged.rename(final_output)

def ensure_fallback_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    seed_items = [
        ("bhakti_1.jpg", "Radha Krishna divine"),
        ("bhakti_2.jpg", "Lord Krishna flute"),
        ("bhakti_3.jpg", "Vrindavan temple"),
        ("mystery_1.jpg", "ancient temple India"),
        ("mystery_2.jpg", "Kailash temple"),
        ("mystery_3.jpg", "ancient Sanskrit manuscript"),
        ("humor_1.jpg", "funny cartoon"),
        ("humor_2.jpg", "happy couple smiling"),
        ("humor_3.jpg", "morning tea")
    ]
    for name, q in seed_items:
        file_path = ASSETS_DIR / name
        if not file_path.exists() or file_path.stat().st_size < 5000:
            fetch_image_wikimedia(q, file_path)

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
        
        print(f"\n==========================================")
        print(f"[GENERATING VIDEO {video_num}/3] {p['headline']} ({p['theme']})")
        print(f"==========================================")
        
        seg_videos = []
        for j, seg in enumerate(p["segments"]):
            seg_prefix = f"seg_{j+1:02d}"
            audio_path = video_work_dir / f"{seg_prefix}.mp3"
            img_raw_path = video_work_dir / f"{seg_prefix}_raw.jpg"
            img_final_path = video_work_dir / f"{seg_prefix}_final.png"
            seg_video_path = video_work_dir / f"{seg_prefix}.mp4"
            
            # 1. Voiceover
            voice = p.get("voice", "hi-IN-MadhurNeural")
            dur = generate_voiceover(seg["text"], voice, audio_path)
            
            # 2. Multi-tier Image Fetcher (Wikimedia HD + DuckDuckGo + Curated Local Pack)
            query = seg.get("query", seg["visual_prompt"][:50])
            img_loaded = get_segment_image(seg["visual_prompt"], query, p.get("theme", ""), j, img_raw_path)
            print(f"    [Photo OK] Segment {j+1} HD image taiyar!")
                    
            # 3. Add Hindi Text on Image
            processed_img = overlay_hindi_text(img_loaded, seg["text"], p["headline"])
            processed_img.save(img_final_path)
            
            # 4. Make video segment with cinematic alternating zoom
            build_segment_video(img_final_path, audio_path, dur, seg_video_path, seg_idx=j)
            seg_videos.append(seg_video_path)
            print(f"  ✓ Segment {j+1}/{len(p['segments'])} taiyar ({dur:.1f}s)")
            
        # 5. Assemble and Add BGM
        bgm = find_bgm_track(p.get("theme", ""))
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
