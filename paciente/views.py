from django.shortcuts import render, redirect
from django.http import HttpResponse
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from datetime import datetime, timedelta
from .models import Consulta, Documento
from django.contrib.messages import constants, add_message

def home(request):
    if not request.user.username:
        return redirect('/usuarios/login')

    if request.method == 'GET':
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedico.objects.all() 
        consultas = Consulta.objects.filter(paciente=request.user)

        datas = consultas.filter(data_aberta__data__gte=datetime.now())

        dias_faltando = []
        for data in datas:
            dias_faltando.append((data.data_aberta.data - timedelta(days=(datetime.now().day))).day)

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)

        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)

        especialidades = Especialidades.objects.all()

        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user), 'consultas': consultas, 'dias_faltando': dias_faltando})
    
def escolher_horario(request, id_dados_medicos):
    if not request.user.username:
        return redirect('/usuarios/login')

    if request.method == 'GET':
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now())

        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})

def agendar_horario(request, id_data_aberta):
    if not request.user.username:
        return redirect('/usuarios/login')

    if request.method == 'GET':
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        
        horario_agendado = Consulta(
            paciente = request.user,
            data_aberta = data_aberta,

        )

        horario_agendado.save()

        data_aberta.agendado = True
        data_aberta.save()

        add_message(request, constants.SUCCESS, 'Consulta agendada com sucesso')
        return redirect('/pacientes/minhas_consultas')
    
def minhas_consultas(request):
    if not request.user.username:
        return redirect('/usuarios/login')

    if request.method == "GET":
        especialidades_filtro = request.GET.get('especialidades')
        data = request.GET.get('data')
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        
        if data:
            data_formatada = datetime.strptime(data, '%Y-%m-%d')
            minhas_consultas = minhas_consultas.filter(data_aberta__data__gte=data_formatada)

        if especialidades_filtro:
            minhas_consultas = minhas_consultas.filter(data_aberta__user__dadosmedico__especialidade_id=especialidades_filtro)

        especialidades = Especialidades.objects.all
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico': is_medico(request.user), 'especialidades': especialidades})
    
def consulta(request, id_consulta):
    if not request.user.username:
        return redirect('/usuarios/login')
    
    if request.method == 'GET':
        consulta =  Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta=consulta)

        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'documentos': documentos})
    
def cancelar_consulta_paciente(request, id_consulta):
    if not request.user.username:
        return redirect('/usuarios/login')

    consulta = Consulta.objects.get(id=id_consulta)

    if request.user.id != consulta.paciente.id:
        add_message(request, constants.ERROR, 'Esta consulta não pertence a você!')
        return redirect(f'/pacientes/consulta/{id_consulta}/')
    
    consulta.status = 'C'
    consulta.save()
    
    return redirect(f"/pacientes/consulta/{id_consulta}/")
    