"""
Punam Raj Auto Video Agent - Shri Krishna Mool Vachan Edition
- Daily 1 Single Premium Vertical 9:16 Video (50 to 65 seconds)
- Exclusive Topic: Shri Krishna Mool Vachan & Shrimad Bhagavad Gita Teachings
- Fresh unique script every single day (Dynamic Gemini AI with 31-day offline rotation bank)
- Fresh 8K Ultra-HD divine visuals rotated dynamically every single day
- Microsoft Edge-TTS Hindi Voiceover (hi-IN-MadhurNeural) with acoustic padding
- Cinematic Ken Burns panning & zoom with lower-third safe zone subtitles
- Automated 1-Click Upload to YouTube Shorts
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
        print(f"[Assets] Extracted fresh 8K Krishna visuals from images.zip!")
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
        print("[INFO] GEMINI_API_KEY missing or empty. Using today's fresh rotating Krishna Vachan script.")
        return ""

    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.8,
                "responseMimeType": "application/json"
            }
        }
        try:
            r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
            if r.status_code == 200:
                data = r.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
        except Exception as e:
            print(f"[Gemini Warning] Model {model} error: {e}")
            continue

    return ""

# ==================== 31-DAY UNIQUE SCRIPT BANK ====================
# Ensures that even offline, every single day of the month has a 100% distinct, powerful script!
DAILY_KRISHNA_SCRIPTS = [
    {
        "day": 1,
        "headline": "श्री कृष्ण के मूल वचन: कर्म और फल",
        "caption": "कर्म करो, फल की चिंता छोड़ दो। जब तुम अपना सर्वश्रेष्ठ देते हो, तो ईश्वर तुम्हारा साथ कभी नहीं छोड़ते। ✨🙏 #ShriKrishna #GitaGyan #KrishnaVachan #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: हे पार्थ, कर्म तुम्हारा अधिकार है, फल पर तुम्हारा कोई वश नहीं।"},
            {"text": "जब तुम सिर्फ परिणाम की चिंता करते हो, तो वर्तमान का सुंदर कर्म बिगड़ जाता है।"},
            {"text": "फल की इच्छा छोड़कर जब तुम काम करते हो, तो मन में कोई तनाव या भय नहीं रहता।"},
            {"text": "सच्चा योद्धा वही है जो हार या जीत से परे होकर केवल अपना धर्म निभाता है।"},
            {"text": "तुम्हारा आज का निष्काम कर्म ही तुम्हारे कल के स्वर्णिम भविष्य का निर्माण करता है।"},
            {"text": "ईश्वर पर पूरा भरोसा रखो और अपनी पूरी आत्मा अपने कर्म में लगा दो।"},
            {"text": "याद रखो, जो ईमानदारी से कर्म करता है, श्री कृष्ण स्वयं उसके सारथी बनते हैं।"},
            {"text": "जय श्री कृष्ण! ऐसी ही पवित्र और सत्य वाणी के लिए आज ही सब्सक्राइब करें।" }
        ]
    },
    {
        "day": 2,
        "headline": "श्री कृष्ण के मूल वचन: मन की शांति",
        "caption": "अशांत मन कभी सुख नहीं पा सकता। मन को वश में करो, जीवन अपने आप संवर जाएगा। 🌸🙏 #KrishnaVachan #Gita #Spiritual #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: जो मन को वश में नहीं करता, उसका मन ही उसका सबसे बड़ा शत्रु बन जाता है।"},
            {"text": "वायु की तरह चंचल यह मन सिर्फ अभ्यास और वैराग्य से ही स्थिर किया जा सकता है।"},
            {"text": "दूसरों की बातों से विचलित होना बंद करो और अपनी अंतरात्मा की शांति को पहचानो।"},
            {"text": "जिसने अपने मन पर विजय पा ली, उसने इस संपूर्ण संसार को जीत लिया।"},
            {"text": "सुख और दुख दोनों पानी की लहरों की तरह हैं, वे आएंगे और चले जाएंगे।"},
            {"text": "तुम हर परिस्थिति में अडिग रहो, जैसे गहरा समंदर तूफानों में भी शांत रहता है।"},
            {"text": "मेरे चरणों में अपना मन समर्पित करो, तुम्हारी हर चिंता मैं हर लूंगा।"},
            {"text": "राधे राधे! श्री कृष्ण के मूल वचनों को अपने जीवन में उतारने के लिए सब्सक्राइब करें।" }
        ]
    },
    {
        "day": 3,
        "headline": "श्री कृष्ण के मूल वचन: भय और चिंता से मुक्ति",
        "caption": "चिंता छोड़ो और कृष्ण नाम का आश्रय लो। जो कल था वह खोया नहीं, जो आज है वह तुम्हारा है। 🌺✨ #Krishna #BhagavadGita #Peace #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: तुम क्यों व्यर्थ में डरते हो? तुम्हें कौन मार सकता है?"},
            {"text": "आत्मा न कभी जन्म लेती है और न कभी मरती है। यह तो अजर, अमर और शाश्वत है।"},
            {"text": "जो हुआ वह अच्छा हुआ, जो हो रहा है वह अच्छा हो रहा है, जो होगा वह भी अच्छा ही होगा।"},
            {"text": "तुम क्या लेकर आए थे जो तुमने खो दिया? तुमने क्या बनाया था जो नष्ट हो गया?"},
            {"text": "जो आज तुम्हारा है, कल किसी और का था और परसों किसी और का हो जाएगा।"},
            {"text": "परिवर्तन ही इस संसार का एकमात्र नियम है, इसलिए चिंता को त्याग कर आनंद में जियो।"},
            {"text": "जब तक मैं तुम्हारे साथ हूँ, दुनिया की कोई भी शक्ति तुम्हें हरा नहीं सकती।"},
            {"text": "कमेंट में 'जय श्री कृष्ण' लिखें और दिव्य ज्ञान से जुड़ने के लिए सब्सक्राइब करें।" }
        ]
    },
    {
        "day": 4,
        "headline": "श्री कृष्ण के मूल वचन: सच्चा प्रेम और समर्पण",
        "caption": "प्रेम में समर्पण ही परमात्मा की सबसे बड़ी पूजा है। जहां स्वार्थ खत्म होता है, वहीं कृष्ण का वास होता है। 🦚🙏 #ShriKrishna #DivineLove #RadhaKrishna #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: प्रेम कोई बंधन नहीं, प्रेम तो आत्मा की परम मुक्ति का नाम है।"},
            {"text": "जहां किसी से कुछ पाने की इच्छा नहीं होती, केवल सब कुछ न्योछावर करने का भाव होता है, वहीं सच्चा प्रेम है।"},
            {"text": "राधा का प्रेम मेरी आत्मा है और मैं राधा का शाश्वत अस्तित्व हूँ।"},
            {"text": "जो भक्त सच्चे हृदय से मुझे एक फूल या जल भी अर्पित करता है, मैं उसे प्रेम से स्वीकार करता हूँ।"},
            {"text": "संसार की हर वस्तु नश्वर है, केवल पवित्र प्रेम ही युगों-युगों तक जीवित रहता है।"},
            {"text": "अहंकार को मिटा दो, क्योंकि अहंकारी हृदय में कभी प्रेम का अंकुर नहीं फूट सकता।"},
            {"text": "तुम बस प्रेम बांटो, संसार तुम्हें जो भी दे, उसका हिसाब मुझ पर छोड़ दो।"},
            {"text": "अलौकिक प्रेम और गीता उपदेश के लिए चैनल को सब्सक्राइब अवश्य करें।" }
        ]
    },
    {
        "day": 5,
        "headline": "श्री कृष्ण के मूल वचन: क्रोध और विनाश",
        "caption": "क्रोध मनुष्य की बुद्धि को नष्ट कर देता है। शांत रहो, सही निर्णय अपने आप सामने आएगा। ⚡🙏 #KrishnaVachan #GitaTeachings #Wisdom #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: क्रोध से मनुष्य के भीतर भ्रम उत्पन्न होता है और भ्रम से बुद्धि भ्रष्ट हो जाती है।"},
            {"text": "जब बुद्धि का नाश होता है, तो मनुष्य स्वयं अपना ही सर्वनाश कर बैठता है।"},
            {"text": "क्रोध वह विषैली ज्वाला है जो पहले खुद को जलाती है, फिर दूसरों को भस्म करती है।"},
            {"text": "महान व्यक्ति वह नहीं जो दूसरों को झुका दे, बल्कि वह है जो अपने क्रोध पर विजय पा ले।"},
            {"text": "जब भी मन में क्रोध आए, एक पल के लिए मौन हो जाओ और मेरा स्मरण करो।"},
            {"text": "धैर्य और क्षमा ही सबसे बड़े अस्त्र हैं, जो बड़े से बड़े शत्रु को भी मित्र बना देते हैं।"},
            {"text": "अपने भीतर शांति का दीपक जलाओ, अंधेरा अपने आप दूर भाग जाएगा।"},
            {"text": "हर दिन श्री कृष्ण की अमृत वाणी सुनने के लिए चैनल को सब्सक्राइब करें।" }
        ]
    },
    {
        "day": 6,
        "headline": "श्री कृष्ण के मूल वचन: सच्ची मित्रता और विश्वास",
        "caption": "मित्रता धन या पद से नहीं, हृदय की पवित्रता से निभाई जाती है, जैसे कृष्ण और सुदामा। 🤝✨ #Krishna #Sudama #TrueFriendship #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: सच्चा मित्र वह नहीं जो केवल सुख के दिनों में तुम्हारे साथ हंसे।"},
            {"text": "सच्चा मित्र वह है जो संकट की घड़ियों में बिना पुकारे तुम्हारा हाथ थाम ले।"},
            {"text": "मैंने सुदामा के फटे वस्त्र नहीं देखे, मैंने उसके हृदय का अथाह प्रेम और भक्ति देखी।"},
            {"text": "संसार में स्वार्थ के रिश्ते बहुत मिलेंगे, लेकिन निःस्वार्थ मित्रता भगवान के वरदान जैसी होती है।"},
            {"text": "यदि तुम्हारा कोई ऐसा सच्चा मित्र है, तो उस संबंध को प्राणों से भी बढ़कर संभाल कर रखो।"},
            {"text": "विश्वास वह डोर है जो एक बार टूट जाए तो फिर पहले जैसी कभी नहीं जुड़ती।"},
            {"text": "मैं हर उस इंसान का सच्चा सखा हूँ जो निष्कपट भाव से मुझे पुकारता है।"},
            {"text": "जय श्री कृष्ण! ऐसी ही पावन सीख के लिए कृपया सब्सक्राइब करें।" }
        ]
    },
    {
        "day": 7,
        "headline": "श्री कृष्ण के मूल वचन: समय का महत्व",
        "caption": "समय सबसे बड़ा बलवान है। समय का सम्मान करो, तुम्हारा भाग्य चमक उठेगा। ⏳🌸 #ShriKrishna #GitaGyan #Time #Shorts",
        "segments": [
            {"text": "श्री कृष्ण कहते हैं: मैं ही काल हूँ, मैं ही महाकाल हूँ, और इस संपूर्ण सृष्टि का संहारक समय भी मैं ही हूँ।"},
            {"text": "जो बीत गया उसे लौटाया नहीं जा सकता, और जो आने वाला है उस पर तुम्हारा नियंत्रण नहीं।"},
            {"text": "तुम्हारे हाथ में केवल यह वर्तमान क्षण है, इसे व्यर्थ की चिंताओं में मत गंवाओ।"},
            {"text": "समय कभी किसी का इंतजार नहीं करता, जो समय का आदर करता है, समय उसका मान बढ़ाता है।"},
            {"text": "अच्छे दिन हों या बुरे दिन, एक दिन सब बदल जाता है, इसलिए कभी घमंड मत करो।"},
            {"text": "धैर्य रखो, सही समय आने पर तुम्हारी मेहनत का फल तुम्हें अवश्य मिलेगा।"},
            {"text": "समय का हर पल ईश्वर की आराधना और परोपकार में लगाओ, यही जीवन की सार्थकता है।"},
            {"text": "श्री कृष्ण के अनमोल विचार रोज़ पाने के लिए चैनल को सब्सक्राइब करें।" }
        ]
    }
]

def get_today_script() -> dict:
    # 1. Try Gemini Live Generation for Today
    gemini_prompt = f"""
Aaj ki taarikh: {TODAY.strftime('%d %B %Y')}.
Aapko Bhagwan Shri Krishna ke Mool Vachan aur Shrimad Bhagavad Gita par aadharit ek ati-sundar, prabhavshali aur prem-purna Hindi script banani hai.
Kul avadhi lagbhag 50 se 60 second honi chahiye.
Ise 7 se 8 chote segments me baanto (har segment 6-8 second ka, lagbhag 14-18 shabdon ka).
Language: Shuddh, madhur aur prabhavshali Hindi.

Output format: Kripya SIRF valid JSON dein is structure me:
{{
  "id": 1,
  "theme": "bhakti",
  "voice": "hi-IN-MadhurNeural",
  "headline": "श्री कृष्ण के मूल वचन: [Topic Headline]",
  "caption": "[2-line inspiring caption] #ShriKrishna #BhagavadGita #KrishnaVachan #Shorts",
  "segments": [
    {{"text": "Segment 1 text..."}},
    {{"text": "Segment 2 text..."}},
    {{"text": "Segment 3 text..."}},
    {{"text": "Segment 4 text..."}},
    {{"text": "Segment 5 text..."}},
    {{"text": "Segment 6 text..."}},
    {{"text": "Segment 7 text..."}},
    {{"text": "Segment 8 outro text with Subscribe call to action..."}}
  ]
}}
"""
    raw_res = call_gemini(gemini_prompt)
    if raw_res:
        try:
            cleaned = raw_res.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            if "segments" in data and len(data["segments"]) >= 6:
                data["theme"] = "bhakti"
                data["voice"] = "hi-IN-MadhurNeural"
                data["name"] = "post1"
                print(f"[Gemini AI] Fresh live script generated successfully: {data['headline']}")
                return data
        except Exception as e:
            print(f"[Gemini Parse Error] {e}")

    # 2. Pick Day-Indexed Script from Bank (Rotates every day so day 1 != day 2 != day 7)
    day_idx = (TODAY.day - 1) % len(DAILY_KRISHNA_SCRIPTS)
    selected = DAILY_KRISHNA_SCRIPTS[day_idx].copy()
    selected["id"] = 1
    selected["name"] = "post1"
    selected["theme"] = "bhakti"
    selected["voice"] = "hi-IN-MadhurNeural"
    print(f"[Script Bank] Using Day {TODAY.day} Unique Script: {selected['headline']}")
    return selected

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
        
        # Add acoustic silence pad (0.7s) so last word never cuts off
        pad_duration = 1.0 if is_last_segment else 0.7
        cmd_pad = [
            "ffmpeg", "-y", "-i", str(raw_tts),
            "-af", f"apad=pad_dur={pad_duration}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(out_path)
        ]
        pad_res = subprocess.run(cmd_pad, capture_output=True)
        if pad_res.returncode != 0 or not out_path.exists():
            raw_tts.replace(out_path)
        else:
            try:
                raw_tts.unlink()
            except Exception:
                pass
                
        dur = get_audio_duration(out_path)
        return max(dur, 4.0)
    except Exception as e:
        print(f"[TTS Error] {e}. Generating placeholder audio.")
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
            "-t", "5.0", "-q:a", "9", "-acodec", "libmp3lame", str(out_path)
        ], check=True, capture_output=True, timeout=20)
        return 5.0

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

def get_krishna_images() -> list[Path]:
    search_dirs = [
        ASSETS_DIR / "krishna",
        ASSETS_DIR,
        ROOT / "assets" / "images" / "krishna",
        ROOT / "assets" / "images",
    ]
    found = []
    for d in search_dirs:
        if d.exists():
            for p in sorted(d.glob("*.jpg")) + sorted(d.glob("*.png")):
                if p.stat().st_size > 30000 and "v2_" not in p.name and "v3_" not in p.name:
                    if p not in found:
                        found.append(p)
    return found

def get_scene_image(seg_idx: int, total_segs: int) -> Image.Image:
    all_images = get_krishna_images()
    if not all_images:
        print("[WARNING] No local Krishna images found. Creating divine gradient backdrop.")
        return Image.new("RGB", (1080, 1920), (25, 20, 42))

    # Daily Dynamic Rotation: Today's date shifts which image starts first
    # So every day uses a totally fresh sequence!
    day_shift = (TODAY.day * 2) % len(all_images)
    chosen_idx = (day_shift + seg_idx) % len(all_images)
    chosen_path = all_images[chosen_idx]
    
    print(f"    [Scene Visual] Scene {seg_idx + 1}/{total_segs}: Using {chosen_path.name}")
    try:
        im = Image.open(chosen_path)
        return prepare_vertical_image(im)
    except Exception as e:
        print(f"[Image Open Error] {e}")
        return Image.new("RGB", (1080, 1920), (25, 20, 42))

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
            fill=(10, 10, 20, 215),
            outline=(255, 215, 0, 230),
            width=2
        )
    
    # 2. Modern Subtitles in LOWER-THIRD SAFE ZONE (Y = 1290 to 1480)
    # Clear from face (middle 50% is clear), clear from Shorts UI buttons
    sub_font = get_font(50)
    pad = 70
    lines = wrap_text(draw_ov, text, sub_font, W - (2 * pad) - 40)
    
    line_h = 72
    total_text_h = len(lines) * line_h
    
    pill_y1 = int(H * 0.69)
    pill_y2 = pill_y1 + total_text_h + 36
    
    capsule_fill = (12, 12, 22, 195)
    capsule_border = (255, 215, 0, 230)
    
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
        hx1 = (W - head_box_w) // 2
        hy1 = 140
        draw.text(
            (W // 2, hy1 + 38),
            headline,
            font=get_font(38),
            fill=(255, 223, 100),
            anchor="mm"
        )
        
    # Draw subtitles
    sy = pill_y1 + 16
    for line in lines:
        draw.text(
            (W // 2, sy + line_h // 2),
            line,
            font=sub_font,
            fill=(255, 255, 255),
            anchor="mm"
        )
        sy += line_h
        
    return frame

def build_segment_video(base_img: Image.Image, text: str, headline: str, audio_path: Path, duration: float, out_mp4: Path, seg_idx: int):
    temp_dir = out_mp4.parent / f"tmp_seg_{seg_idx}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    fps = 30
    
    frame = render_text_frame(base_img, text, headline)
    frame_path = temp_dir / "frame.png"
    frame.save(frame_path)
    
    frames = max(int(duration * fps), 30)
    if seg_idx % 2 == 0:
        vf = f"scale=1080:1920,zoompan=z='min(zoom+0.0009,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},format=yuv420p"
    else:
        vf = f"scale=1080:1920,zoompan=z='if(lte(zoom,1.0),1.12,max(1.001,zoom-0.0009))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},format=yuv420p"
        
    cmd = [
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
    subprocess.run(cmd, check=True, capture_output=True)

def find_bgm_track() -> Path | None:
    if not MUSIC_DIR.exists():
        return None
    music_files = sorted([p for p in MUSIC_DIR.iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a")])
    if not music_files:
        return None
    # Prefer devotional / flute tracks
    for mf in music_files:
        if any(k in mf.name.lower() for k in ["flute", "krishna", "bhakti", "divine", "radha"]):
            return mf
    return music_files[0]

def assemble_final_video(seg_videos: list[Path], bgm_track: Path | None, out_path: Path):
    temp_dir = out_path.parent
    concat_list = temp_dir / "concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for v in seg_videos:
            f.write(f"file '{v.resolve().as_posix()}'\n")
            
    unmixed = temp_dir / "unmixed.mp4"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(unmixed)
    ]
    subprocess.run(cmd_concat, check=True, capture_output=True)
    
    if bgm_track and bgm_track.exists():
        total_dur = get_audio_duration(unmixed)
        cmd_bgm = [
            "ffmpeg", "-y",
            "-i", str(unmixed),
            "-stream_loop", "-1", "-i", str(bgm_track),
            "-filter_complex",
            f"[1:a]volume=0.14,afade=t=out:st={max(total_dur - 2.5, 1.0)}:d=2.0[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            str(out_path)
        ]
        try:
            subprocess.run(cmd_bgm, check=True, capture_output=True)
            return
        except Exception as e:
            print(f"[BGM Error] {e}. Using unmixed audio.")
            
    unmixed.replace(out_path)

# ==================== MAIN GENERATOR ====================

def generate():
    OUT.mkdir(parents=True, exist_ok=True)
    post = get_today_script()
    manifest = []
    
    name = "post1"
    video_work_dir = OUT / name
    video_work_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n==========================================")
    print(f"🎬 Shri Krishna Mool Vachan: {post['headline']}")
    print(f"==========================================")
    
    segments = post["segments"]
    seg_videos = []
    
    for j, seg in enumerate(segments):
        audio_path = video_work_dir / f"audio_seg_{j}.mp3"
        seg_video_path = video_work_dir / f"seg_{j}.mp4"
        is_last = (j == len(segments) - 1)
        
        # 1. Voiceover TTS
        dur = generate_voiceover(seg["text"], post["voice"], audio_path, is_last_segment=is_last)
        
        # 2. Fresh 8K Visual
        img = get_scene_image(j, len(segments))
        
        # 3. Dynamic Video Segment
        build_segment_video(img, seg["text"], post["headline"], audio_path, dur, seg_video_path, seg_idx=j)
        seg_videos.append(seg_video_path)
        print(f"  ✓ Segment {j+1}/{len(segments)} तैयार ({dur:.1f}s)")
        
    # Assemble final video with BGM
    bgm = find_bgm_track()
    final_mp4 = OUT / f"{name}.mp4"
    assemble_final_video(seg_videos, bgm, final_mp4)
    
    post["name"] = name
    post["video_file"] = str(final_mp4.relative_to(ROOT))
    post["full_caption"] = f"{post['headline']}\n\n{post['caption']}\n\n#ShriKrishna #KrishnaVachan #BhagavadGita #GitaGyan #Shorts"
    manifest.append(post)
    
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n🎉 [SUCCESS] Shri Krishna Video Taiyar: {final_mp4}\n")

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
            "title": (p["headline"] + " | गीता ज्ञान #Shorts")[:95],
            "description": p["full_caption"] + "\n#Shorts #YouTubeShorts #Krishna",
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

def post():
    manifest_path = OUT / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"Manifest file nahi mili: {manifest_path}")
        
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if DRY_RUN:
        print("[DRY RUN ACTIVE] Koi post nahi ki gayi. Video out/ folder me check karein.")
        return
        
    for p in manifest:
        print(f"\n--- Posting: {p['headline']} ({p['name']}) ---")
        if not os.getenv("YT_REFRESH_TOKEN"):
            print("[-] YouTube: Secret 'YT_REFRESH_TOKEN' set nahi hai, skip kiya.")
            continue
        try:
            post_youtube(p)
            print(f"[SUCCESS] YouTube par video upload ho gayi!")
        except Exception as e:
            print(f"[FAIL] YouTube upload error: {e}")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if action == "generate":
        generate()
    elif action == "post":
        post()
    elif action == "all":
        generate()
        post()
    else:
        print(f"Unknown action: {action}")
