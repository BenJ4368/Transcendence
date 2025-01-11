# Transcendence
> bgaertne's part

# Infrastructure backend et déploiement
Cette partie primaire du projet consiste en la création et la gestion des containers Docker, qui englobe:
- **le serveur web Nginx, et son pare-feu Naxsi**
- **la base de données PostgreSQL et la gestion du cache avec Redis.**
- **le coffre-fort Vault**
- **l'application Django en elle-même**

# Nginx et Naxsi
> Reverse Proxy et Web App Firewall

> Nginx, 'Engine X'

Le ***Proxy*** standard, ou "***Forward Proxy***" agit en intermédiaire pour le client. Le client veut faire une demande à un serveur sur le web, mais c'est son proxy qui converse avec le serveur, et passe ensuite la réponse au client, protégeant ainsi l'identité de ce dernier.

Le ***Reverse Proxy*** agit de la même façon, mais il protège les serveurs. Il gère les requêtes des clients et renvoie les réponses appropriées. Il est ici couplé à un pare-feu d'application web (WAF) pour déceler les requêtes potentiellement dangereuses.

### Nginx agit donc en Reverse Proxy dans notre configuration.

C'est également Nginx qui accepte ou refuse les connexions HTTP et/ou HTTPS, et qui utilise la technologie SSL pour chiffrer les données transitant entre un navigateur et un site web. Tout ça selon la configuration utilisée, évidemment.

Un ***Web App Firewall***, ou pare-feu d'applications web, agit comme un videur. Il intercepte toutes les requêtes reçues par le Proxy, et les analyse. Grâce à un set de règles bien précises, il redirige les requêtes jugées malveillantes vers une page dédiée, interdisant l'accès aux serveurs.

Ainsi, les injections SQL, scripts XSS et autres attaques via requêtes HTTP sont bloquées avant d'atteindre le serveur.

`https://127.0.0.1/profil/login/` renverra la bonne page.

`https://127.0.0.1/je_suis-une.requete?malveillante` ne sera pas stoppée, mais rendra une 404.

`https://127.0.0.1/test.php?input=<script>alert('XSS')<script>` ne passera pas, et sera redirigée vers la page 'Request Denied' grâce aux règles Naxsi.

Le container **Nginx** se trouve dans le réseau Docker *nginx-django-network*. Il ne peut communiquer qu'avec le container qui contient l'application **Django**.

### Nginx est un composant principal du projet, et tourne sur un container dédié. Naxsi est une sorte d'add-on pour Nginx, les deux sont installés en même temps, dans le même container. Ce service est le dernier à être lancé.

# PostgreSQL et Redis
> Persistance et mise en cache des données

La ***Base de données***, gérée par ***PostgreSQL***, permet de stocker les différentes données nécessaires au fonctionnement de l'application. Sans persistance des données, rien n'est sauvegardé sur le long terme. Recharger la page, vider le cache ou redémarrer l'application ferait perdre toutes les données entrées préalablement.

Le serveur de mise en cache ***Redis*** permet de stocker dans la mémoire vive puis d'utiliser rapidement certaines données à court terme. Souvent utilisé pour les opérations comme les sessions ou la gestion des files d'attente.

L'installation et la configuration des containers Docker qui contiennent chacun l'un de ces deux services est la seule chose que j'ai eu à faire. La base de données PostgreSQL est entièrement gérée par l'application Django, notamment via les migrations qui sont effectuées et vérifiées à chaque redémarrage du projet. Redis n'a pas besoin de configuration particulière.

Ces deux containers se trouvent dans le réseau Docker *redis-postgres-django-network*. Ils ne peuvent communiquer qu'entre eux (ce qui n'arrive pas, pas besoin) et avec l'application **Django**.

### PostgreSQL et Redis nécessitent tous les deux leurs propres containers. Chacun est indépendant de l'autre. Ces deux services sont lancés en premier, avec le container Vault.

# Hashicorp's Vault
> Gestion des secrets dans une base de données à accès restreint. Le 'Coffre-fort'.

**Vault** permet la gestion, le stockage et l'accès à des données sensibles de manière sécurisée via chiffrement, scellage, et authentification.

À l'initialisation du serveur **Vault** nous sont donnés des '*Unseal keys*', et un '*Root token*'. Ces clés sont à sauvegarder en lieu sûr, elles ne seront pas redonnées par la suite.

Après initialisation et à chaque redémarrage de **Vault**, le serveur est scellé. Ses secrets sont chiffrés et inaccessibles. Les *Unseal keys*, dont on choisit le nombre à l'initialisation, servent à déverrouiller **Vault**. En entreprise, les *Unseal Keys* sont plus ou moins nombreuses et données à plusieurs personnes. Un nombre minimum de ces *Unseal keys* doivent être entrées pour déverrouiller **Vault**. Dans notre projet, une seule *Unseal key* est générée.

Le *Root token* est une clé d'authentification qui permet l'accès complet aux fonctionnalités de **Vault**, ***après déverrouillage***. Utilisée pour configurer et administrer **Vault**.

Je stocke nos *Unseal key*, et *Root token* dans un des fichiers accessibles uniquement depuis la machine hôte, avec les droits root. Seul mon script d'initialisation les utilise.

Pour que Django puisse communiquer avec l'**API Vault**, je crée une '*policy*', qui s'apparente à un rôle en fait, dont je décris les droits sur les données dans un fichier de configuration. Il faudra ensuite créer un *Client Vault*, grâce à la librairie *Hvac*, dans l'application Django, qui se chargera de communiquer avec **Vault**. C'est ce client qui va lire, lister, écrire, modifier et supprimer les données dans **Vault**, selon la '*policy*'.

Ce container **Vault** se trouve dans le réseau Docker *vault-django-network*. Il ne peut communiquer qu'avec l'application **Django**. Et uniquement via l'**API Vault**.

### Vault tourne dans son propre container, qui est lancé en premier, avec PostgreSQL et Redis. Une fois le serveur lancé, puisqu'il est à initialiser et/ou à déverrouiller, un second container Vault-init se lance et effectue les actions requises via un script. Le container Vault-init se ferme lorsqu'il n'est plus utile.

# L'application Django
> Framework Django, ses requirements, et Daphne

Après le développement de l'application avec le **Framework Django** par mes collègues, j'en récupère les fichiers, et les 'requirements' à installer pour créer le container Docker où cette application va tourner. J'installe aussi **Daphne**, un service qui sert d'interface asynchrone entre **Nginx** et **Django Channels**. Un intermédiaire qui s'assure que **Nginx** et **Django** communiquent correctement.
Un peu de configuration pour les connexions avec **PostgreSQL**, **Redis** et **Vault**, et je peux lancer le container. J'installe les dépendances, copie l'application, lance Daphne, et tout est bon de mon côté.

Ce container **Web** se trouve dans les 3 réseaux précédents. Il peut donc communiquer avec tous les containers dans leurs réseaux respectifs.

### L'application Django et le serveur Daphne se trouvent dans le même container. Il se lance lorsque Vault-init a terminé de déverrouiller Vault. Le container Nginx se lance juste après.