import os
from googletrans import Translator,LANGCODES
from gtts import gTTS
from pytube import YouTube

def translate_text(text,lang_code):
    """
    Translate the input text to the specified language using Google Translate API.

    Args:
        text (str): The text to be translated.
        lang_code (str): The language code of the target language.

    Yields:
        str: The translated text.

    """
    
    for chunk in create_chunks(text):
        translated_chunk = Translator().translate(chunk, dest=lang_code)
        yield translated_chunk.text

def create_chunks(text):
    """
    Break the input text into chunks of the specified size.

    Args:
        text (str): The input text to be split.
        chunk_size (int): The maximum size of each chunk. Defaults to 10000.

    Yields:
        str: A chunk of the input text.

    """
    for i in range(0, len(text), 10000):
        yield text[i:i+10000]

def fetch_translated_text(text,lang_choice):
    """
    Fetch the translated text for the given input text and target language.

    Args:
        text (str): The input text to be translated.
        lang_choice (str): The language code of the target language.

    Returns:
        str: The translated text.

    """    
    translated_result=""
    for translated_chunk in translate_text(text, LANGCODES[lang_choice.lower()]):
        translated_result=translated_result+(translated_chunk)
    return translated_result


def ttspeech(text: str, language: str) -> None:
    """
    Converts the given text into speech and saves it as an mp3 file.

    Args:
        text (str): Text to be converted into speech.
        language (str): Language of the text.

    Returns:
        None
    """

    # Creating the speech using the gTTS library
    speech = gTTS(text=text, lang=LANGCODES[language.lower()], slow=False)

    # Defining the file name and path to save the speech as mp3 file
    file_name = "savedaudiofile.mp3"
    file_path = os.path.join(os.path.dirname(__file__), file_name)

    # Saving the speech as an mp3 file
    speech.save(file_path)

def vid_duration(duration):
    """
    Converts the duration of a video from seconds to hours, minutes and seconds.

    Args:
        duration (int): Duration of the video in seconds.

    Returns:
        A string representation of the duration in the format 'hh:mm:ss'.
    """
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_vid_data(link):
    """
    Gets the title, duration, description, and thumbnail URL of a YouTube video.

    Args:
        link (str): URL of the YouTube video.

    Returns:
        A dictionary containing the video data.
    """
    yt = YouTube(link)

    # Collecting relevant data from the video
    data = {
        "Title": yt.title,
        "Duration": vid_duration(yt.length),
        "Description": yt.description,
        "Thumbnail": yt.thumbnail_url,
        
    }
    
    return data


# print(get_vid_data("https://www.youtube.com/watch?v=5tmGKTNW8DQ"))