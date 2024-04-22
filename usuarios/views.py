from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth

def cadastrar(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas devem ser iguais')
            return redirect('/usuarios/cadastro/')

        if len(senha) < 6:
            messages.add_message(request, constants.ERROR, 'A senhas deve possuir pelo menos 6 caracteres')
            return redirect('/usuarios/cadastro/')
        
        users = User.objects.filter(username=username)

        if users.exists():
            messages.add_message(request, constants.ERROR, 'O usuário já existe')
            return redirect('/usuarios/cadastro/')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=senha
        )

        return redirect('/usuarios/login/')
    
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            return redirect('/pacientes/home')
        
        messages.add_message(request, constants.ERROR, 'O Usuário ou senha estão incorretos')
        return render(request, 'login.html')
    
def logout(request):
    print(request.user) # ver qual é o usuário logado
    print(request.user.is_authenticated) # conferir se tem algum usuário logado
    print(request.user.email) # conferir o email do usuario

    auth.logout(request)
    return redirect('/usuarios/login')