from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from .forms import *
import logging

@login_required
def home_view(request):

	if request.headers.get('x-spa-request') == 'true': 
		html = render_to_string(f'a_home/partials/home_p.html', request=request)
		return JsonResponse({
			'html': html,
			'target': 'spa-content',  # ID de l'élément cible
		})

	return render(request, 'a_home/home.html')

@login_required
def create_lobby(request):
	form = LobbyCreateForm()

	if request.method == 'POST':
		form = LobbyCreateForm(request.POST)
		if form.is_valid():
			new_lobby = form.save(commit=False)
			new_lobby.admin = request.user
			new_lobby.save()
			new_lobby.members.add(request.user)
			logger = logging.getLogger("mylogger")
			logger.info(new_lobby.lobby_id)
			logger.info(new_lobby.members.all())
			# Si la requête est SPA, appeler la vue du lobby
			return JsonResponse({
				'redirect_url': reverse('lobby', args=[new_lobby.lobby_id])
			})
	
	context = {
		'form': form,
	}

	if request.headers.get('x-spa-request') == 'true': 
		# Génère le HTML du formulaire à envoyer dans la réponse JSON
		html = render_to_string(f'a_home/partials/lobby_create_p.html', context, request=request)

		# Extraire seulement les erreurs du formulaire s'il y en a
		form_errors = {field.name: field.errors for field in form}

		return JsonResponse({
			'html': html,
			'target': 'spa-content',  # ID de l'élément cible
			'form_errors': form_errors  # Ajouter les erreurs du formulaire
		})

	return render(request, 'a_home/lobby_create.html', context)


@login_required
def lobby_view(request, lobby_id):
	form = ChatmessageCreateForm()

	lobby = get_object_or_404(Lobby, lobby_id=lobby_id)
	players = lobby.members.all()  # Ou une liste personnalisée
	lobby_messages = lobby.lobby_messages.all()[:30]


	if request.user not in lobby.members.all():
		if lobby.is_full():
			messages.warning(request, 'lobby is full')
			return redirect('home')


	if request.headers.get("X-Requested-With") == "XMLHttpRequest":  # verify if the request come from ajax
		form = ChatmessageCreateForm(request.POST)
		if form.is_valid():
			message = form.save(commit=False)
			message.author = request.user
			message.lobby = lobby
			message.save()
			context = {
				'message': message,
				'user': request.user
			}
			# rendering partial for dynamique insertion
			return render(request, 'a_home/partials/chat_message_p.html', context)


	context = {
		'player_1': players[0] if len(players) > 0 else None,
		'player_2': players[1] if len(players) > 1 else None,
		'lobby': lobby,
		'user': request.user,
		'form': form,
		'lobby_messages': lobby_messages,
	}
	
	if request.user not in lobby.members.all():
		lobby.members.add(request.user)

	if request.headers.get('x-spa-request') == 'true': 
		html = render_to_string(f'a_home/partials/lobby_p.html', request=request, context=context)
		return JsonResponse({
			'html': html,
			'target': 'spa-content',  # ID de l'élément cible
		})


	return render(request, 'a_home/lobby.html', context)

@login_required
def join_lobby(request):
	lobby_list = Lobby.objects.filter(is_private=False)
	context = {
		'lobbys': lobby_list,
		'user': request.user,
	}

	if request.headers.get('x-spa-request') == 'true': 
		html = render_to_string(f'a_home/partials/lobby_join_p.html' , context, request=request)
		return JsonResponse({
			'html': html,
			'target': 'spa-content',  # ID de l'élément cible
		})

	if request.headers.get("X-Requested-With") == "XMLHttpRequest":  # verify if the request come from ajax
		# potentielement la repetion est inutile ici
		context = {
			'lobbys': lobby_list,
			'user': request.user,
		}
		html = render(request, 'a_home/partials/lobby_list.html', context).content.decode('utf-8')
		return JsonResponse({'html': html})



	return render(request, 'a_home/lobby_join.html', context)
