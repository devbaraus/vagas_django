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

def recommend(query, user):
    pdf_path = user.curriculo

    ## can be done before
    start = time.time()
    pdf_text = get_pdf_text(pdf_path)
    vagas_text = get_vagas_text(query)
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
    queries = list(np.array(list(query))[indexes])
    print(f'tfidf + cosine = {time.time() - start}')

    return queries

def get_pdf_text(pdf_path):

    reader = PyPDF2.PdfReader(pdf_path)
    text = []

    for page in reader.pages:
        text.append(page.extract_text())

    text = " ".join(text)

    print(f'{reader.metadata.title =}')
    return text

def get_vagas_text(query):
    vagas_text = []
    for vaga in query:
        cargo = vaga.cargo
        atividades = vaga.atividades
        requisitos = vaga.requisitos
        empresa = vaga.empresa
        ramo_empresa = empresa.ramo_atividade
        descricao_empresa = empresa.descricao

        vagas_text.append(" ".join([cargo, atividades, requisitos, ramo_empresa, descricao_empresa]).replace("\n", " "))

    return vagas_text

def treat_text(texts):
    nltk.download('rslp')
    stemmer = nltk.stem.RSLPStemmer()
    treated = []
    if type(texts) == str:
        texts = [texts]

    for text in texts:
        text = text.lower().split(" ")
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