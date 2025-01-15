import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
from pymongo import MongoClient

# NLTK'den stopwords listesini indirme
nltk.download('stopwords')
nltk.download('punkt')

# MongoDB bağlantısı
client = MongoClient('mongodb://localhost:27017/')
db = client['Yazlab2_3']  
collection = db['articles']  

# stopwords listesini yükleme
stop_words = set(stopwords.words('english'))

# Kök bulma için stemmer'ı yaratma
ps = PorterStemmer()

# Makalelerin bulunduğu klasör
folder_path = "C:/Users/hilal/Desktop/Yazlab2_3/database/all_docs_abstacts_refined/"

# Tüm dosyaları gezme
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        key_path = os.path.join(folder_path, filename.replace('.txt', '.key'))
        
        if os.path.exists(key_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                print("Read file:", filename)
                # Noktalama işaretlerini kaldırma
                text = text.translate(str.maketrans('', '', string.punctuation))
                # Küçük harfe dönüştürme
                text = text.lower()
                # Kelimeleri tokenize etme
                words = word_tokenize(text)
                # Stopwords'leri ve sayıları temizleme
                words = [word for word in words if word not in stop_words and not word.isdigit()]
                # Kelime köklerini bulma
                stemmed_words = [ps.stem(word) for word in words]
                
                # Metni birleştirme
                cleaned_text = ' '.join(stemmed_words)

                with open(key_path, 'r', encoding='utf-8') as key_file:
                    keys = key_file.read()
                    keys = keys.lower()  # Anahtar kelimeleri küçük harfe dönüştürme
                    keys = keys.split('\n')  # Anahtar kelimeleri ayırma

                    # Metni ve anahtar kelimeleri MongoDB'ye kaydetme
                    article = {
                        'filename': filename,
                        'cleaned_text': cleaned_text,  # Metni tek bir string olarak ekleyin
                        'keys': keys
                    }
                    try:
                        collection.insert_one(article)
                        print("Inserted article:", filename)
                    except Exception as e:
                        print("Error inserting article:", e)
        else:
            print(f"No key file found for {filename}. Skipping...")
