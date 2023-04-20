python manage.py seed_candidatos 1 --formacao 1~5 --experiencia 1~5 --curso 1~5 --idioma 1~5
python manage.py seed_candidatos 1 --formacao_input fixtures/formacoes_academicas.json --experiencia_input fixtures/experiencia_profissional.json --curso_input fixtures/cursos_especializacoes.json --idioma_input fixtures/idiomas.json
python manage.py seed_empregadores 1 --vagas 1~5
python manage.py seed_empregadores 1 --vagas 1~5 --vagas_input fixtures/vagas.json