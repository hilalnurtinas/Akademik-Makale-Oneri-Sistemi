

import numpy as np
import torch
import fasttext
from transformers import AutoTokenizer, AutoModel
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity

# MongoDB bağlantısı
client = MongoClient('mongodb://localhost:27017/')
db = client['Yazlab2_3']  
collection = db['articles']  
collection2 = db['articles_embeddings']  # Vektör temsillerini 
collection3 = db['articles_vectors']

def runOnce():

    # Scibert modeli ve tokenizer'ını yükleme
    scibert_model_name = "allenai/scibert_scivocab_uncased"
    scibert_tokenizer = AutoTokenizer.from_pretrained(scibert_model_name)
    scibert_model = AutoModel.from_pretrained(scibert_model_name)

    # FastText modelini yükleme
    fasttext_model_path = "cc.en.300.bin"
    fasttext_model = fasttext.load_model(fasttext_model_path)

    # Tüm makaleleri MongoDB'den çekme
    all_articles = list(collection.find())

    # Scibert ve FastText vektör temsillerini oluşturma
    scibert_embeddings = []
    fasttext_embeddings = []
    filenames = []
    i = 0
    for article in all_articles:
        cleaned_text = article['cleaned_text']
        filenames.append(article['filename'])
        i += 1
        print(i)
        # Scibert vektör temsilini oluşturun
        inputs = scibert_tokenizer(cleaned_text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = scibert_model(**inputs)
            scibert_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        scibert_embeddings.append(scibert_embedding)

        # FastText vektör temsilini oluşturun
        words = cleaned_text.split()
        fasttext_embedding = np.zeros(300)  # FastText vektör boyutu

        count = 0
        for word in words:
            if word.strip():
                fasttext_embedding += fasttext_model.get_word_vector(word.strip())
                count += 1
        if count > 0:
            fasttext_embedding /= count  # Ortalama vektörü hesaplayın
        fasttext_embeddings.append(fasttext_embedding)

        embedding_document = {
            'filename': article['filename'],
            'scibert_embedding': scibert_embedding.tolist(),  # numpy array'ini listeye dönüştür
            'fasttext_embedding': fasttext_embedding.tolist()  # numpy array'ini listeye dönüştür
        }
        collection3.insert_one(embedding_document)




def getScribertEmbedings(filename):
    # Veritabanından tüm vektörleri çekme
    all_embeddings = list(collection3.find())
    referanceEmbeddings = list(collection3.find({'filename': filename}))

    if not referanceEmbeddings:
        return [], []

    # Referans vektör belirleme
    reference_scibert_vector = referanceEmbeddings[0]['scibert_embedding']
    reference_fasttext_vector = referanceEmbeddings[0]['fasttext_embedding']

    # Kosinüs benzerliği ile vektörler arasındaki benzerliği hesaplama
    scibert_similarities = [cosine_similarity([reference_scibert_vector], [emb['scibert_embedding']])[0][0] for emb in all_embeddings]
    fasttext_similarities = [cosine_similarity([reference_fasttext_vector], [emb['fasttext_embedding']])[0][0] for emb in all_embeddings]

    # Benzerlikleri MongoDB'ye kaydetme
    for idx, emb in enumerate(all_embeddings):
        scibert_similarity = float(scibert_similarities[idx])
        fasttext_similarity = float(fasttext_similarities[idx])
        
        collection2.update_one(
            {"filename": emb['filename']},
            {"$set": {"scibert_similarity": scibert_similarity, "fasttext_similarity": fasttext_similarity}},
            upsert=True
        )

    # MongoDB'den benzerlik oranlarını çekme ve sıralama
    all_embeddings = list(collection2.find({"filename": {"$ne": filename}}))  # Tıklanan makaleyi dışla
    all_embeddings.sort(key=lambda x: x['scibert_similarity'], reverse=True)
    top_5_scibert = all_embeddings[:5]

    all_embeddings.sort(key=lambda x: x['fasttext_similarity'], reverse=True)
    top_5_fasttext = all_embeddings[:5]

        # En benzer ilk 5 makaleyi yazdırma
    print("Top 5 Similar Articles based on Scibert:")
    for article in top_5_scibert:
        print(f"Article: {article['filename']} - Scibert Similarity: {article['scibert_similarity']:.4f}")

    print("\nTop 5 Similar Articles based on FastText:")
    for article in top_5_fasttext:
        print(f"Article: {article['filename']} - FastText Similarity: {article['fasttext_similarity']:.4f}")
    


    return top_5_scibert, top_5_fasttext


# runOnce() fonksiyonunu sadece bir kez çalıştırarak vektör temsillerini veritabanına kaydet
# runOnce()

# getScribertEmbedings fonksiyonunu çağırarak benzerlikleri hesapla ve yazdır
#getScribertEmbedings('1005397.txt')