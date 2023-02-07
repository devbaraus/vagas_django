import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import numpy as np
import time
from emprega.models import (
    Empresa,
    Vaga,
    Candidato,
    Usuario,
)

def recommend_vagas(vagas, user):
    pdf_path = user.curriculo
     
    ## can be done before
    start = time.time()
    pdf_text = get_pdf_text(pdf_path)
    vagas_text = []
    for vaga in vagas:
        vagas_text.append(get_vaga_text(vaga))
    print(f'getting text = {time.time() - start}')

    ## can be done before
    start = time.time()
    pdf_text = treat_text(pdf_text)
    vagas_text = treat_text(vagas_text)
    print(f'treating text = {time.time() - start}')

    start = time.time()
    query_tfidf, corpus_tfidf = apply_tfidf(pdf_text, vagas_text)
    cosine_similarities = cosine_similarity(query_tfidf, corpus_tfidf)

    indexes = np.argsort(cosine_similarities[0])[::-1]
    queries = list(np.array(list(vagas))[indexes])
    print(f'tfidf + cosine = {time.time() - start}')

    return queries

def recommend_candidatos(candidatos, user):
    own_vagas = Vaga.objects.filter(empresa=user.empresa)
    print(own_vagas)

    start = time.time()

    query_text = ""
    for vaga in own_vagas:
        query_text += " " + get_vaga_text(vaga)

    candidatos_text = []
    for candidato in candidatos:
        candidatos_text.append(get_candidato_text(candidato))
    print(f'getting text = {time.time() - start}')

    ## can be done before
    start = time.time()
    query_text = treat_text(query_text)
    candidatos_text = treat_text(candidatos_text)
    print(f'treating text = {time.time() - start}')

    start = time.time()
    query_tfidf, corpus_tfidf = apply_tfidf(query_text, candidatos_text)
    cosine_similarities = cosine_similarity(query_tfidf, corpus_tfidf)

    indexes = np.argsort(cosine_similarities[0])[::-1]
    queries = list(np.array(list(candidatos))[indexes])
    print(f'tfidf + cosine = {time.time() - start}')

    return queries

def get_candidato_text(candidato):
    candidato_text = ""
    pdf_path = candidato.curriculo
    candidato_text += " " + get_pdf_text(pdf_path)

    return candidato_text

def get_pdf_text(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    text = []

    for page in reader.pages:
        text.append(page.extract_text())

    text = " ".join(text)

    return text

def get_vaga_text(vaga):
    cargo = vaga.cargo
    atividades = vaga.atividades
    requisitos = vaga.requisitos
    empresa = vaga.empresa
    ramo_empresa = empresa.ramo_atividade
    descricao_empresa = empresa.descricao

    return " ".join([cargo, atividades, requisitos, ramo_empresa, descricao_empresa]).replace("\n", " ")

def treat_text(texts):
    nltk.download('rslp')
    stemmer = nltk.stem.RSLPStemmer()
    treated = []
    if type(texts) == str:
        texts = [texts]

    for text in texts:
        text = text.lower().strip(" ").split(" ")
        text = " ".join([stemmer.stem(word) for word in text if word != ''])
        treated.append(text)

    return treated

def apply_tfidf(query, corpus):
    nltk.download('stopwords')
    stopwords_list = stopwords.words('english') + stopwords.words('portuguese')

    vectorizer = TfidfVectorizer(stop_words=stopwords_list)

    corpus_tfidf = vectorizer.fit_transform(corpus)
    query_tfidf = vectorizer.transform(query)

    return query_tfidf, corpus_tfidf