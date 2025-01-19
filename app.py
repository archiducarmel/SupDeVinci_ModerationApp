import streamlit as st
import cv2
import boto3 
import tempfile
import os
from dotenv import load_dotenv
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import json

# Import des fonctions de moderation.py
from moderation import (
    process_media,
    check_filetype, 
    extract_frame_video,
    moderate_image
)

# Télécharger les ressources NLTK nécessaires
nltk.download('stopwords')

# Configuration de la page
st.set_page_config(
    page_title="📸 Content Moderator Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 0.5rem;
            border-radius: 0.5rem;
            border: none;
            margin: 0.5rem 0;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .social-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        .social-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .social-profile {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e0e0e0;
            margin-right: 10px;
        }
        .social-username {
            font-weight: bold;
            color: #1DA1F2;
        }
        .social-timestamp {
            color: #657786;
            font-size: 0.9em;
        }
        .hashtag {
            display: inline-block;
            padding: 5px 10px;
            background: #E8F5FE;
            color: #1DA1F2;
            border-radius: 15px;
            margin: 5px;
            font-size: 0.9em;
        }
        .moderation-alert {
            background: #FDE8E8;
            border: 2px solid #F56565;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
        .prohibited-content {
            text-align: center;
            padding: 40px;
            background: #FDE8E8;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

def get_aws_session(access_key, secret_key):
    """Configure la session AWS avec les clés d'accès."""
    aws_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1"
    )
    return aws_session

def initialize_services(aws_session):
    """Initialise tous les services AWS nécessaires."""
    return {
        'rekognition': aws_session.client('rekognition'),
        'transcribe': aws_session.client('transcribe'),
        'comprehend': aws_session.client('comprehend'),
        's3': aws_session.client('s3')
    }

def create_bucket_if_not_exists(s3_client, bucket_name):
    """Crée un bucket S3 s'il n'existe pas déjà."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except:
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            st.sidebar.success(f"✅ Bucket {bucket_name} créé avec succès!")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur lors de la création du bucket: {str(e)}")

def load_env_credentials():
    """Charge les credentials depuis le fichier .env"""
    try:
        load_dotenv()
        access_key = os.getenv("ACCESS_KEY")
        secret_key = os.getenv("SECRET_KEY")
        if access_key and secret_key:
            return access_key, secret_key
        else:
            return None, None
    except Exception as e:
        st.sidebar.error(f"❌ Erreur lors du chargement des credentials: {str(e)}")
        return None, None

def sidebar_config():
    """Configure la barre latérale avec les paramètres."""
    st.sidebar.title("⚙️ Configuration")
    
    # AWS Credentials
    st.sidebar.subheader("🔑 Credentials AWS")
    
    if st.sidebar.button("📂 Charger credentials depuis .env"):
        env_access_key, env_secret_key = load_env_credentials()
        if env_access_key and env_secret_key:
            st.session_state['access_key'] = env_access_key
            st.session_state['secret_key'] = env_secret_key
            st.sidebar.success("✅ Credentials chargés avec succès!")
        else:
            st.sidebar.error("❌ Aucun credential trouvé dans .env")
    
    access_key = st.sidebar.text_input(
        "Access Key",
        value=st.session_state.get('access_key', ''),
        type="password"
    )
    secret_key = st.sidebar.text_input(
        "Secret Key",
        value=st.session_state.get('secret_key', ''),
        type="password"
    )
    bucket_name = st.sidebar.text_input("Nom du bucket S3", "test-bucket-sdvnantes-2")
    
    return {
        'access_key': access_key,
        'secret_key': secret_key,
        'bucket_name': bucket_name
    }

def display_social_card(file_path, results=None, moderation_results=None):
    """Affiche une carte style réseau social avec l'image/vidéo et les résultats."""
    st.markdown("""
        <div class="social-card">
            <div class="social-header">
                <div class="social-profile"></div>
                <div>
                    <div class="social-username">Content Moderator Pro</div>
                    <div class="social-timestamp">il y a quelques secondes</div>
                </div>
            </div>
    """, unsafe_allow_html=True)

    if moderation_results:
        st.markdown("""
            <div class="prohibited-content">
                <h2>🚫 Contenu inapproprié détecté</h2>
                <p style="color: #DC2626; font-size: 1.2em;">Cette publication a été bloquée</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.error("Thèmes sensibles détectés :")
        for theme in moderation_results:
            st.markdown(f"⚠️ {theme}")
            
    else:
        if file_path and os.path.exists(file_path):
            try:
                file_type = check_filetype(file_path)
                
                if file_type == "image":
                    from PIL import Image
                    img = Image.open(file_path)
                    st.image(img, use_container_width=True)
                
                elif file_type == "video":
                    video_file = open(file_path, 'rb')
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                    video_file.close()
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage du média : {str(e)}")
        elif file_path:
            st.error("Le fichier média n'existe pas")
            
        if results:
            if 'hashtags' in results:
                st.markdown("<div style='margin: 15px 0;'>", unsafe_allow_html=True)
                hashtags_html = " ".join([f"<span class='hashtag'>#{tag}</span>" for tag in results['hashtags']])
                st.markdown(hashtags_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            if 'subtitles' in results and file_type == "video":
                with st.expander("📝 Voir la transcription"):
                    st.markdown(f"""
                        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-top: 10px;'>
                            {results['subtitles']}
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def display_results(results, file_type, file_path=None, moderation_list=None):
    """Affiche les résultats de l'analyse avec un style réseau social."""
    if file_path:
        display_social_card(
            file_path=file_path,
            results=results if results is not None else None,
            moderation_results=moderation_list
        )

def resize_image_if_needed(image_path, max_size_mb=4):
    """Redimensionne l'image si elle dépasse la taille maximale autorisée."""
    file_size = os.path.getsize(image_path) / (1024 * 1024)
    
    if file_size <= max_size_mb:
        return image_path
        
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de charger l'image: {image_path}")
    
    ratio = (max_size_mb * 1024 * 1024 / os.path.getsize(image_path)) ** 0.5
    new_width = int(image.shape[1] * ratio)
    new_height = int(image.shape[0] * ratio)
    
    resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    output_path = os.path.splitext(image_path)[0] + '_resized.jpg'
    cv2.imwrite(output_path, resized, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    return output_path

def process_uploaded_file(file_path, services, bucket_name):
    """Traite un fichier uploadé avec redimensionnement si nécessaire."""
    try:
        file_type = check_filetype(file_path)
        moderation_list = None
        
        if file_type == "image":
            processed_path = resize_image_if_needed(file_path)
            moderation_list = moderate_image(processed_path, services['rekognition'])
            
        elif file_type == "video":
            frame = extract_frame_video(file_path, frame_id=1)
            if frame is None:
                raise ValueError("Impossible d'extraire une frame de la vidéo")
                
            tmp_frame_path = os.path.join(tempfile.gettempdir(), "frame_to_moderate.jpg")
            cv2.imwrite(tmp_frame_path, frame)
            
            moderation_list = moderate_image(tmp_frame_path, services['rekognition'])
            os.unlink(tmp_frame_path)
        
        results = None
        if not moderation_list:
            results = process_media(
                file_path,
                services['rekognition'],
                services['transcribe'],
                services['comprehend'],
                bucket_name
            )
            
        if file_type == "image" and processed_path != file_path:
            os.unlink(processed_path)
            
        return results, moderation_list
            
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

def main():
    """Fonction principale de l'application."""
    if 'access_key' not in st.session_state:
        st.session_state['access_key'] = ''
    if 'secret_key' not in st.session_state:
        st.session_state['secret_key'] = ''
        
    st.title("📸 Content Moderator Pro")
    st.markdown("### 🔍 Analysez et modérez votre contenu en un clic!")
    
    config = sidebar_config()
    
    if not (config['access_key'] and config['secret_key']):
        st.warning("⚠️ Veuillez configurer vos credentials AWS dans la barre latérale")
        return
        
    aws_session = get_aws_session(config['access_key'], config['secret_key'])
    services = initialize_services(aws_session)
    create_bucket_if_not_exists(services['s3'], config['bucket_name'])
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier (image ou vidéo)",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi']
    )
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name
        
        with st.spinner("🔄 Analyse en cours..."):
            results, moderation_list = process_uploaded_file(
                file_path,
                services,
                config['bucket_name']
            )
            
            display_results(
                results,
                "image" if uploaded_file.type.startswith("image") else "video",
                file_path=file_path,
                moderation_list=moderation_list
            )
        
        os.unlink(file_path)

if __name__ == "__main__":
    main()