#!/usr/bin/env python
# coding: utf-8

# ![ai](https://www.emineo-education.fr/wp-content/uploads/2022/11/supdevinci-nantes.png)
# 
# 
# <h4 style="text-align: left; color:#20a08d; font-size: 35px"><span><strong> Assurez la modération des contenus multimédia avec AWS</strong></span></h4>

# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Introduction
# </strong></span></h4>

# Le saviez-vous ? Les réseaux sociaux du groupe Meta Facebook et Instagram recueillent environ 2 milliards d'images de leurs utilisateurs tous les jours. Imaginez toute l'infrastructure informatique nécessaire pour traiter toutes ces données

# ![](https://github.com/archiducarmel/SupDeVinci_Developpement/releases/download/ia_ml_aws/fb.gif)

# Afin de fournir des services intuitifs à leurs utilisateurs, plusieurs traitements sont réalisés sur chacune de ces images.

# ![](https://github.com/archiducarmel/SupDeVinci_Developpement/releases/download/ia_ml_aws/fb2.png)

# Nous allons utiliser dans ce TP les services AWS pour réaliser quelques-uns de ces fonctionnalités. La finalité ultime consiste à développer une fonction de traitement qui recueille une image ou une vidéo en entrée, la modère afin de vérifier si son contenu est publiable, produit des sous-titres (dans le cas des vidéos) et fournit des hashtags issus de mots les plus représentatifs du contenu.

# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Workflow de traitement
# </strong></span></h4>

# Voici ci-dessous le procédé de traitement qui sera appliqué de bout-en-bout sur toute image présentée en entrée de la fonction de traitement.
# 
# ![](https://github.com/archiducarmel/SupDeVinci_Developpement/releases/download/ia_ml_aws/aws_socialmedia.drawio.png)

# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Détection du type de fichier
# </strong></span></h4>

# La fonction `check_filetype` ci-dessous permet de déterminer le type (image ou vidéo) d'un fichier fourni en entrée.

# In[44]:


import os

def check_filetype(filename):
    file_basename = os.path.basename(filename)
    extension = file_basename.split(".")[-1]
    if extension in ["jpg", "png", "tiff", "svg"]:
        filetype = "image"
    elif extension in ["mp4", "avi", "mkv"]:
        filetype = "video"
    else :
        filetype = None
    
    print(f"[INFO] : Filename {file_basename} type is : {filetype}")
    
    return filetype


# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Extraction d'une image de la vidéo
# </strong></span></h4>

# La fonction `extract_frame_video` ci-dessous permet d'extraire une image sous forme de tableau de pixels d'une vidéo à partir de la position de l'image dans la vidéo

# In[46]:


import cv2

def extract_frame_video(video_path, frame_id):
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
    ret, frame = video.read()
    return frame


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">extract_frame_video</code> sur la vidéo de test afin d'en extraire la première image de la vidéo, puis affichez cette image avec <code style="text-align: left; font-size: 16px; color:#131fcf">matplotlib</code></span></p>

# In[47]:


from matplotlib import pyplot as plt
import cv2


# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Modération d'une image
# </strong></span></h4>

# La fonction `get_aws_session` ci-dessous permet de se connecter à une session AWS en utilisant les clés d'accès et clés secrètes.

# In[1]:

# In[19]:


#!pip install boto3 python-dotenv 
#!pip install nltk


# In[4]:


import os, boto3
from dotenv import load_dotenv

def get_aws_session():
    load_dotenv()  # take environment variables from .env.

    # Create an aws_session
    aws_session = boto3.Session(
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        region_name="us-east-1"
    )
    
    return aws_session


# Passons maintenant au développement de la fonction `moderate_image`. Cette fonction prendra en entrée une image et renverra la liste des thèmes choquants présents dans l'image, s'il y'en a. 

# <p style="text-align: left; font-size: 16px; color:#7a0f43"><span>❓ Quelle service AWS serait le plus indiqué pour réaliser ce traitement ?</span></p>

# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code dans la fonction  <strong>moderate_image</strong> permettant d'analyser une image et détecter les sujets de modération </span></p>

# In[5]:


def moderate_image(image_path, aws_service):
    
    moderation_list = list()
    
    with open(image_path, 'rb') as image:
        response = aws_service.detect_moderation_labels(Image={'Bytes': image.read()})
        for label in response['ModerationLabels']:
            moderation_list.append(label['Name'])
    
    return moderation_list


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant de tester la fonction  <strong>moderate_image</strong>. Pour ce faire : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#     <li>Instancier une session AWS avec vos clés</li>
#     <li>Instancier le service AWS approprié pour ce traitement </li>
#     <li>Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">moderate_image</code> avec ce service comme argument afin de recueillir la liste potentielle des thèmes choquants</li>
#     </ul> </span></p>

# In[7]:

aws_session = get_aws_session()

# Create a client session for Rekognition 
rekognition = aws_session.client('rekognition')


# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Production de sous-titres
# </strong></span></h4>

# La production de sous-titres à partir d'une vidéo s'appuiera sur la technologie speech-to-text d'AWS.

# <div class="alert alert-info">
#   <strong>BUCKET S3</strong><br><br> Au préalable, assurez-vous d'avoir créé un bucket S3 puisque la transcription speech-to-text nécessite que le fichier transcrit soit déposé dans un bucket S3
# </div>

# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant d'instancier un client S3 puis de créer un bucket </span></p>

# In[13]:


# To upload the image you clicked to S3 bucket
s3 = aws_session.client('s3')
try:
    s3.create_bucket(Bucket='test-bucket-sdvnantes-2')
except :
    print("Le bucket existe déjà !")


# <p style="text-align: left; font-size: 16px; color:#7a0f43"><span>❓ Quelle service AWS serait le plus indiqué pour réaliser ce traitement de transcription speech-to-text ?</span></p>

# In[ ]:





# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code de la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">get_text_from_speech</code> permettant de réaliser la transcription speech-to-text avec AWS</span></p>

# <p style="text-align: left; font-size: 16px; color:#ec8f1a"><span>📚  Voice to text using AWS Transcribe : </span> <a href="https://dev.to/botreetechnologies/voice-to-text-using-aws-transcribe-with-python-1cfc">https://dev.to/botreetechnologies/voice-to-text-using-aws-transcribe-with-python-1cfc</a></p> 

# In[14]:


import time
import urllib
import json
import os

def get_text_from_speech(filename, aws_service, job_name, bucket_name):
    
    job_uri = f"https://s3.amazonaws.com/{bucket_name}/{os.path.basename(filename)}"

    aws_service.start_transcription_job(TranscriptionJobName=job_name, Media={'MediaFileUri': job_uri}, MediaFormat='mp4', LanguageCode='fr-FR')
    
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("[INFO] : Not ready yet !")
        time.sleep(2)
    print("[INFO] : Job finished !")
    


    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        response = urllib.request.urlopen(status['TranscriptionJob']['Transcript']['TranscriptFileUri'])
        data = json.loads(response.read())
        text = data['results']['transcripts'][0]['transcript']
    
    return text


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant de tester la fonction  <strong>get_text_from_speech</strong>. Pour ce faire : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#     <li>Uploader la vidéo de test sur le bucket de test préalablement créé</li>
#     <li>Instancier le service AWS approprié pour ce traitement </li>
#     <li>Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">get_text_from_speech</code> avec ce service comme argument afin de recueillir le texte recueilli</li>
#     </ul> </span></p>

# In[16]:


import os

TEST_VIDEO_FILE = "./assets/tuto_coiffure.mp4"
BUCKET_NAME = 'test-bucket-sdvnantes-2'

# Create a client session for Transcribe 
transcribe = aws_session.client('transcribe')


# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Production de hashtags d'une séquence vidéo
# </strong></span></h4>

# La production de hashtag sur une séquence vidéo se base sur le texte extrait de la vidéo après l'étape de speech-to-text, qui sera utilisé pour en extraire des mots-clés (keyphrases). Au préalable, le texte extrait devra être nettoyé pour y enlever quelques éléments inutiles. C'est la fonction de la fonction `clean_text`

# In[20]:


import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

def clean_text(raw_text):
 
    stop_words = set(stopwords.words('french')+ ["on", "ça", "je", "tu"]) 

    tokenizer = RegexpTokenizer(r'\w+')

    #word_tokens = word_tokenize(example_sent)
    word_tokens = tokenizer.tokenize(raw_text)

    # converts the words in word_tokens to lower case and then checks whether 
    #they are present in stop_words or not
    filtered_sentence_1 = [w.lower() for w in word_tokens if not w.lower() in stop_words]
    #with no lower case conversion
    filtered_sentence = []

    for w in filtered_sentence_1:
        if w not in stop_words:
            filtered_sentence.append(w)

    filtered_text = " ".join(filtered_sentence)
    
    return filtered_text


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">clean_text</code> le texte extrait afin de recueillir un texte nettoyé</span></p>

# In[24]:



def extract_keyphrases(text, aws_service):
    response = aws_service.detect_key_phrases(Text=text, LanguageCode='fr')
    
    sorted_keyphrases = sorted(response["KeyPhrases"], key=lambda x: x['Score'])
    
    hashtags = [dic["Text"] for dic in sorted_keyphrases[-10:]]
    
    return hashtags


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant de tester la fonction  <strong>extract_keyphrases</strong>. Pour ce faire : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#     <li>Instancier le service AWS approprié pour ce traitement </li>
#     <li>Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">extract_keyphrases</code> avec ce service comme argument afin de recueillir la liste des mots-clés</li>
#     </ul> </span></p>

# In[27]:


# Create a client session for Comprehend 
comprehend = aws_session.client('comprehend')


# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Production de hashtags d'une image
# </strong></span></h4>

# La production de hashtags sur une image se base sur la détection des objets et des célébrités présents dans l'image.

# <h4 style="text-align: left; color:#20a08d; font-size: 20px"><span><strong> Détection d'objets sur une image
# </strong></span></h4>

# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code de la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">detect_objects</code> permettant de détecter les objets présents sur une image donnée en entrée de la fonction. Ne retenez que les 10 objets détectés avec le plus de confiance.</span></p>

# In[28]:


def detect_objects(image_path, aws_service):
    with open(image_path, 'rb') as image:

        response = aws_service.detect_labels(
            Image={
                'Bytes': image.read()
            },
            MaxLabels=100,
            MinConfidence=50)

        objects_list = [objects["Name"] for objects in response["Labels"]][:10]
    
    return objects_list


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant de tester la fonction  <strong>detect_objects</strong>. Pour ce faire : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#     <li>Instancier le service AWS approprié pour ce traitement </li>
#     <li>Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">detect_objects</code> avec ce service comme argument afin de recueillir la liste des objets présents sur cette image de test</li>
#     </ul> </span></p>

# In[29]:


rekognition = aws_session.client('rekognition')


# <h4 style="text-align: left; color:#20a08d; font-size: 20px"><span><strong> Détection des célébrités sur une image
# </strong></span></h4>

# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code de la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">detect_celebrities</code> permettant de détecter les célébrités présents sur une image donnée en entrée de la fonction.</span></p>

# In[30]:


def detect_celebrities(image_path, aws_service):
    
    with open(image_path, 'rb') as image:

        response = aws_service.recognize_celebrities(
            Image={'Bytes': image.read()})

        celebrities_list = [celebrity["Name"] for celebrity in response["CelebrityFaces"]][:10]

        return celebrities_list


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant de tester la fonction  <strong>detect_celebrities</strong>. Pour ce faire : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#     <li>Instancier le service AWS approprié pour ce traitement </li>
#     <li>Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">detect_celebrities</code> avec ce service comme argument afin de recueillir la liste des célébrités présentes sur chacune des images de test</li>
#     </ul> </span></p>

# In[31]:


# <h4 style="text-align: left; color:#20a08d; font-size: 20px"><span><strong> Reconnaissance d'émotion faciale sur une image
# </strong></span></h4>

# <span style="color:#131fcf">🖥️ Codez la fonction `detect_emotions` qui doit :
# 
# <ul style="color:#131fcf">
# <li>Prendre en entrée :
#   <ul>
#     <li>Le chemin de l'image à analyser</li>
#     <li>Le client AWS Rekognition configuré</li>
#   </ul>
# </li>
# 
# <li>Analyser l'image :
#   <ul>
#     <li>Ouvrir l'image en mode binaire</li>
#     <li>Utiliser Rekognition avec <strong>detect_faces</strong></li>
#     <li>Demander tous les attributs (Attributes=['ALL'])</li>
#   </ul>
# </li>
# 
# <li>Pour chaque visage détecté, afficher :
#   <ul>
#     <li>Le genre avec son niveau de confiance</li>
#     <li>L'âge estimé (range min-max)</li>
#     <li>Les 3 émotions principales avec leur niveau de confiance</li>
#   </ul>
# </li>
# 
# <li>Retourner la liste complète des informations des visages détectés</li>
# 
# <li>Exemple de sortie console attendue :
# <code style="color:#131fcf">
# [INFO] Visage détecté:
#   - Genre: Male (confiance: 99.9%)
#   - Âge estimé: 20-30 ans
#   - Émotions principales:
#     * HAPPY: 95.5%
#     * CALM: 4.5%
# ---
# </code>
# </li>
# </ul>
# </span>

# In[38]:


def detect_emotions(image_path, aws_service):
    """
    Détecte les émotions sur les visages présents dans une image en utilisant Amazon Rekognition.
    
    Cette fonction analyse une image pour détecter les visages et leurs émotions associées.
    Pour chaque visage, elle retourne les émotions détectées avec leur niveau de confiance.
    
    Paramètres :
    - image_path (str) : Chemin vers l'image à analyser
    - aws_service (boto3.client) : Client AWS Rekognition configuré
    
    Retourne :
    - list[dict] : Liste des visages détectés avec leurs émotions
                  Format: [
                      {
                          'BoundingBox': dict,
                          'Emotions': [
                              {
                                  'Type': str,  # HAPPY, SAD, ANGRY, CONFUSED, etc.
                                  'Confidence': float
                              },
                              ...
                          ],
                          'AgeRange': {'Low': int, 'High': int},
                          'Gender': {'Value': str, 'Confidence': float}
                      },
                      ...
                  ]
    
    Exemple :
    >>> rekognition = boto3.client('rekognition')
    >>> emotions = detect_emotions("./photo.jpg", rekognition)
    >>> for face in emotions:
    ...     print(f"Émotions détectées : {face['Emotions']}")
    """
    try:
        # Lire l'image
        with open(image_path, 'rb') as image:
            response = aws_service.detect_faces(
                Image={'Bytes': image.read()},
                Attributes=['ALL']  # Demander tous les attributs, y compris les émotions
            )
        
        # Extraire les informations pertinentes pour chaque visage
        faces_info = []
        for face in response['FaceDetails']:
            face_data = {
                'BoundingBox': face['BoundingBox'],
                'Emotions': sorted(
                    face['Emotions'],
                    key=lambda x: x['Confidence'],
                    reverse=True
                ),
                'AgeRange': face['AgeRange'],
                'Gender': {
                    'Value': face['Gender']['Value'],
                    'Confidence': face['Gender']['Confidence']
                }
            }
            faces_info.append(face_data)
            
            # Log des émotions détectées pour ce visage
            print(f"[INFO] Visage détecté:")
            print(f"  - Genre: {face_data['Gender']['Value']} "
                  f"(confiance: {face_data['Gender']['Confidence']:.2f}%)")
            print(f"  - Âge estimé: {face_data['AgeRange']['Low']}-{face_data['AgeRange']['High']} ans")
            print("  - Émotions principales:")
            for emotion in face_data['Emotions'][:3]:  # Top 3 des émotions
                print(f"    * {emotion['Type']}: {emotion['Confidence']:.2f}%")
            print("---")
        
        return faces_info
        
    except Exception as e:
        print(f"[ERREUR] Une erreur est survenue lors de la détection des émotions : {str(e)}")
        return []


# <span style="color:#131fcf">🖥️ Codez la fonction `summarize_emotions` qui doit :
# 
# <ul style="color:#131fcf">
# <li>Prendre en entrée une liste de visages détectés dans une image comme fourni par la fonction <code>detect_emotions</code></li>
# <li>Exemple d'entrée :
# <code style="color:#131fcf">
# [{
#     'Gender': {'Value': 'Male', 'Confidence': 99.9},
#     'AgeRange': {'Low': 20, 'High': 30},
#     'Emotions': [
#         {'Type': 'HAPPY', 'Confidence': 95.5},
#         {'Type': 'CALM', 'Confidence': 4.5}
#     ]
# }]
# </code>
# <li>Pour chaque visage, analyser :
#   <ul>
#     <li>Le genre (Homme/Femme)</li>
#     <li>L'âge (calcul de la moyenne du range)</li>
#     <li>Les émotions avec une confiance > 50%</li>
#   </ul>
# </li>
# 
# <li>Retourner un dictionnaire avec :
#   <ul>
#     <li>Nombre total de visages</li>
#     <li>Émotion dominante (celle avec la plus haute confiance moyenne)</li>
#     <li>Statistiques des émotions (comptage et confiance moyenne)</li>
#     <li>Statistiques d'âge (min, max, moyenne)</li>
#     <li>Distribution des genres</li>
#   </ul>
# </li>
# </li>
# </ul>
# </span>

# In[39]:


def summarize_emotions(faces_info):
    """
    Résume les émotions détectées sur tous les visages d'une image.
    
    Cette fonction agrège les émotions de tous les visages et calcule les émotions
    dominantes dans l'image.
    
    Paramètres :
    - faces_info (list[dict]) : Liste des informations des visages détectés
    
    Retourne :
    - dict : Résumé des émotions dominantes et statistiques
    
    Exemple :
    >>> emotions = detect_emotions("./group_photo.jpg", rekognition)
    >>> summary = summarize_emotions(emotions)
    >>> print(f"Émotion dominante : {summary['dominant_emotion']}")
    """
    if not faces_info:
        return {
            'number_of_faces': 0,
            'dominant_emotion': None,
            'emotion_stats': {},
            'age_stats': {'min': None, 'max': None, 'average': None},
            'gender_distribution': {'MALE': 0, 'FEMALE': 0}
        }
    
    # Initialiser les compteurs
    emotion_counts = {}
    emotion_confidence_sums = {}
    total_ages = []
    gender_counts = {'Male': 0, 'Female': 0}
    
    # Analyser chaque visage
    for face in faces_info:
        # Compter les genres
        gender = face['Gender']['Value']
        gender_counts[gender] += 1
        
        # Collecter les âges
        age_range = face['AgeRange']
        total_ages.append((age_range['Low'] + age_range['High']) / 2)
        
        # Agréger les émotions (seulement celles avec une confiance > 50%)
        for emotion in face['Emotions']:
            if emotion['Confidence'] > 30:  # Seuil de confiance significatif
                emotion_type = emotion['Type']
                if emotion_type not in emotion_counts:
                    emotion_counts[emotion_type] = 0
                    emotion_confidence_sums[emotion_type] = 0
                
                emotion_counts[emotion_type] += 1
                emotion_confidence_sums[emotion_type] += emotion['Confidence']
    
    # Calculer les moyennes de confiance pour chaque émotion
    emotion_stats = {
        emotion: {
            'count': count,
            'average_confidence': emotion_confidence_sums[emotion] / count
        }
        for emotion, count in emotion_counts.items()
    }
    
    # Trouver l'émotion dominante (celle avec la plus haute confiance moyenne)
    dominant_emotion = max(
        emotion_stats.items(),
        key=lambda x: x[1]['average_confidence']
    )[0]
    
    # Calculer les statistiques d'âge
    age_stats = {
        'min': min(total_ages),
        'max': max(total_ages),
        'average': sum(total_ages) / len(total_ages)
    }
    
    return {
        'number_of_faces': len(faces_info),
        'dominant_emotion': dominant_emotion,
        'emotion_stats': emotion_stats,
        'age_stats': age_stats,
        'gender_distribution': gender_counts
    }


# <ul style="color:#131fcf">
# <li>Testez la détection et l'analyse d'émotions :
#   <ul>
#     <li>Sur chacune des 4 images de groupe</li>
#     <li>Comparez les résultats entre elles</li>
#   </ul>
# </li>
# <li>Pour chaque image :
#   <ul>
#     <li>Afficher les détails de chaque visage détecté</li>
#     <li>Générer le résumé des statistiques</li>
#     <li>Noter les différences d'émotions dominantes</li>
#   </ul>
# </li>
# </li>
# </ul>
# </span>

# In[41]:


# In[ ]:





# <h4 style="text-align: left; color:#20a08d; font-size: 20px"><span><strong> Fonction de traitement finale
# </strong></span></h4>

# Il est maintenant temps de développer la fonction de traitement finale `process_media` qui se basera sur l'ensemble des fonctions développées précédemment.

# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code de la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">process_media</code> permettant de réaliser l'ensemble des traitements : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#     <li>Déterminer le type de média (vidéo ou image)</li>
#     <li>Si le média est une image : </li>
#     <ul style="text-align: left; font-size: 16px; color:#131fcf">
#         <li>Modérer l'image</li>
#         <li>Si aucun contenu choquant n'est détecté,  détecter les objets, l'émotion dominante des visages et les célébrités présents sur l'image qui serviront de mot-clés pour produire les hashtags</li>
#         <li>Si du contenu choquant est trouvé, retourner <strong>None</strong></li>
#     </ul>
#     <li>Si le média est une vidéo : </li>
#     <ul style="text-align: left; font-size: 16px; color:#131fcf">
#         <li>Extraire la première image de la vidéo</li>
#         <li>Sauvegarder cette image comme fichier temporaire</li>
#         <li>Modérer cette première image</li>
#         <li>Si aucun contenu choquant n'est détecté sur cette image,  convertir la voix présente sur la vidéo en texte</li>
#         <li>Extraire les mots-clés du texte extrait</li>
#         <li>Si du contenu choquant est trouvé, retourner <strong>None</strong></li>
#     </ul>
#     <li>La sortie de cette fonction devra être un dictionnaire et avoir ce format : <strong>{subtitles : "abcdefgijklm", hashtags:["hastag1", "hastag1", ...]}</strong> pour une vidéo et <strong>{hashtags:["hastag1", "hastag1", ...]} pour une image</strong> </li>
# </ul></span></p>

# In[42]:


def process_media(media_file, rekognition, transcribe, comprehend, bucket_name):
    filetype = check_filetype(filename=media_file)
    if filetype == "image":
        moderation_list = moderate_image(image_path=media_file, aws_service=rekognition)
        
        if len(moderation_list) > 0:
            print("[INFO] : Contenu choquant détecté")
            return None
        else:
            objects_list = detect_objects(image_path=media_file, aws_service=rekognition)
            celebrities_list = detect_celebrities(image_path=media_file, aws_service=rekognition)
            faces_info = detect_emotions(image_path=media_file, aws_service=rekognition)
            emotions_stats = summarize_emotions(faces_info)
            
            hashtags = objects_list + celebrities_list + [emotions_stats["dominant_emotion"]]
            
            return {'hashtags':hashtags}
    
    elif filetype == "video":
        frame = extract_frame_video(video_path=media_file, frame_id=1)
        tmp_path = "./tmp.png"
        cv2.imwrite(tmp_path, frame)
        moderation_list = moderate_image(image_path=tmp_path, aws_service=rekognition)

        if len(moderation_list) > 0:
            print("[INFO] : Contenu choquant détecté")
            return None
        else:
            s3.upload_file(media_file, bucket_name,os.path.basename(media_file))

            text_extracted = get_text_from_speech(filename=media_file,
                                                  aws_service=transcribe,
                                                  job_name=f"job_{str(time.time())}",
                                                  bucket_name=bucket_name)
            
            cleaned_text = clean_text(raw_text=text_extracted)
            
            hashtags = extract_keyphrases(text=cleaned_text, aws_service=comprehend)
            
            return {'subtitles':text_extracted, 'hashtags':hashtags}


# <p style="text-align: left; font-size: 16px; color:#131fcf"><span>🖥️  Ecrivez le code permettant de tester la fonction  <strong>process_media</strong>. Pour ce faire : <ul style="text-align: left; font-size: 16px; color:#131fcf">
#         <li>Instancier une session AWS avec vos clés</li>
#     <li>Instancier les services AWS appropriés pour tous les traitements </li>
#     <li>Appelez la fonction <code style="text-align: left; font-size: 16px; color:#131fcf">process_media</code> sur l'image de test et la vidéo de test afin d'en vérifier le bon fonctionnement </li>
#     </ul> </span></p>

# In[49]:


# <h4 style="text-align: left; color:#20a08d; font-size: 25px"><span><strong> Resources 📚📚</strong></span></h4>
# 
# * <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/translate.html" target="_blank">Translate with Boto3</a>
# * <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html#Textract.Client.start_document_text_detection" target="_blank">Textract Documentation</a>
# * <a href="https://aws.amazon.com/textract/" target="_blank">Textract Landing</a>
