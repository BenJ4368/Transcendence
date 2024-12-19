// Fonction pour charger un template dynamique
function loadPartial(url, updateHistory = true) {
	fetch(url, {
		headers: {
			'x-requested-with': 'XMLHttpRequest',
			'x-spa-request': 'true' // Header personnalisé
		}})
		.then(response => {
			if (!response.ok) {
				throw new Error(`Erreur HTTP : ${response.status}`);
			}
			return response.json(); // Convertir la réponse en JSON
		})
		.then(data => {
			// Récupérer l'élément cible et mettre à jour son contenu
			const targetElement = document.getElementById(data.target);
			if (!targetElement) {
				throw new Error(`Élément avec l'ID '${data.target}' introuvable`);
			}

			// Injecter le HTML dans l'élément cible
			targetElement.innerHTML = data.html;

			const event = new CustomEvent('spaContentUpdated', { detail: { time: Date.now() } });
			document.dispatchEvent(event);

			// Mettre à jour l'URL dans la barre d'adresse si demandé
			if (updateHistory) {
				history.pushState({ templateName: url }, '', url);
			}
		})
		.catch(error => {
			console.error('Erreur lors du chargement du template :', error);
		});
}

// Fonction pour attacher des événements aux liens SPA
function SetupSpaLinks() {
	document.querySelectorAll('.spa-link').forEach(link => {
		link.removeEventListener('click', handleSpaLinkClick); // Supprimer les anciens événements pour éviter les doublons
		link.addEventListener('click', handleSpaLinkClick); // Attacher l'événement de clic
	});
}

// Gestionnaire de clic pour les liens SPA
function handleSpaLinkClick(event) {
	event.preventDefault();
	const url = this.getAttribute('href'); // URL du lien
	loadPartial(url); // Charger le contenu partiel via AJAX
}


document.addEventListener('DOMContentLoaded', function () {
	console.log("envent called : DOMContentLoaded")
    const initialPath = location.pathname;
    console.log('Initial load: setting history state for', initialPath);

    // Ajouter un état initial dans l'historique
    history.replaceState({ templateName: initialPath }, '', initialPath);
	document.dispatchEvent(new Event('spaContentUpdated'));
    // Initialiser les liens SPA
});


// Gérer les boutons "Avant" et "Arrière" du navigateur
window.addEventListener('popstate', function (event) {
	// Afficher le chemin actuel
	const currentPath = location.pathname;
	console.log('popstate triggered');
	console.log('Current Path:', currentPath);

	// Afficher l'état actuel de l'historique
	if (event.state) {
		console.log('Event State:', event.state);
		console.log('Template Name in State:', event.state.templateName);
	} else {
		console.log('No state in event.');
	}

	// Recharger le contenu en fonction de l'état ou du chemin actuel
	if (event.state && event.state.templateName) {
		console.log('Loading partial using templateName from state...');
		loadPartial(event.state.templateName, false); // Utiliser l'état de l'historique
	} else {
		console.log('Loading partial using currentPath...');
		loadPartial(currentPath, false); // Recharger l'URL actuelle si l'état est manquant
	}
	document.dispatchEvent(new Event('spaContentUpdated'));
});

// Assurez-vous que l'écouteur est défini immédiatement
document.addEventListener('spaContentUpdated', function (e) {
	console.log("event listener spa", e.detail); // Vérifiez que l'écouteur fonctionne
	SetupSpaLinks(); // Reconfigure les éléments après mise à jour dynamique
});

const globalSocket = new WebSocket('ws://' + window.location.host + '/ws/global/');

function sendMessage(message) {
	if (globalSocket.readyState === WebSocket.OPEN) {
		globalSocket.send(JSON.stringify({ 'message': message }));
	} else {
		console.error('WebSocket non prêt : état actuel = ', globalSocket.readyState);
	}
}

globalSocket.onopen = function() {
	console.log('Connexion établie');
	// Exemple : envoyer un message à l'ouverture
	sendMessage('Bonjour tout le monde!');
};

globalSocket.onmessage = function(e) {
	const data = JSON.parse(e.data);
	console.log('Message reçu : ', data.message);
};

globalSocket.onclose = function() {
	console.log('Connexion fermée');
};