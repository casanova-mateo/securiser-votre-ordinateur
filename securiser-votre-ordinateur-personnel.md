# 🛡️ Sécuriser votre ordinateur personnel

*Guide pratique pour Windows, macOS et Linux — par Matéo CASANOVA*

## 🔐 Pourquoi sécuriser votre ordinateur ?

Vos fichiers personnels, vos e-mails, vos données bancaires ou vos documents importants peuvent être ciblés par des logiciels malveillants, des pirates informatiques ou des entreprises qui collectent vos données. Que vous utilisiez Windows, macOS ou Linux, ce guide vous aidera à protéger vos données contre les fuites, les attaques et la surveillance.

Ce guide s’adresse à tous, sans connaissances techniques particulières. Il s’appuie sur les recommandations de l’ANSSI (guide d’hygiène informatique en 42 mesures, voir l’annexe) et de Cybermalveillance.gouv.fr, adaptées à un usage personnel, et chaque conseil est accompagné de sa raison. Toutes les mesures proposées sont gratuites : seul l’achat d’un disque dur externe est conseillé pour les sauvegardes. Les rares options plus techniques sont signalées comme telles.

> **Par où commencer :** si vous ne deviez faire que cinq choses, commencez par celles-ci. Elles protègent contre les attaques les plus fréquentes : failles non corrigées, mots de passe volés, hameçonnage et perte de données.
>
> 1. Activez les mises à jour automatiques de votre ordinateur et de votre téléphone (voir 2.1, mises à jour)
> 2. Utilisez un gestionnaire de mots de passe et un mot de passe différent pour chaque compte (voir 2.3, mots de passe et accès)
> 3. Activez la double authentification (2FA) sur votre messagerie et votre banque (voir 2.3, mots de passe et accès)
> 4. Sauvegardez vos fichiers importants sur un disque externe (voir 2.8, sauvegardes)
> 5. Méfiez-vous des messages et des appels qui vous pressent d’agir, et ne communiquez jamais un code reçu par SMS (voir 4.1, bons réflexes en ligne)
>
> La liste de vérification, à la fin du guide, récapitule l’ensemble des mesures.

---

## Les bases

### 🔄 Gardez votre système et vos logiciels à jour

Tous les systèmes d’exploitation (Windows, macOS, Linux) comportent des failles de sécurité que les pirates peuvent exploiter. Les éditeurs publient régulièrement des mises à jour pour les corriger. Tarder à les installer, c’est laisser la porte ouverte aux attaques.

Ne vous arrêtez pas au système : vos logiciels (navigateur, suite bureautique, lecteur PDF…), vos extensions de navigateur et votre box internet ont eux aussi besoin de mises à jour. Activez les mises à jour automatiques partout où elles sont proposées.

> **Exemple :** lorsqu’une faille majeure est découverte dans Windows, Microsoft publie un correctif. Les cybercriminels étudient ce correctif et s’attaquent, souvent en quelques heures, aux ordinateurs qui ne sont pas encore à jour.

#### 🪟 Windows

- Ouvrez **Paramètres > Windows Update**
- Vérifiez que les mises à jour ne sont pas suspendues (elles sont automatiques par défaut)
- Installez les correctifs de sécurité sans attendre

#### 🍎 macOS

- Allez dans **Réglages Système > Général > Mise à jour de logiciels**
- Activez les mises à jour automatiques

#### 🐧 Linux

- Utilisez le gestionnaire de mises à jour, qui met aussi à jour les applications Flatpak (voir la partie Linux)

> **Attention :** Windows 10 n’est plus pris en charge par Microsoft depuis octobre 2025. Les particuliers peuvent encore recevoir ses correctifs de sécurité jusqu’au 12 octobre 2027 en s’inscrivant, depuis Windows Update, au programme de mises à jour de sécurité étendues (ESU) : en France, c’est gratuit avec un compte Microsoft. Préparez la suite dès maintenant : si votre PC peut passer à Windows 11, la mise à niveau est gratuite ; sinon, Linux Mint, gratuit lui aussi, permet de continuer à utiliser votre ordinateur en sécurité (voir la partie Linux).

---

### 🦠 Utilisez l’antivirus intégré

Pour un usage personnel, un antivirus payant n’est pas nécessaire, à condition de garder le système à jour. Mais aucun antivirus, gratuit ou payant, ne remplace la prudence : la plupart des infections viennent d’un fichier téléchargé ou d’un lien ouvert par l’utilisateur.

- **Windows :** Microsoft Defender est inclus et activé par défaut. Dans les tests indépendants d’AV-TEST et d’AV-Comparatives, il obtient des scores de protection comparables à ceux des antivirus payants. Vérifiez qu’il est actif dans **Sécurité Windows > Protection contre les virus et menaces**
- **macOS :** les protections intégrées (Gatekeeper, qui vérifie les applications, et XProtect, qui détecte les logiciels malveillants connus) fonctionnent automatiquement et se mettent à jour en arrière-plan. Elles réagissent parfois avec retard aux menaces nouvelles : la prudence sur ce que vous téléchargez reste votre meilleure protection.
- **Linux :** il n’y a pas d’antivirus intégré, mais les logiciels malveillants visant les ordinateurs personnels sous Linux sont rares, car les pirates ciblent en priorité Windows, bien plus répandu. Votre protection repose surtout sur vos habitudes : installez vos logiciels depuis le gestionnaire de logiciels de votre distribution, n’exécutez pas un fichier ou une commande trouvés sur Internet sans savoir ce qu’ils font, et gardez le système à jour. Si vous téléchargez beaucoup de fichiers ou en échangez avec des utilisateurs de Windows, l’antivirus libre et gratuit ClamAV permet de les analyser (option technique).

> **Attention :** une fenêtre ou une page web qui affirme que votre ordinateur est infecté et vous pousse à acheter un logiciel ou à appeler un numéro est presque toujours une arnaque. Fermez-la sans rien télécharger.

---

### 👤 Sécurisez vos mots de passe et vos accès

Bien protéger vos accès garantit que personne d’autre que vous ne peut utiliser votre ordinateur ou vos comptes en ligne. C’est votre première ligne de défense contre les accès non autorisés.

**Ce qui protège vos accès :**

- Un mot de passe fort et unique (ou une phrase secrète)
- Une authentification biométrique, en option (empreinte digitale, reconnaissance faciale)
- L’authentification à deux facteurs (2FA) pour une protection supplémentaire
- Les clés d’accès (passkeys), qui remplacent peu à peu les mots de passe

#### 🔑 L’entropie des mots de passe (pourquoi le hasard compte)

En sécurité, l’entropie mesure à quel point un mot de passe est imprévisible, autrement dit le nombre de tentatives qu’un attaquant devrait effectuer pour le deviner.

- **Faible entropie :** peu de possibilités, facile à deviner. Exemple : `Password123` semble complexe, mais suit un schéma très courant.
- **Haute entropie :** énormément de possibilités, très difficile à deviner. Exemple : `n9!X4uVq%3pL7#dA` est long, aléatoire et imprévisible.

**Comment augmenter l’entropie :**

- **Allongez le mot de passe :** chaque caractère supplémentaire multiplie le nombre de combinaisons à essayer (16 caractères minimum).
- **Mélangez les types de caractères :** majuscules, minuscules, chiffres et symboles.
- **Rendez-le aléatoire :** évitez les mots du dictionnaire, les dates de naissance et les suites logiques (`123456`, `azerty`).

En résumé, ce sont les mots de passe entièrement aléatoires qui offrent la meilleure entropie : laissez votre gestionnaire de mots de passe les générer pour vous. Pour les rares mots de passe que vous devez retenir (session de l’ordinateur, gestionnaire de mots de passe), une phrase secrète d’au moins 6 mots tirés au hasard (méthode Diceware : des dés et une liste de 7 776 mots) est une excellente alternative, beaucoup plus facile à mémoriser. Elle offre plus de 200 000 milliards de milliards de combinaisons.

> **Pourquoi c’est important :** quand une base de mots de passe mal protégée est volée, les pirates peuvent tester des centaines de milliards de combinaisons par seconde sur leurs propres machines. À ce rythme, un mot de passe de 8 lettres minuscules est trouvé en quelques secondes, alors qu’un mot de passe aléatoire de 16 caractères demanderait des milliers de milliards d’années.

#### 🔄 Pourquoi votre mot de passe doit être unique pour chaque compte

Si vous utilisez le même mot de passe sur plusieurs comptes et qu’un site est piraté, les attaquants récupèrent ce mot de passe et l’essaient sur vos autres comptes : c’est ce qu’on appelle le « credential stuffing » (bourrage d’identifiants).

> **Exemple :**
>
> 1. Le mot de passe de votre messagerie est `Coffee2024!`.
> 2. Vous utilisez ce même mot de passe sur une boutique en ligne, qui se fait pirater : votre mot de passe est volé.
> 3. Les pirates l’essaient sur votre messagerie, vos réseaux sociaux et votre banque… et ils y parviennent.

> **Solution :** utilisez un mot de passe différent pour chaque compte. Ainsi, si l’un d’eux est volé, vos autres comptes restent protégés.

#### 🛠 Comment gérer vos mots de passe et vos comptes

- Utilisez un gestionnaire de mots de passe gratuit : **Bitwarden** (le plus simple, synchronisé entre ordinateur et téléphone) ou **KeePassXC** (les mots de passe restent uniquement sur votre ordinateur : copiez régulièrement son fichier, qui est chiffré, sur une clé USB ou dans le cloud). Il retient et génère pour vous des mots de passe complexes.
- Protégez ce gestionnaire par une phrase secrète solide, que vous apprenez par cœur : ce sera le seul mot de passe à retenir.
- Profitez-en pour faire la liste de vos comptes en ligne et supprimez ceux que vous n’utilisez plus.
- Configurez le verrouillage automatique de votre appareil après 5 à 10 minutes d’inactivité, pour qu’un ordinateur laissé sans surveillance ne reste pas ouvert.
- Ne réutilisez jamais un mot de passe sur plusieurs comptes.
- Activez la 2FA en priorité sur votre messagerie, votre banque et votre gestionnaire de mots de passe : la connexion exige alors votre mot de passe **et** un code temporaire, reçu par SMS ou, de préférence, généré par une application gratuite (Ente Auth, 2FAS…). Un SMS peut en effet être détourné si un escroc obtient un duplicata de votre carte SIM.
- Rangez les codes de secours fournis lors de l’activation de la 2FA dans votre gestionnaire de mots de passe : ils vous permettront de récupérer vos comptes si vous perdez votre téléphone.
- Vérifiez de temps en temps si votre adresse e-mail apparaît dans une fuite de données connue (haveibeenpwned.com, gratuit). Si c’est le cas, changez les mots de passe concernés.
- Sur un ordinateur familial, créez un compte par personne, chacun avec son propre mot de passe : chacun garde ses fichiers et ses comptes à l’abri des erreurs des autres.
- Ne communiquez jamais votre mot de passe à qui que ce soit : aucun service légitime ne vous le demandera.

#### 🧰 Le kit de secours

Quelques informations ne peuvent pas être rangées dans le gestionnaire de mots de passe, puisqu’elles servent justement à y accéder ou à débloquer l’ordinateur. Notez-les sur une feuille rangée chez vous en lieu sûr, jamais près de l’ordinateur ni sur un post-it :

- la phrase secrète du gestionnaire de mots de passe ;
- le code de récupération 2FA du gestionnaire ;
- la clé de récupération du chiffrement du disque (sous Linux, sa phrase de chiffrement).

Pourquoi ces trois-là seulement ? Une feuille de papier ne se verrouille pas : quiconque la trouve peut la lire. Vos autres mots de passe restent donc dans le gestionnaire, qui les chiffre. Mais pour ces trois secrets, qui ouvrent tout le reste, le risque de les oublier et de perdre définitivement l’accès à vos données est bien plus élevé que celui qu’un cambrioleur trouve la feuille et sache s’en servir.

#### 🗝️ Les clés d’accès (passkeys) : l’avenir des mots de passe

De plus en plus de services (Google, Apple, Microsoft, Amazon…) proposent de remplacer le mot de passe par une clé d’accès (*passkey*). Vous vous connectez alors avec l’empreinte, la reconnaissance faciale ou le code de déverrouillage de votre appareil, sans rien taper.

- **Plus pratique :** il n’y a rien à retenir ni à saisir.
- **Plus sûr :** la clé d’accès ne fonctionne que sur le vrai site. Un faux site d’hameçonnage ne peut pas la récupérer, même si vous vous laissez tromper : c’est aujourd’hui la meilleure protection contre le phishing.
- Quand un service vous le propose, acceptez de créer une clé d’accès. Elle est enregistrée dans votre gestionnaire de mots de passe (Bitwarden les gère gratuitement) ou dans celui de votre appareil (Apple, Google, Windows).
- Gardez une autre méthode de connexion (mot de passe avec 2FA, codes de secours) tant que vous n’êtes pas sûr de retrouver vos clés d’accès sur un nouvel appareil.

#### 🪟 Sécuriser votre session Windows

- Utilisez un mot de passe ou une phrase secrète robuste
- Activez Windows Hello (code PIN, empreinte ou reconnaissance faciale selon votre PC) dans **Paramètres > Comptes > Options de connexion**. Le code PIN Windows Hello ne fonctionne que sur ce PC : même découvert, il ne donne pas accès à votre compte Microsoft ailleurs.
- Votre compte, créé à l’installation, est administrateur. Pour passer à un compte standard sans déplacer vos fichiers : dans **Paramètres > Comptes > Autres utilisateurs**, ajoutez un second compte et donnez-lui le type « Administrateur ». Si Windows vous demande une adresse e-mail, choisissez « Je ne dispose pas des informations de connexion de cette personne », puis « Ajouter un utilisateur sans compte Microsoft ». Connectez-vous-y une fois, puis passez votre compte habituel en « Utilisateur standard ». Pour installer un logiciel, Windows vous demandera simplement le mot de passe administrateur, sans changer de session : rangez-le dans votre gestionnaire de mots de passe.
- Réglez un délai court de mise en veille et de verrouillage de l’écran

#### 🍎 Sécuriser votre session macOS

- Utilisez une phrase secrète robuste
- Activez Touch ID ou le déverrouillage avec l’Apple Watch
- Votre compte, créé à la configuration du Mac, est administrateur. Pour passer à un compte standard sans déplacer vos fichiers : dans **Réglages Système > Utilisateurs et groupes**, ajoutez un second compte de type « Administrateur ». Connectez-vous-y une fois, puis retirez à votre compte habituel l’autorisation d’administrer l’ordinateur. Pour installer un logiciel, macOS vous demandera simplement le nom et le mot de passe administrateur : rangez-les dans votre gestionnaire de mots de passe.
- Exigez le mot de passe dès la mise en veille de l’écran dans **Réglages Système > Écran verrouillé**

---

### 🔐 Activez le chiffrement complet du disque

Le chiffrement complet du disque protège vos données « au repos », c’est-à-dire lorsque votre ordinateur est éteint. Si votre ordinateur portable est perdu ou volé, le chiffrement garantit que, sans votre mot de passe, vos fichiers ne sont qu’une suite de données incompréhensibles pour quiconque tenterait de les lire.

- **Sans chiffrement :** un voleur peut retirer votre disque, le brancher sur un autre ordinateur et lire vos fichiers en quelques minutes.
- **Avec chiffrement :** il n’obtient que des données brouillées et illisibles, sauf en cas de faille non corrigée dans le système de chiffrement ou de mot de passe trop faible.

> **Attention :** le chiffrement s’accompagne d’une clé de récupération. Si vous la perdez et oubliez votre mot de passe, vos données sont définitivement perdues. Ajoutez-la à votre kit de secours (voir « Le kit de secours », en 2.3), jamais dans un fichier sur le même ordinateur.

#### 🪟 Windows

- Édition Famille : activez le chiffrement de l’appareil dans **Paramètres > Confidentialité et sécurité > Chiffrement de l’appareil**. Il est souvent déjà actif sur les PC récents, mais il nécessite un PC compatible et une connexion avec un compte Microsoft.
- Éditions Pro, Entreprise et Éducation : activez BitLocker dans **Panneau de configuration > Système et sécurité > Chiffrement de lecteur BitLocker**
- Avec un compte Microsoft, votre clé de récupération y est enregistrée automatiquement (account.microsoft.com/devices/recoverykey). Avec un compte local, Windows vous propose de l’imprimer ou de l’enregistrer dans un fichier. Dans tous les cas, ajoutez-la à votre kit de secours.
- Si l’option n’apparaît pas, VeraCrypt est une alternative gratuite, réservée aux utilisateurs à l’aise avec l’informatique
- Par défaut, la puce de sécurité du PC (TPM) déverrouille le disque automatiquement au démarrage : c’est alors votre mot de passe Windows qui protège vos données, et le disque reste illisible s’il est retiré de l’ordinateur. Option technique (éditions Pro) : ajoutez un code PIN demandé avant le démarrage de Windows. Sans ce code, un voleur qui allume le PC trouve le disque déjà déverrouillé, ce qui rend possibles des attaques avancées, comme intercepter la clé au moment où la puce la transmet. Avec le code, le disque reste verrouillé tant qu’il n’a pas été saisi. Il faut d’abord autoriser cette option dans l’éditeur de stratégie de groupe (« Exiger une authentification supplémentaire au démarrage »).

#### 🍎 macOS

- Activez FileVault dans **Réglages Système > Confidentialité et sécurité > FileVault** (il est souvent proposé dès la configuration du Mac)
- Au moment de l’activation, choisissez de créer une clé de récupération et ajoutez-la à votre kit de secours. L’autre option, autoriser votre compte iCloud à déverrouiller le disque, est plus simple, mais la protection de votre Mac dépend alors aussi de la sécurité de votre compte Apple.

#### 🐧 Linux

- Le chiffrement (LUKS) s’active au moment de l’installation, il est difficile à ajouter après coup (voir la partie Linux)

---

### ☁️ Maîtrisez vos comptes en ligne (Microsoft, iCloud)

Les comptes liés au cloud (compte Microsoft sous Windows, iCloud sous macOS) synchronisent souvent vos fichiers, vos paramètres et même vos mots de passe vers des serveurs distants. Cela signifie que :

- vos données sont stockées hors de votre contrôle ;
- une fuite de données chez Microsoft ou Apple pourrait exposer vos informations ;
- l’entreprise peut être contrainte de transmettre vos fichiers aux autorités, et un pirate qui prend le contrôle de votre compte y accède aussi.

Cette synchronisation est pratique, mais elle introduit des risques pour votre confidentialité et votre sécurité.

**Recommandations :**

- Protégez votre compte Microsoft ou Apple par un mot de passe unique et la 2FA, car il donne accès à toutes vos données
- Désactivez la synchronisation de vos fichiers les plus sensibles (papiers d’identité, documents bancaires, fiches de paie), ou chiffrez-les avant de les envoyer dans le cloud (voir Cryptomator dans la partie sur les sauvegardes)
- Un compte local, sans cloud, reste l’option la plus confidentielle lorsque votre système le permet

#### 🪟 Windows

- Édition Famille : gardez votre compte Microsoft, car il est nécessaire au chiffrement de l’appareil, et protégez-le avec la 2FA (account.microsoft.com)
- Éditions Pro : un compte local est possible, à condition d’activer BitLocker
- N’enregistrez pas vos documents sensibles sur OneDrive
- Limitez les données envoyées à Microsoft dans **Paramètres > Confidentialité et sécurité > Diagnostics et commentaires**

#### 🍎 macOS

- Ouvrez **Réglages Système > [votre nom] > iCloud**
- Désactivez les services que vous ne souhaitez pas synchroniser (iCloud Drive, Photos, Contacts…)
- Option avancée : activez la **Protection avancée des données** (chiffrement de bout en bout d’iCloud). Elle exige de configurer un contact ou une clé de secours.
- Pour ne plus utiliser iCloud, cliquez sur **Se déconnecter** et choisissez de conserver une copie locale de vos données
- Désactivez le partage des analyses dans **Réglages Système > Confidentialité et sécurité > Analyse et améliorations**

---

### 🌐 Sécurisez votre navigation sur le web

C’est par le navigateur que commencent la plupart des attaques : sites d’hameçonnage (phishing), publicités malveillantes, téléchargements piégés et scripts de pistage. Considérez-le comme la porte d’entrée de votre vie numérique : s’il est vulnérable, les pirates n’ont pas besoin de toucher au reste de votre système.

**Conseils :**

- Utilisez un navigateur gratuit axé sur la confidentialité, qui limite par défaut le pistage publicitaire : Firefox ou Brave. Tor Browser, plus lent, est à réserver aux besoins ponctuels d’anonymat.
- Installez un bloqueur de publicités comme uBlock Origin (Firefox) : il bloque aussi les publicités piégées et de nombreux traqueurs. Brave intègre déjà le sien. N’ajoutez pas d’extensions à Tor Browser : chacune rend votre navigateur plus reconnaissable et réduit votre anonymat.
- Si vous gardez Chrome ou Edge : installez uBlock Origin Lite. Dans Chrome, activez la « Protection renforcée » (**Paramètres > Confidentialité et sécurité > Sécurité**), qui vérifie en temps réel les sites et les téléchargements dangereux, mais transmet en contrepartie à Google l’adresse des pages que vous visitez. Dans Edge, laissez Microsoft Defender SmartScreen activé : il bloque les sites et les téléchargements signalés comme dangereux.
- N’installez que les extensions dont vous avez vraiment besoin et supprimez les autres : une extension peut souvent lire le contenu des pages que vous visitez
- Safari et Brave bloquent déjà les cookies tiers, et Firefox les cloisonne site par site : ces cookies ne peuvent plus vous suivre d’un site à l’autre. Ne désactivez pas cette protection.
- Gardez votre navigateur à jour
- Avant de saisir des informations personnelles, vérifiez que l’adresse commence par `https://` et qu’elle est correctement orthographiée. Dans Firefox, activez le mode HTTPS uniquement (**Paramètres > Vie privée et sécurité**).
- Préférez un gestionnaire de mots de passe dédié à celui du navigateur. Les logiciels espions spécialisés dans le vol d’identifiants (« infostealers ») visent en priorité les mots de passe enregistrés dans les navigateurs, alors qu’un gestionnaire verrouillé garde les siens chiffrés par sa phrase secrète. Si vous utilisez malgré tout le navigateur, c’est toujours bien plus sûr que de réutiliser le même mot de passe partout.

> **Attention :** le cadenas affiché à côté de l’adresse signifie seulement que la connexion est chiffrée, pas que le site est honnête. De nombreux sites frauduleux en affichent un.

#### 🍎 macOS

- Avec Safari, vérifiez que la protection contre le pistage est active dans **Safari > Réglages > Confidentialité > Empêcher le suivi sur plusieurs domaines**

---

### 📡 Sécurisez votre réseau

#### 🧱 Le pare-feu de votre ordinateur

Activez le pare-feu de votre système (gratuit et intégré) : il bloque les connexions entrantes que vous n’avez pas demandées.

- **Windows :** **Sécurité Windows > Pare-feu et protection du réseau** (activé par défaut)
- **macOS :** **Réglages Système > Réseau > Coupe-feu** (désactivé par défaut : activez-le)
- **Linux :** voir la partie Linux

#### 🏠 Chez vous : la box et le Wi-Fi

Ces réglages se font dans l’interface d’administration de votre box, accessible depuis le navigateur (l’adresse figure dans la notice ou sur l’étiquette de la box).

- Utilisez le chiffrement WPA2 ou WPA3, jamais WEP, qui se casse en quelques minutes, ni un réseau ouvert
- La clé Wi-Fi d’origine, imprimée sur la box, est généralement solide. Changez-la si elle est courte ou si vous l’avez beaucoup partagée.
- Changez le mot de passe d’administration de la box s’il est encore celui d’origine
- Désactivez le WPS (connexion par bouton ou par code PIN) si vous ne l’utilisez pas : sur de nombreux équipements, une faille connue permet de retrouver la clé Wi-Fi par ce biais
- Activez le réseau Wi-Fi invité pour vos visiteurs et vos objets connectés (caméras, enceintes, téléviseur) : ils restent ainsi séparés de vos ordinateurs
- Changez le mot de passe par défaut de vos objets connectés : les identifiants d’usine sont souvent publics et testés automatiquement par les pirates. Laissez aussi la box se mettre à jour automatiquement.

#### 🧳 En déplacement

Sur un Wi-Fi public (gare, café, hôtel), vous partagez le réseau avec des inconnus, et un pirate peut créer un faux réseau portant le même nom. La plupart des sites sont protégés par HTTPS, mais le réseau peut voir quels sites vous visitez et tenter de vous rediriger vers de fausses pages.

- Demandez le nom exact du réseau à l’établissement avant de vous y connecter
- Utilisez un VPN fiable : il chiffre toute votre connexion jusqu’à ses serveurs, et le réseau ne voit plus quels sites vous visitez. Proton VPN propose une offre gratuite (un appareil, sans limite de données ni publicité), financée par ses abonnements payants. Évitez les VPN gratuits inconnus : une étude de l’agence scientifique australienne CSIRO a trouvé des traqueurs publicitaires dans les trois quarts des VPN gratuits analysés.
- Désactivez le Wi-Fi et le Bluetooth de vos appareils quand vous ne les utilisez pas, dans les transports et les lieux publics : cela limite le pistage (certains lieux repèrent les appareils à proximité) et réduit l’exposition aux failles Bluetooth, découvertes régulièrement. Sur iPhone, réglez AirDrop sur « Contacts uniquement ».
- Le partage de connexion de votre smartphone est une alternative encore plus sûre : la connexion mobile (4G ou 5G) est chiffrée entre votre téléphone et votre opérateur, et vous êtes seul sur votre réseau, protégé par votre mot de passe

#### 🛡️ Le filtrage DNS : bloquer les sites malveillants

Chaque fois que vous visitez un site, votre ordinateur interroge un serveur DNS, l’annuaire d’Internet qui traduit le nom du site en adresse. Un DNS « filtrant » refuse de donner l’adresse des sites connus pour diffuser des virus ou pratiquer l’hameçonnage. Une fois réglé, il vous protège sans rien faire au quotidien.

- **Quad9** (9.9.9.9) : gratuit, géré par une fondation suisse à but non lucratif. Il bloque les domaines malveillants connus et ne conserve pas votre adresse IP.
- **NextDNS** : plus personnalisable (blocage des publicités, contrôle parental), mais son offre gratuite cesse de filtrer au-delà de 300 000 requêtes par mois. Il nécessite de créer un compte.

Pour activer Quad9 (réglage unique de quelques minutes), indiquez ses adresses comme serveurs DNS :

- en IPv4 : `9.9.9.9` et `149.112.112.112`
- en IPv6 : `2620:fe::fe` et `2620:fe::9`

Si votre connexion utilise l’IPv6, ce qui est le cas de la plupart des box en France, renseignez aussi les adresses IPv6 : sans elles, votre ordinateur risque de continuer à interroger le DNS de votre fournisseur d’accès. Si Internet ne fonctionne plus après le réglage, retirez les adresses IPv6.

- **Sur la box**, si elle le permet : tous les appareils du foyer sont alors protégés. Certaines box, comme la Livebox d’Orange, ne permettent pas de changer de DNS : faites alors le réglage sur l’ordinateur.
- **Windows :** **Paramètres > Réseau et Internet**, sélectionnez **Wi-Fi > Propriétés du matériel** (ou **Ethernet** si vous êtes relié par câble). À la ligne « Attribution du serveur DNS », choisissez « Manuel », renseignez les adresses IPv4 et IPv6, puis activez pour chacune le chiffrement « DNS sur HTTPS » : vos requêtes DNS ne peuvent alors plus être lues sur un Wi-Fi public. Sur un portable, laissez le retour au DNS non chiffré autorisé, car certains réseaux bloquent ce chiffrement.
- **macOS :** **Réglages Système > Réseau**, sélectionnez **Wi-Fi** (ou **Ethernet**), puis **Détails > DNS**, et ajoutez les quatre adresses.
- **Linux :** dans les paramètres réseau, cliquez sur la roue crantée de votre connexion. Dans les onglets IPv4 et IPv6, désactivez le DNS automatique et saisissez les adresses.

Sur un ordinateur portable, le réglage fait sur l’ordinateur vous protège aussi en déplacement, sauf quand un VPN est actif : c’est alors lui qui gère le DNS.

---

### 💾 Sauvegardez vos données

Une sauvegarde est une copie de vos fichiers importants, conservée séparément de votre ordinateur. Elle protège vos données en cas de perte, de vol, de panne ou d’attaque (par exemple un rançongiciel, ou *ransomware*).

Commencez par repérer vos données importantes (photos, documents administratifs, travaux personnels) : ce sont elles qu’il faut sauvegarder en priorité.

**Le minimum :** un disque dur externe et l’outil de sauvegarde gratuit intégré à votre système (voir ci-dessous). Branchez le disque au moins une fois par semaine : la sauvegarde démarre automatiquement. Débranchez-le ensuite.

**Pour aller plus loin, la règle 3-2-1-1-0 :**

- **3** copies de vos données
- sur **2** types de supports différents (par exemple : disque dur externe + clé USB ou stockage cloud)
- dont **1** copie hors site (chez un proche ou dans le cloud)
- dont **1** copie hors ligne (déconnectée)
- et **0** erreur : testez régulièrement la restauration de vos sauvegardes pour vérifier qu’elles fonctionnent

**Bonnes pratiques :**

- Chiffrez vos sauvegardes lorsque c’est possible, ou rangez le disque en lieu sûr
- Pour la copie hors site, un proche peut garder un second disque chez lui. Proton Drive et Sync.com proposent aussi 5 Go gratuits, chiffrés de bout en bout : même le fournisseur ne peut pas lire vos fichiers (applications pour Windows et macOS).
- Si vous utilisez un cloud grand public (Google Drive, OneDrive, Dropbox), chiffrez vos fichiers sensibles avant l’envoi avec **Cryptomator** (gratuit et open source sur ordinateur) : il crée un coffre-fort chiffré dans votre dossier cloud, et le fournisseur ne voit que des fichiers illisibles. Rangez le mot de passe du coffre et sa clé de récupération dans votre gestionnaire de mots de passe : sans eux, les fichiers sont irrécupérables.

> **Attention :** ne laissez pas vos sauvegardes connectées en permanence à l’ordinateur : un logiciel malveillant pourrait les infecter ou les chiffrer.

#### 🪟 Windows

- Utilisez l’**Historique des fichiers** (**Panneau de configuration > Système et sécurité > Historique des fichiers**) avec un disque externe : il sauvegarde par défaut vos dossiers Documents, Images, Vidéos, Musique et Bureau
- Éditions Pro : chiffrez le disque de sauvegarde avec BitLocker To Go. Édition Famille : rangez le disque en lieu sûr.

#### 🍎 macOS

- Utilisez Time Machine sur un disque externe, en cochant l’option **Chiffrer la sauvegarde**

#### 🐧 Linux

- Utilisez Déjà Dup (gratuit, à installer depuis le gestionnaire de logiciels si besoin), qui peut protéger vos sauvegardes par un mot de passe : rangez-le dans votre gestionnaire de mots de passe
- Attention : Timeshift, installé par défaut sous Linux Mint, sauvegarde le système mais pas vos documents

---

### 📱 Protégez aussi votre smartphone

Votre téléphone reçoit vos codes de double authentification et donne souvent accès à votre banque et à votre messagerie : il mérite la même attention que votre ordinateur.

- Verrouillez-le par un code d’au moins 6 chiffres (un million de combinaisons, contre 10 000 pour 4 chiffres), complété si vous le souhaitez par l’empreinte ou la reconnaissance faciale. Le chiffrement du téléphone est alors activé automatiquement sur les iPhone et sur les téléphones sortis avec Android 10 ou une version plus récente.
- Installez les mises à jour du système et des applications. Un téléphone qui ne reçoit plus de mises à jour de sécurité n’est plus protégé : vérifiez la durée de suivi annoncée par le fabricant avant d’acheter.
- Installez vos applications uniquement depuis l’App Store ou Google Play, qui les contrôlent avant publication, et refusez les autorisations inutiles (contacts, micro, localisation)
- Activez la localisation et l’effacement à distance : « Localiser » sur iPhone, Find Hub (anciennement « Localiser mon appareil ») sur Android
- Sauvegardez régulièrement votre téléphone (sur votre ordinateur ou dans le cloud)

---

## 🐧 Linux, une alternative gratuite et sûre

Linux est un système d’exploitation gratuit. Il est particulièrement utile pour un ordinateur trop ancien pour Windows 11, dont les correctifs de Windows 10 s’arrêteront au plus tard en octobre 2027. Comptez simplement un petit temps d’adaptation.

| Critère                | Windows                                    | macOS                                          | Linux                                               |
|------------------------|--------------------------------------------|------------------------------------------------|-----------------------------------------------------|
| Prix                   | Inclus à l’achat du PC                     | Inclus à l’achat du Mac                        | Gratuit, comme la plupart de ses logiciels          |
| Collecte de données    | Données de diagnostic envoyées, réductibles | Limitée, analyses désactivables               | Très faible, voire nulle                            |
| Code source            | Fermé                                      | Fermé en grande partie                         | Ouvert et auditable                                 |
| Ancien ordinateur      | Windows 11 exige un PC assez récent        | Seuls les Mac récents reçoivent les nouvelles versions | Fonctionne bien sur un ancien PC            |
| Logiciels malveillants | Cible principale des pirates               | Moins ciblé                                    | Rares                                               |
| Mises à jour           | Automatiques, redémarrages imposés         | Automatiques, réglables                        | Proposées par le gestionnaire, sans redémarrage imposé |

**Distributions recommandées :**

- **Linux Mint :** la plus simple pour débuter, avec une utilisation proche de Windows
- **Debian :** stable et fiable, un peu plus technique
- **Pour des besoins avancés :** Tails (système live qui passe par le réseau Tor et ne laisse aucune trace) et Qubes OS (sécurité par compartimentation ; exige un ordinateur puissant et de bonnes connaissances)

---

### 🐧 Installer Linux (guide rapide)

1. Sauvegardez vos fichiers sur un disque externe : l’installation peut effacer le contenu de votre disque
2. Choisissez une distribution (Linux Mint conseillée pour débuter)
3. Téléchargez l’image ISO uniquement depuis le site officiel, qui explique aussi comment vérifier son authenticité
4. Créez une clé USB amorçable (Rufus sous Windows, balenaEtcher sous macOS ou Linux)
5. Démarrez sur la clé USB (touche F12, F2 ou Échap au démarrage, selon le fabricant)
6. Testez le système en mode live, sans rien installer, pour vérifier que tout fonctionne (Wi-Fi, son, écran)
7. Installez Linux en activant le chiffrement du disque (option proposée par l’installateur, technologie LUKS) et ajoutez la phrase de chiffrement à votre kit de secours
8. Après l’installation :
   - Faites les mises à jour avec le gestionnaire de mises à jour (sous Linux Mint, l’icône en forme de bouclier en bas à droite de l’écran) : il met à jour en une fois le système et les applications Flatpak. En ligne de commande, `sudo apt update && sudo apt upgrade` ne met pas à jour les applications Flatpak : ajoutez `flatpak update`.
   - Activez le pare-feu, désactivé par défaut : sous Linux Mint, depuis l’écran de bienvenue (rubrique « Premiers pas »), ou avec `sudo ufw enable` si l’interrupteur se désactive tout seul ; sous Debian, `sudo apt install ufw` puis `sudo ufw enable`
   - Utilisez des mots de passe robustes
   - Configurez des sauvegardes (par exemple avec Déjà Dup, gratuit)
   - Pour plus de confidentialité, naviguez avec Firefox et un VPN fiable, ou avec Tor Browser

---

## 💡 Bonnes pratiques au quotidien

Même un système parfaitement configuré peut être fragilisé par de mauvaises habitudes. Ces règles permettent de garder vos protections (chiffrement, confidentialité, sécurité) réellement efficaces.

### 🛡️ Les bons réflexes en ligne

- Méfiez-vous des messages inattendus qui vous pressent d’agir (colis en attente, remboursement, compte bloqué…) : ne cliquez pas sur le lien et passez directement par le site officiel
- Ne communiquez jamais un code reçu par SMS ou par e-mail à quelqu’un qui vous le demande, même par téléphone et même s’il se présente comme votre banque
- Un proche vous écrit depuis un nouveau numéro (« Coucou maman, j’ai changé de numéro ») et demande de l’argent en urgence, ou vous appelle avec une voix qui semble la sienne (les voix peuvent être imitées par l’IA) ? Rappelez-le sur son numéro habituel avant toute action. Vous pouvez aussi convenir d’un mot de passe familial.
- N’ouvrez pas les pièces jointes d’expéditeurs inconnus
- Installez vos logiciels uniquement depuis leur site officiel ou le magasin d’applications de votre système. Évitez les logiciels piratés (« crackés »), une source majeure de virus : il existe des alternatives gratuites (LibreOffice, VLC, GIMP…)
- Ne contournez jamais un avertissement de sécurité de votre système : « Windows a protégé votre ordinateur » (SmartScreen) ou une application que macOS refuse d’ouvrir (Gatekeeper). De faux logiciels demandent souvent de cliquer sur « Exécuter quand même » ou « Ouvrir quand même » : c’est une technique d’infection classique.
- Avant d’envoyer une copie de pièce d’identité, ajoutez-y un filigrane indiquant le destinataire et l’usage (service gratuit de l’État : filigrane.beta.gouv.fr) : un document volé sera plus difficile à réutiliser pour usurper votre identité. Pour échanger des informations sensibles, préférez une messagerie chiffrée de bout en bout comme Signal (gratuite) : seuls vous et votre correspondant pouvez lire les messages.
- Utilisez un moteur de recherche respectueux de la vie privée, qui n’associe pas vos recherches à un profil publicitaire (DuckDuckGo, Startpage)
- Déconnectez-vous de vos comptes après utilisation sur un ordinateur partagé

### 💻 Les bonnes habitudes avec vos appareils

- Éteignez votre ordinateur quand vous ne l’utilisez pas : le chiffrement du disque ne protège pleinement vos données qu’à l’arrêt (en veille, les clés de chiffrement restent en mémoire)
- Verrouillez l’écran dès que vous vous absentez (raccourcis ci-dessous)
- Utilisez un compte standard au quotidien, et le compte administrateur uniquement pour les installations : un logiciel malveillant lancé depuis un compte standard ne peut pas modifier le système sans le mot de passe administrateur
- Installez les mises à jour dès qu’elles sont proposées, et vérifiez-les au moins une fois par semaine
- Désinstallez les logiciels que vous n’utilisez plus : chacun peut contenir des failles
- Affichez les extensions des fichiers (`.pdf`, `.exe`…) : un fichier nommé « Facture.pdf.exe » est un programme déguisé en document, à ne jamais ouvrir. Windows et macOS les masquent par défaut (réglage ci-dessous).
- Ne branchez jamais une clé USB trouvée ou offerte dont vous ignorez la provenance : elle peut contenir un logiciel malveillant, ou se faire passer pour un clavier qui tape des commandes à votre place. Débranchez vos clés et disques externes après usage.
- Vérifiez que votre pare-feu est activé avant d’utiliser un Wi-Fi public
- Ne laissez jamais votre ordinateur sans surveillance dans un lieu public
- Faites une sauvegarde avant un voyage et n’emportez que les fichiers nécessaires : en cas de perte ou de vol, vous ne perdez rien et vous exposez moins de données
- Avant de vendre, donner ou jeter un ordinateur ou un téléphone, sauvegardez vos données puis réinitialisez-le complètement, pour que personne ne puisse récupérer vos fichiers

### 🪟 Windows

- Verrouillez l’écran avec **Windows + L**
- Pour éteindre, choisissez **Démarrer > Marche/Arrêt > Arrêter** plutôt que la mise en veille
- Pour reprendre votre travail sans tout rouvrir, la veille prolongée protège autant que l’arrêt. Activez-la dans **Panneau de configuration > Options d’alimentation > Choisir l’action des boutons d’alimentation**, : cliquez sur « Modifier des paramètres actuellement non disponibles », cochez « Veille prolongée », puis choisissez « Mettre en veille prolongée » dans le menu Marche/Arrêt.
- Affichez les extensions de fichiers : dans l’Explorateur de fichiers, **Afficher > Afficher > Extensions de noms de fichiers**
- Laissez Microsoft Defender activé et n’installez pas un second antivirus : deux antivirus actifs en même temps peuvent entrer en conflit et ralentir l’ordinateur

### 🍎 macOS

- Verrouillez l’écran avec **Ctrl + Cmd + Q**
- Pour éteindre, choisissez **menu Pomme > Éteindre** plutôt que la suspension d’activité
- Affichez les extensions de fichiers : **Finder > Réglages > Avancés**, cochez « Afficher toutes les extensions de fichiers »

### 🐧 Linux

- Verrouillez l’écran avec **Ctrl + Alt + L** (Linux Mint) ou **Super + L** (GNOME, sous Debian ou Ubuntu)
- Pour éteindre, utilisez le menu du bureau ou la commande `sudo poweroff`
- N’utilisez pas le compte root au quotidien ; servez-vous de `sudo` uniquement si nécessaire
- Installez vos mises à jour avec le gestionnaire de mises à jour, qui couvre aussi les applications Flatpak, et vos logiciels depuis le gestionnaire de logiciels de votre distribution (dépôts officiels) plutôt que depuis des sites web

---

## 🚨 Que faire en cas de problème ?

Même bien protégé, on peut être victime d’une attaque. Les bons réflexes limitent les dégâts. Soyez attentif aux signes d’alerte : ordinateur soudain très lent, fichiers renommés ou illisibles, message réclamant une rançon, mot de passe qui ne fonctionne plus, alerte de connexion inconnue ou paiement que vous n’avez pas fait.

> **Pour se faire aider :** 17Cyber (17cyber.gouv.fr) est le service public gratuit d’assistance aux victimes, accessible 24 h/24. Un questionnaire identifie votre problème et vous indique quoi faire. Si nécessaire, vous échangez en ligne avec un policier ou un gendarme, et vous pouvez être mis en relation avec un professionnel près de chez vous (son intervention peut être payante).

### 🦠 Si votre ordinateur semble infecté (virus, rançongiciel)

> **Attention :** si vos fichiers sont renommés ou changent d’icône sous vos yeux, un rançongiciel est en train de les chiffrer. Coupez aussitôt l’alimentation (bouton d’alimentation maintenu une dizaine de secondes, ou prise débranchée) pour sauver les fichiers restants. Sinon, suivez les étapes ci-dessous.

1. Débranchez immédiatement vos disques de sauvegarde et vos clés USB, et ne les reconnectez pas à cet ordinateur
2. Déconnectez-le d’Internet : coupez le Wi-Fi ou débranchez le câble réseau
3. Ne l’éteignez pas et ne le redémarrez pas : la mémoire de l’ordinateur peut contenir des traces de l’attaque, utiles si un professionnel intervient
4. Ne payez jamais de rançon : rien ne garantit la récupération de vos fichiers, et vous financez les criminels
5. Faites-vous aider sur 17cyber.gouv.fr et portez plainte (commissariat ou gendarmerie)
6. Une fois l’ordinateur nettoyé ou réinstallé, restaurez vos fichiers depuis votre sauvegarde, puis changez vos mots de passe

### 🔓 Si l’un de vos comptes est piraté

- Depuis un appareil sain (l’appareil piraté peut enregistrer ce que vous tapez), changez immédiatement le mot de passe de ce compte, ainsi que celui de tous les comptes qui utilisaient le même
- Si vous ne pouvez plus vous connecter, utilisez la procédure « mot de passe oublié » ou « compte piraté » du service concerné
- Activez la 2FA et déconnectez toutes les sessions ouvertes (option souvent appelée « Se déconnecter de tous les appareils »)
- Vérifiez les réglages du compte : adresse et téléphone de récupération, transferts automatiques d’e-mails, appareils connectés
- Prévenez vos contacts si des messages ont été envoyés en votre nom

### 💳 Si vous êtes victime d’une fraude bancaire

- Faites immédiatement opposition auprès de votre banque (application, site ou numéro indiqué au dos de votre carte)
- Si vous avez toujours votre carte, signalez les paiements frauduleux en ligne sur Perceval (service-public.fr) : le récépissé facilite le remboursement par votre banque
- Votre banque doit vous rembourser un paiement que vous n’avez pas autorisé, au plus tard le jour ouvrable qui suit votre signalement, sauf si elle prouve une négligence grave de votre part ou soupçonne une fraude de votre part (articles L133-18 et L133-19 du Code monétaire et financier). Signalez l’opération au plus vite, et au plus tard 13 mois après le débit (article L133-24).
- Portez plainte (commissariat ou gendarmerie)

### 📣 Signalez les arnaques

Vos signalements permettent de faire bloquer les numéros et les sites frauduleux, et d’alerter d’autres victimes potentielles.

- SMS frauduleux : transférez-les gratuitement au 33700
- E-mails d’hameçonnage : signalez-les sur signal-spam.fr
- Sites ou contenus illicites : signalez-les sur internet-signalement.gouv.fr (Pharos)

---

## ✅ Récapitulatif : liste de vérification

- [ ] Les mises à jour automatiques sont activées et mon système est encore pris en charge
- [ ] L’antivirus intégré est actif (Microsoft Defender sous Windows)
- [ ] Mon mot de passe de session est long et unique (ou une phrase secrète)
- [ ] J’utilise un gestionnaire de mots de passe, et mon kit de secours papier est rangé en lieu sûr
- [ ] La 2FA (ou une clé d’accès) protège ma messagerie et ma banque, et ses codes de secours sont conservés
- [ ] J’utilise un compte standard au quotidien, et chaque membre du foyer a son propre compte
- [ ] Le verrouillage automatique de l’écran est configuré
- [ ] Le disque est chiffré
- [ ] Mes fichiers sensibles ne sont pas synchronisés dans le cloud, ou ils y sont chiffrés (Cryptomator)
- [ ] Mon navigateur est à jour et ne contient que les extensions nécessaires
- [ ] Les extensions de fichiers sont affichées (Windows et macOS)
- [ ] Le pare-feu est activé, ma box utilise le WPA2 ou le WPA3, et son mot de passe d’administration a été changé
- [ ] Ma box ou mon ordinateur utilise un DNS filtrant (Quad9)
- [ ] En déplacement, je désactive le Wi-Fi et le Bluetooth quand je ne m’en sers pas
- [ ] Mon smartphone est verrouillé par un code et à jour
- [ ] Je sauvegarde régulièrement sur un disque externe, que je débranche ensuite, et j’ai déjà testé la restauration d’un fichier
- [ ] Je sais où trouver de l’aide en cas de problème (17cyber.gouv.fr)

---

## 📋 Annexe : correspondance avec les 42 mesures de l’ANSSI

Le guide d’hygiène informatique de l’ANSSI (« Renforcer la sécurité de son système d’information en 42 mesures », 2017) s’adresse aux entreprises et aux administrations. Les tableaux ci-dessous, classés selon les chapitres de ce guide, indiquent où chaque mesure applicable à un particulier est traitée ici (intitulés abrégés).

#### Sensibiliser et connaître son système

| Mesure de l’ANSSI | Dans ce guide |
|---|---|
| 2 — Sensibiliser aux bonnes pratiques | L’ensemble du guide |
| 4 — Identifier les informations sensibles | 2.5 Comptes en ligne et 2.8 Sauvegardes (repérer vos données importantes) |
| 5 — Inventorier les comptes privilégiés | 2.3 Mots de passe et accès (liste de vos comptes, compte administrateur) |
| 7 — N’autoriser que des équipements maîtrisés sur le réseau | 2.7 Réseau (Wi-Fi invité) |

#### Authentifier et contrôler les accès

| Mesure de l’ANSSI | Dans ce guide |
|---|---|
| 8 — Distinguer les rôles utilisateur et administrateur | 2.3 Mots de passe et accès et 4.2 Habitudes (compte standard, un compte par personne) |
| 10 — Règles de choix des mots de passe | 2.3 Mots de passe et accès (entropie, phrase secrète) |
| 11 — Protéger les mots de passe stockés | 2.3 Mots de passe et accès (gestionnaire, kit de secours) |
| 12 — Changer les identifiants par défaut | 2.7 Réseau (box, objets connectés) |
| 13 — Privilégier une authentification forte | 2.3 Mots de passe et accès (2FA, clés d’accès) |

#### Sécuriser les appareils

| Mesure de l’ANSSI | Dans ce guide |
|---|---|
| 14 — Niveau de sécurité minimal des appareils | 2.2 Antivirus, 2.6 Navigation (extensions) et 4.2 Habitudes (logiciels inutiles) |
| 15 — Supports amovibles | 4.2 Habitudes et 5.1 Ordinateur infecté (clés USB) |
| 17 — Pare-feu local | 2.7 Réseau (pare-feu) |
| 18 — Chiffrer les données transmises par Internet | 2.6 Navigation (HTTPS), 2.8 Sauvegardes (Cryptomator) et 4.1 Réflexes en ligne (Signal) |

#### Sécuriser le réseau

| Mesure de l’ANSSI | Dans ce guide |
|---|---|
| 19 — Cloisonner le réseau | 2.7 Réseau (Wi-Fi invité) |
| 20 — Sécurité du Wi-Fi | 2.7 Réseau (box et Wi-Fi) |
| 21 — Protocoles sécurisés | 2.6 Navigation (HTTPS) et 2.7 Réseau (DNS chiffré) |
| 24 — Protéger sa messagerie | 2.3 Mots de passe et accès (2FA) et 4.1 Réflexes en ligne (hameçonnage) |

#### Administration et déplacements

| Mesure de l’ANSSI | Dans ce guide |
|---|---|
| 29 — Limiter les droits d’administration | 2.3 Mots de passe et accès et 4.2 Habitudes (compte standard) |
| 30 — Sécurité physique des appareils nomades | 4.2 Habitudes (surveillance, verrouillage) |
| 31 — Chiffrer le matériel qui peut être perdu | 2.4 Chiffrement du disque et 2.9 Smartphone |
| 32 — Connexion réseau en déplacement | 2.7 Réseau (en déplacement) |
| 33 — Smartphones et tablettes | 2.9 Smartphone |

#### Mises à jour, sauvegardes et incidents

| Mesure de l’ANSSI | Dans ce guide |
|---|---|
| 34 — Politique de mise à jour | 2.1 Mises à jour |
| 35 — Anticiper la fin de maintenance | 2.1 Mises à jour (Windows 10) et 3 Linux |
| 37 — Sauvegardes | 2.8 Sauvegardes |
| 38 — Contrôles réguliers | 2.3 Mots de passe et accès (fuites de données) et 6 Liste de vérification |
| 39 — Référent en sécurité | 5 En cas de problème (17Cyber) |
| 40 — Gestion des incidents | 5 En cas de problème |

#### Mesures écartées volontairement

Ces mesures concernent l’organisation d’une entreprise ou d’une administration : formation des équipes (1), infogérance (3), arrivées et départs du personnel (6), droits sur les ressources partagées (9), gestion centralisée des postes (16), passerelle Internet, services exposés et interconnexions avec des partenaires (22, 23 et 25), salles serveurs (26), postes et réseau d’administration (27 et 28), journaux d’événements (36), analyse de risques formelle (41) et produits qualifiés par l’ANSSI (42).
