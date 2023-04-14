import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
import pathlib
import numpy as np
import tensorflow as tf
from zipfile import ZipFile
from keras import layers,models
from numpy import loadtxt
from core.forms import UploadFileForm,StudentForm
from os import path
from pydub import AudioSegment
import soundfile

def squeeze(audio, labels):
  audio = tf.squeeze(audio, axis=-1)
  return audio, labels

def get_spectrogram(waveform):
  # Convert the waveform to a spectrogram via a STFT.
  spectrogram = tf.signal.stft(
      waveform, frame_length=255, frame_step=128)
  # Obtain the magnitude of the STFT.
  spectrogram = tf.abs(spectrogram)
  # Add a `channels` dimension, so that the spectrogram can be used
  # as image-like input data with convolution layers (which expect
  # shape (`batch_size`, `height`, `width`, `channels`).
  spectrogram = spectrogram[..., tf.newaxis]
  return spectrogram

def make_spec_ds(ds):
  return ds.map(
      map_func=lambda audio,label: (get_spectrogram(audio), label),
      num_parallel_calls=tf.data.AUTOTUNE)

def run_tensorflow_model():
    filename = "Storage/sounds/whaleDB_reduced.zip"
    with ZipFile(filename, 'r') as zip:
        # extracting all the files
        print('Extracting all the files now...')
        zip.extractall()
        print('Extraction completed...')
    DATASET_PATH = 'whaleDB_reduced'
    data_dir = pathlib.Path(DATASET_PATH)
    train_ds, val_ds = tf.keras.utils.audio_dataset_from_directory(
        directory=data_dir,
        batch_size=64,
        validation_split=0.2,
        seed=0,
        output_sequence_length=16000,
        subset='both')
    label_names = np.array(train_ds.class_names)
    train_ds = train_ds.map(squeeze, tf.data.AUTOTUNE)
    val_ds = val_ds.map(squeeze, tf.data.AUTOTUNE)
    test_ds = val_ds.shard(num_shards=2, index=0)
    val_ds = val_ds.shard(num_shards=2, index=1)

    train_spectrogram_ds = make_spec_ds(train_ds)
    val_spectrogram_ds = make_spec_ds(val_ds)
    test_spectrogram_ds = make_spec_ds(test_ds)

    for example_spectrograms, example_spect_labels in train_spectrogram_ds.take(1):
        break

    train_spectrogram_ds = train_spectrogram_ds.cache().shuffle(10000).prefetch(tf.data.AUTOTUNE)
    val_spectrogram_ds = val_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)
    test_spectrogram_ds = test_spectrogram_ds.cache().prefetch(tf.data.AUTOTUNE)

    input_shape = example_spectrograms.shape[1:]
    print('Input shape:', input_shape)
    num_labels = len(label_names)

    # Instantiate the `tf.keras.layers.Normalization` layer.
    norm_layer = layers.Normalization()
    # Fit the state of the layer to the spectrograms
    # with `Normalization.adapt`.
    norm_layer.adapt(data=train_spectrogram_ds.map(map_func=lambda spec, label: spec))

    model = models.Sequential([
        layers.Input(shape=input_shape),
        # Downsample the input.
        layers.Resizing(32, 32),
        # Normalize.
        norm_layer,
        layers.Conv2D(32, 3, activation='relu'),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.25),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_labels),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'],
    )

    EPOCHS = 30
    history = model.fit(
        train_spectrogram_ds,
        validation_data=val_spectrogram_ds,
        epochs=EPOCHS,
    )

    model.evaluate(test_spectrogram_ds, return_dict=True)

    model.save('Storage/models/my_model')
    with open("Storage/models/label_names.txt", "w") as txt_file:
      for line in label_names:
          txt_file.write("".join(line) + "\n")

    return True #model, label_names



#Function to input current wav file 
# Returns predicted whale species name

def detect_whale(model, audio_file_path, label_names):
    print('audio_file_path',audio_file_path)
    try:
        if audio_file_path.endswith('.mp3'):
            new_audio_file_path = audio_file_path.replace('.mp3','.wav')
            AudioSegment.from_file(audio_file_path).export(new_audio_file_path, format="wav")
            data, samplerate = soundfile.read(new_audio_file_path)
            soundfile.write(new_audio_file_path, data, samplerate, subtype='PCM_16')
            audio_file_path = new_audio_file_path
        audio_file = tf.io.read_file(str(audio_file_path))
        audio_file, sample_rate = tf.audio.decode_wav( audio_file, desired_channels=1, desired_samples=16000,)
        audio_file = tf.squeeze(audio_file, axis=-1)
        audio_file = get_spectrogram(audio_file)
        audio_file = audio_file[tf.newaxis,...]
        prediction = model(audio_file)
        score = tf.nn.softmax(prediction[0])
        y_classes = np.argmax(score,axis=-1)
    except Exception as e:
       print('Error in detection: ',e)


    return label_names[y_classes]

whales = {'southern_right_whale':'Eubalaena australis', 'minke_whale':'Balaenoptera acutorostrata', 'sperm_whale':'Physeter macrocephalus', 
        'bluewhale':'Balaenoptera musculus','finbackwhale':'Balaenoptera physalus', 'northern_right_whale':'Eubalaena glacialis', 'bowhead_whale':'Balaena mysticetus', 'narwhal':'Monodon monoceros',
        'killer_whale':'Orcinus orca', 'short_finned_pilot_whale':'Globicephala macrorhynchus', 'false_killerwhale':'Pseudorca crassidens',
        'humpbackwhale':'Megaptera novaeangliae', 'melon_headed_whale':'Peponocephala electra', 'long_finned_pilot_whale':'Globicephala melas',
         'belugawhite_whale':'Delphinapterus leucas'}

def info_scraper(name):
    common_name=''
    scientific_name=''
    length_ft=''
    lifespan_years=''
    family=''
    kingdom = ''
    about = ''
    page = requests.get("https://www.google.com/search?q="+ name)
    common_name = name.title().replace('_', ' ')
    soup = BeautifulSoup(page.content, 'html.parser')
    divparent = soup.find_all('div', attrs={'class':'BNeawe s3v9rd AP7Wnd'})
   # print(divparent)
    for div in divparent:
        # for div in divparent:
        #     if not about:
        #         for about_div in div.find_all('div',attrs={'class':'BNeawe s3v9rd AP7Wnd'}):
        #             if about_div.text:
        #                 about = about_div.text
        #                 about.replace('Wikipedia','')
        #                 break
        for span in div.find_all('span', attrs={'class':'BNeawe s3v9rd AP7Wnd'}):
           # about = div.find_all('span',attrs={'class':'BNeawe s3v9rd AP7Wnd'})[0].text
            if span.text == 'Scientific name':
                scientific_name = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
            if span.text == 'Length':
                length_ft = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
            if span.text == 'Lifespan':
                lifespan_years = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
            if span.text == 'Family':
                family = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
            if span.text == 'Kingdom':
                kingdom = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
               
        if scientific_name == '':
            scientific_name = whales[name]
    return {'common_name':common_name,'scientific_name':scientific_name,'length_ft':length_ft,
            'lifespan_years':lifespan_years,'family':family,'kingdom':kingdom,'about':about}

def train_model(request):
   run = run_tensorflow_model()
   if run:
    html = "<html><body>Model trained! </body></html>"
   else:
    html = "<html><body>Model not trained! </body></html>"
   return HttpResponse(html)

def detect_whale_sound(request,file_name=None):
    model = tf.keras.models.load_model('Storage/models/my_model')
    label_names = loadtxt('Storage/models/label_names.txt', dtype='str')
    response = detect_whale(model, file_name, label_names)
    return response

def index(request):
   context ={} #"<html><body>index connected </body></html>"
   return render(request,'index.html',context)
   
def recorder(request):
   context ={'whale_info':"<h1>{'common_name': 'Humpbackwhale', 'scientific_name': 'Megaptera novaeangliae', 'length_ft': '49 – 52 ft. (Female, Adult) and 43 – 46 ft. (Male, Adult)', 'lifespan_years': '', 'family': 'Balaenopteridae', 'kingdom': 'Animalia', 'about': ''}</h1>"} #"<html><body>index connected </body></html>"
   context = {}
   return render(request,'recorder.html',context)


def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        filename = 'Storage/uploads/'+str(myfile.name)
        whale_type = detect_whale_sound(request,filename)
        whale=info_scraper(whale_type)
        return render(request, 'recorder.html', {'whale_info': whale})
    else:
         HttpResponseRedirect('../recorder.html')

    return render(request, 'recorder.html', {'whale_info': whale})

