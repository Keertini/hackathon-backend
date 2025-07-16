from gtts import gTTS
from io import BytesIO

def generate_tts_audio(text, lang="en"):
    """
    Generates TTS audio as a BytesIO buffer.
    
    Args:
        text (str): The text to convert to speech.
        lang (str): Language code, e.g., 'en'.

    Returns:
        BytesIO: Audio data buffer ready to send as a file.
    """
    tts = gTTS(text=text, lang=lang)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf
