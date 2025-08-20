document.addEventListener('DOMContentLoaded', function() {
	const form = document.getElementById('search-form');
	const queryInput = document.getElementById('query');
	const chatMessages = document.getElementById('chat-messages');
	const loading = document.getElementById('loading');
	const searchButton = document.getElementById('search-button');
	const stepSearch = document.getElementById('step-search');
	const stepAnalyze = document.getElementById('step-analyze');
	const stepGenerate = document.getElementById('step-generate');

	function updateLoadingStep(step) {
		// Retirer d'abord toutes les classes active
		[stepSearch, stepAnalyze, stepGenerate].forEach(el => {
			el.classList.remove('active');
		});

		// Ajouter les classes active selon l'étape
		switch(step) {
			case 'search':
				stepSearch.classList.add('active');
				break;
			case 'analyze':
				stepSearch.classList.add('active');
				stepAnalyze.classList.add('active');
				break;
			case 'generate':
				stepSearch.classList.add('active');
				stepAnalyze.classList.add('active');
				stepGenerate.classList.add('active');
				break;
		}
	}

	form.addEventListener('submit', async function(e) {
		e.preventDefault();
		
		const query = queryInput.value.trim();
		if (!query) return;
		
		// Ajouter le message de l'utilisateur
		addMessage(query, 'user');
		
		// Désactiver le bouton et afficher le chargement
		searchButton.disabled = true;
		loading.classList.remove('hidden');
		
		try {
			// Étape 1 : Recherche
			updateLoadingStep('search');
			await new Promise(resolve => setTimeout(resolve, 800));
			
			// Envoyer la requête
			const response = await fetch('/search', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ query }),
			});
			
			// Étape 2 : Analyse
			updateLoadingStep('analyze');
			await new Promise(resolve => setTimeout(resolve, 800));
			
			if (!response.ok) {
				throw new Error('Erreur réseau');
			}
			
			// Étape 3 : Génération
			updateLoadingStep('generate');
			
			const data = await response.json();
			
			// Traiter la réponse
			if (data.error) {
				console.error('Erreur reçue:', data.error);
				addMessage(`Erreur: ${data.error}`, 'assistant');
			} else if (data.response) {
				addMessage(data.response.content, 'assistant');
			} else {
				addMessage('Désolé, la réponse du serveur est dans un format inattendu.', 'assistant');
			}
		} catch (error) {
			console.error('Erreur:', error);
			addMessage('Désolé, une erreur s\'est produite lors de la recherche.', 'assistant');
		} finally {
			// Réactiver le bouton et masquer le chargement
			searchButton.disabled = false;
			loading.classList.add('hidden');
			queryInput.value = '';
		}
	});

	function addMessage(content, sender) {
		const messageDiv = document.createElement('div');
		messageDiv.className = `message ${sender}-message`;
		messageDiv.innerHTML = content;
		chatMessages.appendChild(messageDiv);
		chatMessages.scrollTop = chatMessages.scrollHeight;
	}
	
	// Fonction pour définir une requête prédéfinie
	window.setQuery = function(query) {
		queryInput.value = query;
		queryInput.focus();
		// Faire défiler jusqu'au formulaire
		document.querySelector('.search-form').scrollIntoView({ behavior: 'smooth' });
	};
});


