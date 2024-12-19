
const WebSocketManager = {
	socket: null,
	currentLobbyId: null,

	connect(lobbyId) {
		if (this.socket) {
			console.warn("WebSocket already open. Disconnecting previous socket.");
			this.disconnect();
		}

		console.log(`Connecting to WebSocket for lobby ${lobbyId}`);
		const url = `ws://${window.location.host}/ws/lobby/${lobbyId}`;
		console.log('WebSocket URL:', url); // Debug pour vérifier l'URL
		this.socket = new WebSocket(url);
		this.currentLobbyId = lobbyId;

		this.socket.addEventListener('open', () => {
			console.log(`Connected to WebSocket for lobby ${lobbyId}`);
		});

		this.socket.addEventListener('close', (event) => {
			console.log(`WebSocket closed for lobby ${lobbyId}:`, event);
		});

		this.socket.addEventListener('message', (event) => {
			const messageData = JSON.parse(event.data);
			const messageHTML = messageData.content;
			console.log("Message received from WebSocket:", messageData);

			if (messageData.type === "chat_message") {
				console.log("message type chat_message");
				const chatMessages = document.getElementById("chat_messages");
				// Crée un nouvel élément de message
				const newMessageElement = document.createElement("li");
				newMessageElement.classList.add("fade-in-up"); // Ajoute la classe d'animation
				newMessageElement.innerHTML = messageHTML; // Ajoute le contenu du message
				// Insère le nouvel élément dans le conteneur des messages
				chatMessages.appendChild(newMessageElement);
				// Assurez-vous que la fonction de défilement est appelée après l'ajout
				scrollToBottom();
			}
			// Gérer les messages ici, par exemple :
			if (messageData.type === "update_message") {
				const playersList = document.getElementById("player-box");
				if (playersList) {
					playersList.outerHTML = messageData.content;
				}
			}
			if (messageData.type === "redirect") {
				alert(messageData.message);
				loadPartial("/");
			}
		});
	},

	disconnect() {
		if (this.socket) {
			console.log(`Disconnecting WebSocket for lobby ${this.currentLobbyId}`);
			this.socket.close();
			this.socket = null;
			this.currentLobbyId = null;
		}
	},
};

function setupChatFormListener(socket) {

	document.getElementById("chat_message_form").addEventListener("submit", function(event) {
		event.preventDefault(); // Empêche le rechargement de la page
		const messageInput = this.querySelector("input[name='body']");
		const message = messageInput.value;

		if (socket.readyState === WebSocket.OPEN) {
			console.log("message sent", message);
			socket.send(JSON.stringify({ body: message })); // Envoie le message via WebSocket
			messageInput.value = ""; // Vide le champ de saisie
		} else {
			console.error("La connexion WebSocket n'est pas ouverte.");
		}
	});
}


// function lobbyChatFormHandler(event, socket){
// 	event.preventDefault(); // Empêche le rechargement de la page
// 	const messageInput = this.querySelector("input[name='body']");
// 	const message = messageInput.value;

// 	if (socket.readyState === WebSocket.OPEN) {
// 		console.log("message sent", message);
// 		socket.send(JSON.stringify({ body: message })); // Envoie le message via WebSocket
// 		messageInput.value = ""; // Vide le champ de saisie
// 	} else {
// 		console.error("La connexion WebSocket n'est pas ouverte.");
// 	}
// }

// function setupLobbyChatForm(socket) {
// 	const lobbyChatForm = document.getElementById('chat_message_form');



// 	if (lobbyChatForm) {
// 		console.log("lobbby chat form has been found");
// 		lobbyChatForm.removeEventListener('submit', lobbyChatFormHandler(socket));
// 		lobbyChatForm.addEventListener('submit', lobbyChatFormHandler(socket));
// 	}
// }


document.addEventListener('spaContentUpdated', function (e) {
	console.log("event listener triggered : spaContentUpdated(lobby.js)", e.detail);
	// Vérifier si le contenu chargé est celui d'un lobby

	const lobbyElement = document.querySelector('[data-lobby-id]');
	if (lobbyElement) {
		console.log("lobby etre la");
		const lobbyId = lobbyElement.dataset.lobbyId;
		scrollToBottom()
		// Connecter au WebSocket pour ce lobby
		WebSocketManager.connect(lobbyId);
		setupChatFormListener(WebSocketManager.socket);

	} else {
		// Déconnecter du WebSocket si le lobby est quitté
		console.log("lobby etre pas la");
		WebSocketManager.disconnect();
	}
});

function scrollToBottom(time = 0) {
	setTimeout(function() {
		const container = document.getElementById('chat_container');
		if (container) {
			container.scrollTop = container.scrollHeight;
		}
	}, time);
}