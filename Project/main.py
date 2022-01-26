import PyPDF3
from textblob import TextBlob
import os
from google.cloud import texttospeech
from gtts import gTTS

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "AI_Video_Dub_Credentials.json"
client = texttospeech.TextToSpeechClient()

def valid(file):
    print(f"Checking {file} ...")

    # If file is not ending with .pdf means its not a valid pdf file.
    if not file.lower().endswith(".pdf") or not os.path.isfile(file):
        print("Please enter valid pdf file address.")
        return False
    return True

def extract_text(filename, page_num=None):
    file_path = open(filename, 'rb')

    print("File is ready to read")
    pdfReader = PyPDF3.PdfFileReader(file_path)
    
    # If user provide their custom page to starts from.
    if page_num:
        text = pdfReader.getPage(page_num-1).extractText()
    else:
        text = pdfReader.getPage(0).extractText()
    
    file_path.close() # Closing file
    def detect_language(text):
        lang = TextBlob(text).detect_language()
        return lang

    file_lang = detect_language(text)
    print(f"File language is: {file_lang}")

    # print(text)
    return text, file_lang

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

def list_voices():
        voices = client.list_voices()
        available_voices = {}
        for idx, voice in enumerate(voices.voices):
            # Display the voice's name. Example: tpc-vocoded
            print(f"{idx}. Name: {voice.name}")
        
        # Display the supported language codes for this voice. Example: "en-US"
            for language_code in voice.language_codes:
                print(f"Supported language: {language_code}")
                # available_voices.append(language_code)
                available_voices[idx] = (voice.name, language_code)
        
        ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

        # Display the SSML Voice Gender
        print(f"SSML Voice Gender: {ssml_gender.name}")

        # Display the natural sample rate hertz for this voice. Example: 24000
        print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")

        # Select voice
        def select_voice(available_voices):
            if available_voices is not None:
                return available_voices[int(input("Please select the voice number: "))]
        
        return select_voice(available_voices)

def convert_to_speech(file, selectVoiceName=False, speakingRate=0.8, default_attr=False):
    if not valid(file):
        return
    
    text, lang = extract_text(file)
    file_name = file.split(".")[0]
    
    # If default_attr is True means no voice selection and no speaking rate selection returns default voice
    if default_attr:
        try:
            print("Generating audio")
            myobj = gTTS(text=text, lang=lang, slow=False)
            myobj.save(f"{file_name}.mp3")
            print("Audio saved successfully")
            return
        except Exception as e:
            print("There is some error on our end.\nerror: ", e)
            return

    language_code = voice_name = None
    if selectVoiceName:
        selected_voice = list_voices()
        print(f"You have selected\nVoice name: {selected_voice[0]} and Language code: {selected_voice[1]}")
        voice_name = selected_voice[0]
        language_code = selected_voice[1]
        clear_console()
    else:
        language_code = "en-US"
        voice_name = "en-US-Wavenet-C"
        print(f"You do not selected any voice name so going with default Voice: {voice_name} and Language code: {language_code}")
    
    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speakingRate
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open(f"{file_name}.mp3", "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{file_name}.mp3"')

    
# if __name__ == "main":
convert_to_speech("LOA.pdf", selectVoiceName=True, speakingRate=1, default_attr=False)
