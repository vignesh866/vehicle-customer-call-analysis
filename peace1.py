import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.utils import make_chunks
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import regex
import csv


def get_subject(tokenized_text):
    txt = ' '.join(tokenized_text)
    for keys in word_to_class_map.keys():
        pattern = "(?e)("+keys+"){e<=1}"
        keys
        m = regex.search(pattern, txt)
        if m is not None:
            return(classes[word_to_class_map[keys]])


def import_all_audio_files(file_location):
    audio_file_list = []
    for file in os.listdir():
        if file.endswith(".wav"):
            audio_file_list.append(file)
    return audio_file_list


def audio_splitter(file_name, chunk_length_ms, file_type):
    myaudio = AudioSegment.from_file(file_name, file_type)
    chunks = make_chunks(myaudio, chunk_length_ms)  # Make chunks of chunk_length sec

    chunk_name_list = []
    for i, chunk in enumerate(chunks):
        chunk_name = "chunk{0}.wav".format(i)
        chunk_name_list.append(chunk_name)
        chunk.export(chunk_name, format="wav")
    return chunk_name_list


def convert_audio_to_text(input_file):
    speech = sr.Recognizer()
    with sr.AudioFile(input_file) as source:
        audio = speech.record(source)  # read the entire audio file

    # recognize speech using Google Speech Recognition
    try:
        string_output = speech.recognize_google(audio)
        return f"{string_output.lower()} "

    except sr.UnknownValueError:
        return " "
    except sr.RequestError as e:
        print("Could not request results from Google service; {0}".format(e))


def text_preprocessing(audio_file, split_time, audio_format):
    audio_2_text = str()
    audio_chunks = audio_splitter(audio_file, split_time, audio_format)
    for chunk in audio_chunks:
        audio_2_text += convert_audio_to_text(chunk)
        os.remove(chunk)
    all_tokens = word_tokenize(audio_2_text)
    stop_words = set(stopwords.words("english"))
    tokens = [words for words in all_tokens if words not in stop_words]
    # Lemmatizr
    lemmatizer = WordNetLemmatizer()
    stems = []
    for t in tokens:
        stems.append(lemmatizer.lemmatize(t))
    return stems


if __name__ == "__main__":

    file_category_dict = {}

    classes = {
        0: 'new vehicle purchase enquiries',
        1: 'test drive request',
        2: 'breakdown',
        3: 'feedback',
        4: 'vehicle quality'
    }

    word_to_class_map = {
        'purchase': 0,
        'new vehicle': 0,
        'take test': 1,
        'test drive': 1,
        'break': 2,
        'broken': 2,
        'breakdown': 2,
        'got broken': 2,
        'satisfaction': 3,
        'scale 1': 3,
        'problem': 4,
        'issue': 4
    }

    audio_file_list = import_all_audio_files(os.getcwd())
    for audio_file in audio_file_list:
        stems = text_preprocessing(audio_file, 9000, "wav")
        file_category_dict[audio_file] = get_subject(stems)

    # fuzzy logic based, semantic regex matching
    with open('TEAMPEACE_i-jtmgj.csv', 'w', newline='') as f:
        fieldnames = ['audio_name', 'Category']
        writem = csv.DictWriter(f, fieldnames=fieldnames)
        writem.writeheader()
        for key in file_category_dict:
            writem.writerow({'audio_name': key, 'Category': file_category_dict[key]})
