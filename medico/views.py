from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.contrib.messages import constants, add_message
from datetime import datetime, timedelta
from paciente.models import Consulta


def cadastro_medico(request):
    if is_medico(request.user):
        add_message(request, constants.WARNING, 'Você já está cadastrado!')
        return redirect('/medicos/abrir_horario')

    if request.method == 'GET':
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades})
    elif request.method == 'POST':
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        dados_medico = DadosMedico(
            crm = crm,
            nome = nome,
            cep = cep,
            rua = rua,
            bairro = bairro,
            numero = numero,
            cedula_identidade_medica = cim,
            rg = rg,
            foto = foto,
            especialidade_id = especialidade,
            descricao = descricao,
            valor_consulta = valor_consulta,
            user = request.user
        )

        dados_medico.save()

        add_message(request, constants.SUCCESS, "O Cadastro Médico foi realizado com sucesso!")
        return redirect('/medicos/abrir_horario')

def abrir_horario(request):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem acessar o agendamento')
        return redirect('/usuarios/logout')
    
    if request.method == 'GET':
        dados_medico = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medico': dados_medico, 'datas_abertas': datas_abertas})
    elif request.method == 'POST':
        data = request.POST.get('data')

        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        if data_formatada <= datetime.now():
            add_message(request, constants.WARNING, 'A data não pode ser anterior a data atual!')
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user,
        )
        
        horario_abrir.save()

        add_message(request, constants.SUCCESS, 'O horário foi cadastradado com sucesso!')
        return redirect('/medicos/abrir_horario')

def consultas_medico(request):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    hoje = datetime.now().date()

    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id'))

    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        return render(request, 'consulta_area_medico.html', {'consulta': consulta})
    
    if request.method == 'POST':
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        if consulta.status == 'C':
            add_message(request, constants.WARNING, 'Esta consulta foi cancelada!')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')
        elif consulta.status == 'F':
            add_message(request, constants.WARNING, 'Esta consulta já foi finalizada!')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')

        consulta.link = link
        consulta.status = 'I'

        consulta.save()

        add_message(request, constants.SUCCESS, 'Consulta Inicializada')

        return redirect(f'/medicos/consulta_area_medico/{id_consulta}/')