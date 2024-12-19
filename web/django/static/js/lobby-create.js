function setupLobbyCreateForm(){

	lobbyForm = document.querySelector('#lobby-create-form');

	if(lobbyForm)
	{
		lobbyForm.removeEventListener('submit', lobbyCreateFormHandler);
		lobbyForm.addEventListener('submit', lobbyCreateFormHandler);
	}
}

async function lobbyCreateFormHandler(event)
{
	event.preventDefault(); // Empêche le rechargement de la page

	console.log("lobbycreate form triggered");
	const form = event.target;
	const formData = new FormData(form);

	try {
		const response = await fetch(form.action, {
			method: 'POST',
			body: formData,
			headers: {
				'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
				'x-spa-request': 'true' // Marqueur pour les requêtes SPA
			}
		});

		if (response.ok) {
			const data = await response.json();
			loadPartial(data.redirect_url);
		} else {
			console.error('Erreur lors de la création du lobby:', response.status);
		}
	} catch (error) {
		console.error('Erreur réseau ou serveur:', error);
	}
}

function SetupLobbyCreate() {
	console.log("Setup lobby create called");
	setupLobbyCreateForm();
}

document.addEventListener('spaContentUpdated', function (e) {
	console.log("event listener triggered : spaContentUpdated(lobby-create.js)", e.detail);
	SetupLobbyCreate(); 
});
