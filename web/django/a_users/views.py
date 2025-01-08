from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.conf import settings
from .forms import *
from .models import Relation
from django.db.models import Q # For search user with query

# Auth import :
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
from io import BytesIO
from base64 import b64encode
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
import hvac

vault_client = settings.VAULT_CLIENT

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			email = form.cleaned_data['email']

		if User.objects.filter(username=username).exists():
			messages.error(request, 'User already exists')
			return render(request, 'register.html', {'form': form})
		if User.objects.filter(email=email).exists():
			messages.error(request, 'Email already used')
			return render(request, 'register.html', {'form': form})

		user = User.objects.create_user(username=username, email=email)
		user.set_unusable_password() # On ne stocke pas le mdp en bdd simple.
		user.save()

		# Stocker le mot de passe dans Vault
		try:
			vault_client.secrets.kv.v2.create_or_update_secret(
				path=f'users/{username}',
				secret={'password': password},
				mount_point='kv'
			)
		except hvac.exceptions.Forbidden as e:
			error_message = f'Permission denied: cannot store password in Vault. Details: {str(e)}'
			messages.error(request, error_message)
			user.delete()  # Supprime l'utilisateur créé si le stockage du mot de passe échoue
			return render(request, 'register.html', {'form': form})
		except hvac.exceptions.InvalidPath as e:
			error_message = f'Invalid path: cannot store password in Vault. Details: {str(e)}'
			messages.error(request, error_message)
			user.delete()  # Supprime l'utilisateur créé si le stockage du mot de passe échoue
			return render(request, 'register.html', {'form': form})

		return redirect('login')

	else:
		form = RegisterForm()

	return render(request, 'register.html', {'form': form})

def get_tokens_for_user(user):
	refresh = RefreshToken.for_user(user)
	return {
		'refresh': str(refresh),
		'access': str(refresh.access_token),
	}

@login_required
@api_view(['GET'])
def jwt_exchange(request):
    tokens = get_tokens_for_user(request.user)
    response = redirect('/')
    response.set_cookie('access_token', tokens['access'])
    response.set_cookie('refresh_token', tokens['refresh'])
    return response

def logout_view(request):

	if request.method == 'POST':

		choice = request.POST.get('choice')

		if choice == 'yes':
			logout(request)

			response = redirect('login')
			response.delete_cookie('access_token')
			response.delete_cookie('refresh_token')

			return response

		elif choice == 'no':
			return redirect('/')

	return render(request, 'confirm_logout.html')

# After login

def profile_view(request, username=None):
	if username:
		profile = get_object_or_404(User, username=username).profile
	else:
		try:
			profile = request.user.profile
		except:
			return redirect_to_login(request.get_full_path())
	return render(request, 'a_users/profile.html', {'profile':profile})


@login_required
def profile_edit_view(request):
	form = ProfileForm(instance=request.user.profile)  
	
	if request.method == 'POST':
		form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if form.is_valid():
			form.save()
			return redirect('profile')
		
	if request.path == reverse('profile-onboarding'):
		onboarding = True
	else:
		onboarding = False
	
	return render(request, 'a_users/profile_edit.html', { 'form':form, 'onboarding':onboarding })


@login_required
def profile_settings_view(request):
	totp_device = TOTPDevice.objects.filter(user=request.user).first()

	default_device = totp_device is not None

	return render(request, 'a_users/profile_settings.html', {'default_device': default_device})


@login_required
def profile_emailchange(request):
	
	if request.method == 'POST':
		form = EmailForm(request.POST, instance=request.user)
		
		if form.is_valid():
			email = form.cleaned_data['email']
			form.save()
			messages.success(request, 'Email updated successfully!')
			return redirect('profile-settings')  # redirection après mise à jour réussie
		else:
			messages.error(request, 'Please correct the error below.')

	else:
		form = EmailForm(instance=request.user)

	# Si requête AJAX, retourne le formulaire partiel seulement
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return render(request, 'partials/email_form.html', {'form': form})
	else:
		return redirect('profile-settings')


@login_required
def profile_emailverify(request):
	send_email_confirmation(request, request.user)
	return redirect('profile-settings')


@login_required
def profile_delete_view(request):
	user = request.user
	if request.method == "POST":
		logout(request)
		user.delete()
		messages.success(request, 'Account deleted, what a pity')
		return redirect('user_logout')
	
	return render(request, 'a_users/profile_delete.html')

### 2FA part

def login_2fa(request):
	step = "part1"
	if request.method == "POST":

		if "username" in request.POST and "password" in request.POST:

			username = request.POST.get('username')
			password = request.POST.get('password')

			#recuperation du mot de passe depuis Vault
			try:
				stored_password = vault_client.secrets.kv.read_secret_version(path=f'users/{username}',mount_point='kv')['data']['data']['password']
			except Exception as e:
				error_message = f'Error retrieving password from Vault. Details: {str(e)}'
				messages.error(request, error_message)
				return render(request, 'a_two_factor/login.html', {'step':step})

			if password == stored_password:
				user = User.objects.get(username=username)
				try:
					device = TOTPDevice.objects.get(user=user, confirmed=True)
				except TOTPDevice.DoesNotExist:
					login(request, user)
					return redirect('/')
				
				step = "part2"
				request.session["temp_user_id"] = user.id
				return render(request, 'a_two_factor/login.html', {'step':step})
			else:
				messages.error(request, 'Wrong credentials. Please try again.')

		elif "otp_token" in request.POST:
			user_id = request.session.get("temp_user_id")
			user = User.objects.get(id=user_id)
			device = TOTPDevice.objects.get(user=user, confirmed=True)
			otp_token = request.POST.get("otp_token")

			if device.verify_token(otp_token):
				login(request, user)
				del request.session["temp_user_id"]
				return redirect('/')
			else:
				step = "part2"
				messages.error(request, 'Invalid token. Please try again.')
				return render(request, 'a_two_factor/login.html', {'step':step})

	return render(request, 'a_two_factor/login.html', {'step':step})

@login_required
def backup_tokens(request):
    
	device = StaticDevice.objects.get_or_create(
        user=request.user, name="backup_tokens"
    )[0]

	if request.method == "POST":
		device.token_set.all().delete()

		# 10 = number of token generated
		for _ in range(10):
			device.token_set.create(token=StaticToken.random_token())
		return redirect("backup_tokens")

	return render(request, "a_two_factor/backup_tokens.html", {"device":device,})

@login_required
def setup_2fa(request):

	device = TOTPDevice.objects.get_or_create(
		user=request.user, name="default", confirmed=False
	)[0]

	qr_code_img = qrcode.make(device.config_url)
	buffer = BytesIO()
	qr_code_img.save(buffer)
	buffer.seek(0)
	encoded_img = b64encode(buffer.read()).decode()
	QR_URL = f'data:image/png;base64,{encoded_img}'

	if request.method == "POST":
		cancel = request.POST.get("cancel")

		if cancel:
			device.delete()
			return redirect('profile-settings')

		otp_token = request.POST.get("otp_token")
		if device.verify_token(otp_token):
			device.confirmed = True
			device.save()
			messages.success(request, '2FA is now activate')
			return redirect('/')
		else:
			messages.error(request, 'Invalid token.')

	context = {
		"QR_URL": QR_URL,
		"secret_key": device.key,
		"otpauth_url": device.config_url,
	}
	return render(request, 'a_two_factor/setup.html', context)

@login_required
def disable_2fa(request):

	if request.method == "POST":
		totp_device = TOTPDevice.objects.filter(user=request.user).first()

		if totp_device:
			totp_device.delete()
		return redirect('profile-settings')

	return render(request, 'a_two_factor/disable.html')

### Friend handler part

@login_required
def create_friend_request(request, username):
	if request.method == "GET":
		requester = request.user
		target = get_object_or_404(User, username=username)

		if target.profile in requester.profile.friends.all():
			return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})
	
		if target.profile in requester.profile.pending_request.all():
			return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})

		requester.profile.pending_request.add(target.profile)
		target.profile.invite_request.add(requester.profile)

		return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})

	return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})

@login_required
def accept_friend_request(request, username):
	if request.method == "GET":
		target = request.user
		requester = get_object_or_404(User, username=username)

		requester.profile.pending_request.remove(target.profile)
		target.profile.invite_request.remove(requester.profile)
		target.profile.friends.add(requester.profile)

	return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})

@login_required
def reject_friend_request(request, username):
	if request.method == "GET":
		target = request.user
		requester = get_object_or_404(User, username=username)

		requester.profile.pending_request.remove(target.profile)
		target.profile.invite_request.remove(requester.profile)

	return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})

@login_required
def delete_friend(request, username):
	if request.method == "GET":
		requester = request.user
		target = get_object_or_404(User, username=username)

		requester.profile.friends.remove(target.profile)
		target.profile.friends.remove(requester.profile)

	return render(request, 'a_friends/friends_interface.html', {'section': 'true_relations'})

@login_required
def friends(request, section="true_relations"):
    query = request.GET.get('search_user_input', '')
    results = []

    if query:
        results = User.objects.filter(username__icontains=query)

    true_relations = request.user.profile.friends.all()
    false_relations = request.user.profile.invite_request.all()

    context = {
        'true_relations': true_relations,
        'false_relations': false_relations,
        'query': query,
        'results': results,
        'section': section,
    }

    if request.headers.get('x-spa-request') == 'true': 
        html = render_to_string(f'a_friends/partials/friends_interface_p.html')
        return JsonResponse({
            'html': html,
            'target': 'dynamic-content',  # ID de l'élément cible
            'context': context
        })

    return render(request, 'a_friends/friends_interface.html', context)
