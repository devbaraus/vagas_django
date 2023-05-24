import os
import time

import PyPDF2
import nltk
import numpy as np
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode


def process_candidato_tfidf(curriculo, candidato_text):
    try:
        text = get_pdf_text(str(curriculo))
    except:
        text = ""

    text += " " + candidato_text

    text = treat_text(text)
    return text


def process_vaga_tfidf(vaga_text):
    vaga_text = treat_text(vaga_text)

    return vaga_text


def recommend_vagas_tfidf(vagas, user):
    start = time.time()

    user_text = [str(user.curriculo_processado)]
    vagas_text = [str(vaga.vaga_processada) for vaga in vagas]

    query_tfidf, corpus_tfidf = apply_tfidf(user_text, vagas_text)
    cosine_similarities = cosine_similarity(query_tfidf, corpus_tfidf)

    indexes = np.argsort(cosine_similarities[0])[::-1]
    queries = list(np.array(list(vagas))[indexes])

    print(f'tfidf + cosine = {time.time() - start}')

    return queries


def recommend_candidatos_tfidf(candidatos, vaga):
    start = time.time()

    vaga_text = [str(vaga.vaga_processada)]
    candidatos_text = [str(candidato.curriculo_processado) for candidato in candidatos]

    query_tfidf, corpus_tfidf = apply_tfidf(vaga_text, candidatos_text)
    cosine_similarities = cosine_similarity(query_tfidf, corpus_tfidf)

    indexes = np.argsort(cosine_similarities[0])[::-1]
    queries = list(np.array(list(candidatos))[indexes])

    print(f'tfidf + cosine = {time.time() - start}')

    return queries


def get_pdf_text(pdf_path):
    media_path = os.path.join(os.path.dirname(__file__), '../media')
    pdf_path = os.path.join(media_path, pdf_path)

    reader = PyPDF2.PdfReader(pdf_path)
    text = []

    for page in reader.pages:
        text.append(page.extract_text())

    text = " ".join(text)
    text = text.replace('\n', ' ')

    return text


def treat_text(text):
    nltk.download('rslp')
    stemmer = nltk.stem.RSLPStemmer()
    text = text.lower().strip(" ").split(" ")
    text = " ".join([stemmer.stem(word) for word in text if word != ''])
    text = unidecode(str(text))

    return text


def apply_tfidf(query, corpus):
    nltk.download('stopwords')
    stopwords_list = stopwords.words('english') + stopwords.words('portuguese')

    vectorizer = TfidfVectorizer(stop_words=stopwords_list)

    corpus_tfidf = vectorizer.fit_transform(corpus)
    query_tfidf = vectorizer.transform(query)

    return query_tfidf, corpus_tfidf


def load_bert_model(model_name="paraphrase-multilingual-MiniLM-L12-v2"):
    model_path = os.path.join(os.path.dirname(__file__), f'bert_models/{model_name}')

    try:
        model = SentenceTransformer(model_path, device="cpu")
    except ValueError:
        print("Model not found in local directory")
        model = SentenceTransformer(model_name, device="cpu")
        model.save(model_path)
        print(f'Model saved at {model_path}')

    return model


def process_candidato_bert(curriculo, candidato_text):
    model = load_bert_model()

    try:
        text = get_pdf_text(str(curriculo))
    except:
        text = ""

    text += " " + candidato_text

    embedding = model.encode(text, show_progress_bar=False).tolist()

    return embedding


def process_vaga_bert(text):
    model = load_bert_model()

    embedding = model.encode(text, show_progress_bar=False).tolist()

    return embedding


def recommend_vagas_bert(vagas, user):
    start = time.time()

    #If bert embedding isn't created in time, use tfidf instead
    if user.curriculo_embedding is None:
        return recommend_vagas_tfidf(vagas, user)

    user_embedding = [user.curriculo_embedding]
    vagas_embedding = [vaga.vaga_embedding for vaga in vagas]

    cosine_similarities = cosine_similarity(user_embedding, vagas_embedding)

    indexes = np.argsort(cosine_similarities[0])[::-1]
    queries = list(np.array(list(vagas))[indexes])

    print(f'bert + cosine = {time.time() - start}')

    return queries


def recommend_candidatos_bert(candidatos, vaga):
    start = time.time()

    vaga_embedding = [vaga.vaga_embedding]
    candidatos_embedding = [candidato.curriculo_embedding for candidato in candidatos]

    cosine_similarities = cosine_similarity(vaga_embedding, candidatos_embedding)

    indexes = np.argsort(cosine_similarities[0])[::-1]
    queries = list(np.array(list(candidatos))[indexes])

    print(f'bert + cosine = {time.time() - start}')

    return queries


if __name__ == '__main__':
    from django.apps import apps

    Usuario = apps.get_model('emprega.Usuario')
    Vaga = apps.get_model('emprega.Vaga')

    usuarios = Usuario.objects.filter(nivel_usuario=4)
    vagas = Vaga.objects.all()
    usuario = Usuario.objects.get(cpf="13673179675")
    vaga = Vaga.objects.get(pk=1)

    vagas_rec = recommend_vagas_bert(vagas, usuario)
    candidatos_rec = recommend_candidatos_bert(usuarios, vaga)

    print(vagas_rec, candidatos_rec)
