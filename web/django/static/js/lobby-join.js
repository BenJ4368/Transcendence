let selectedLobbyId = null;

function setupLobbyButtons() {
	const lobbyButtons = document.querySelectorAll('.lobby-list button'); // Sélectionne les boutons actuels

	lobbyButtons.forEach(button => {
		button.classList.remove('selected'); // Retire les classes "selected"
		button.disabled = false; // Active tous les boutons (facultatif)

		button.removeEventListener('click', LobbyButtonsHandler);
		button.addEventListener('click', LobbyButtonsHandler);
	});
}

function LobbyButtonsHandler(event){

	const joinLobbyButton = document.getElementById('join-lobby-button');
	const joinLobbyLink = document.getElementById('join-lobby-link');
	const lobbyButtons = document.querySelectorAll('.lobby-list button'); // Sélectionne les boutons actuels
	const button = event.currentTarget;

	// console.log("lobby button clicked", event.detail);
	lobbyButtons.forEach(btn => btn.classList.remove('selected'));
	selectedLobbyId = button.getAttribute('data-id');
	button.classList.add('selected');

	if (selectedLobbyId) {
		joinLobbyButton.disabled = false; // Active le bouton
		joinLobbyButton.classList.remove('button-disabled'); // Supprime la classe désactivée
	} else {
		joinLobbyButton.disabled = true; // Désactive le bouton
		joinLobbyButton.classList.add('button-disabled'); // Ajoute une classe désactivée
	}

	joinLobbyLink.href = `/lobby/room/${selectedLobbyId}`;	
}


function setupRefreshButton() {
	const refreshBtn = document.getElementById('refresh-btn');

	if (refreshBtn) {
		refreshBtn.removeEventListener('click', refreshBtnHandler);
		refreshBtn.addEventListener('click', refreshBtnHandler);
	}
}

function refreshBtnHandler() {

	const lobbyInfo = document.getElementById('lobby_list_body');

	fetch('', {
		headers: { 'x-requested-with': 'XMLHttpRequest' },
	})
	.then(response => response.json())
	.then(data => {
		lobbyInfo.outerHTML = data.html;
		setupLobbyButtons();
	})
	.catch(error => console.error('Erreur lors du rafraîchissement : ', error));
}

function SetupLobbyJoin(){
	console.log("Setup lobby join called");
	setupLobbyButtons();
	setupRefreshButton();
}

document.addEventListener('spaContentUpdated', function (e) {
	console.log("event listener triggered : spaContentUpdated(lobby-join.js)", e.detail);
	SetupLobbyJoin(); 
});