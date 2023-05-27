from celery import shared_task
from django.apps import apps
from recomendacao.recommendation import process_candidato_tfidf, process_candidato_bert, process_vaga_tfidf, process_vaga_bert

@shared_task(name='process_candidato')
def process_candidato(pk):
    Candidato = apps.get_model('emprega.Candidato')
    FormacaoAcademica = apps.get_model('emprega.FormacaoAcademica')
    ExperienciaProfissional = apps.get_model('emprega.ExperienciaProfissional')
    CursoEspecializacao = apps.get_model('emprega.CursoEspecializacao')
    Idioma = apps.get_model('emprega.Idioma')

    candidato = Candidato.objects.get(pk=pk)

    educations = FormacaoAcademica.objects.filter(usuario=candidato)
    educations =  " ".join([str(education) for education in educations])

    experiences = ExperienciaProfissional.objects.filter(usuario=candidato)
    experiences = " ".join([f'{str(experience)} {experience.atividades}' for experience in experiences])

    courses = CursoEspecializacao.objects.filter(usuario=candidato)
    courses = " ".join([str(course) for course in courses])

    languages = Idioma.objects.filter(usuario=candidato)
    languages = " ".join([str(language) for language in languages])

    candidato_text = " ".join([educations, experiences, courses, languages])

    processed_text = process_candidato_tfidf(candidato.curriculo, candidato_text)

    candidato.curriculo_processado = processed_text

    #save the processed_text to use in case the embedding doesn't get processed in time
    candidato.save(process = False)

    embedding = process_candidato_bert(candidato.curriculo, candidato_text)
    candidato.curriculo_embedding = embedding

    print(f'Candidato {candidato} - {candidato.pk} processado')

    candidato.save(process = False)


@shared_task(name='process_vaga')
def process_vaga(pk):
    Vaga = apps.get_model('emprega.Vaga')

    vaga = Vaga.objects.get(pk = pk)
    empresa = vaga.empresa
    vaga_text = " ".join([vaga.cargo, vaga.atividades, vaga.esta_ativo, vaga.requisitos, empresa.ramo_atividade, empresa.descricao])

    processed_text = process_vaga_tfidf(vaga_text)
    vaga.vaga_processada = processed_text

    embedding = process_vaga_bert(vaga_text)
    vaga.vaga_embedding = embedding

    print(f'Vaga {vaga} - {vaga.pk} processada')

    vaga.save(process = False)
