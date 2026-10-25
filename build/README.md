# Génération du guide, des fiches et du site

Le PDF `securiser-votre-ordinateur-personnel.pdf`, les trois fiches pratiques du dossier `fiches/` et le site web (`index.html`, `404.html`, `sitemap.xml` et le dossier `guide/`) sont entièrement générés à partir du Markdown. Ne modifiez jamais un PDF ou une page générée à la main : modifiez le Markdown (ou le gabarit de la page), puis relancez la génération.

## Tout générer

Depuis le dossier du guide, cette commande produit le guide, les trois fiches et le site :

```sh
./build/build.sh
```

La première fois, le script crée un environnement Python dans `~/.cache/securiser-votre-ordinateur/venv` et y installe les dépendances (connexion Internet nécessaire). Il les réinstalle de lui-même quand `requirements.txt` change. Les fois suivantes, la génération prend quelques secondes.

L'environnement est placé hors du dossier du guide : sur un disque externe, il occuperait près de 700 Mo et se couvrirait de fichiers cachés `._*`. Pour le placer ailleurs : `BUILD_VENV=/chemin/vers/venv ./build/build.sh`.

Options :

```sh
./build/build.sh autre-guide.md sortie.pdf        # un seul document, avec d'autres fichiers d'entrée et de sortie
./build/build.sh --html /tmp/guide.html           # le guide seul, en enregistrant aussi le HTML intermédiaire
```

Pour regarder le site avant de le publier, lancez un petit serveur web depuis le dossier du guide, puis ouvrez <http://localhost:8000/> :

```sh
python3 -m http.server 8000
```

Les liens entre les pages mènent à des dossiers (`guide/mots-de-passe/`) : ouvert directement depuis le Finder, le site afficherait le contenu de ces dossiers au lieu des pages. Seule la page 404, dont les liens partent de l'adresse du site publié, ne s'affiche correctement qu'une fois en ligne.

## Contrôler le code

Après une modification des scripts, lancez :

```sh
./build/check.sh            # shellcheck, pylint, puis les tests
./build/check.sh -k fiche   # seulement les tests dont le nom contient « fiche »
```

Le script installe aussi les outils de `requirements-dev.txt`, puis vérifie les scripts shell (shellcheck) et le code Python (pylint, avec ses réglages par défaut : la note doit rester à 10/10), avant de lancer les tests du dossier `tests/` (pytest). Il s'arrête à la première erreur. Les tests écrivent leurs PDF dans un dossier temporaire : ils ne modifient jamais les PDF du guide.

## Les fiches pratiques

| Fiche | Source | Contenu |
|---|---|---|
| `fiches/fiche-1-bien-demarrer.pdf` | Extraite du guide | Les 5 priorités (encadré « Par où commencer »), le kit de secours et la liste de vérification |
| `fiches/fiche-2-bons-reflexes.pdf` | Extraite du guide | La partie « Les bons réflexes en ligne », les encadrés sur les fausses alertes de virus et sur le cadenas, et « Signalez les arnaques » |
| `fiches/fiche-3-en-cas-d-urgence.pdf` | `fiches/fiche-urgence.md` | Version condensée du chapitre 5 « Que faire en cas de problème ? » et contacts utiles |

- **Fiches 1 et 2 :** `build_fiches.py` copie mot pour mot ces passages du guide, en les retrouvant par leur titre ou par le début de leur encadré. Elles se mettent donc à jour toutes seules. Si vous renommez l'un de ces titres ou modifiez le début de l'un de ces encadrés, mettez aussi à jour `build_fiches.py` : le script s'arrête avec un message qui indique le passage introuvable.
- **Fiche 3 :** son texte est rédigé à part, car le chapitre 5 est trop long pour une page. **Quand vous modifiez le chapitre 5 du guide, reportez la modification dans `fiches/fiche-urgence.md`.**
- Chaque fiche tient sur une feuille recto-verso.

## Le site web

`build_site.py` met le guide en ligne, page par page, avec la même mise en forme que le PDF (encadrés, chemins de menus, touches, étapes numérotées).

| Page | Adresse | Contenu |
|---|---|---|
| Accueil | `index.html` | Gabarit `build/accueil.html`, complété par la version, la date, le nombre de pages du PDF, le sommaire et les 5 priorités de l'encadré « Par où commencer » (chacune reliée à sa page) |
| Sommaire | `guide/` | Chaque chapitre et chaque partie, reliés à leur page |
| Pages du guide | `guide/mots-de-passe/`… | Une page par chapitre ; le chapitre « Les bases », trop long, a une page par partie |
| Page 404 | `404.html` | Affichée par GitHub Pages pour une adresse inconnue |
| Plan du site | `sitemap.xml` | L'adresse de chaque page, pour les moteurs de recherche (voir « Référencement ») |

Les pages du guide, le sommaire et la page 404 suivent le gabarit `build/page.html`. `site.css` (mise en page, thème clair et sombre, impression) et `site.js`, à la racine du guide, sont écrits à la main et publiés tels quels.

- **Adresses des pages.** Chaque page a une adresse fixe, choisie dans `PAGES` en haut de `build_site.py` d'après le titre de son chapitre ou de sa partie, avec le nom court affiché dans le menu. Ces adresses sont partagées et imprimées : **ne les changez jamais**. Si vous renommez un titre, renommez sa clé dans `PAGES` sans toucher à l'adresse ; si vous ajoutez un chapitre ou une partie, ajoutez-lui une adresse. Le script s'arrête avec un message qui nomme le titre sans adresse, ou l'entrée de `PAGES` qui ne correspond plus à aucun titre.
- **Une page par partie.** Les chapitres de `SPLIT` (« Les bases ») ont une page par partie : ils doivent commencer directement par un titre `###`, sans texte d'introduction.
- **Renvois.** Les renvois numérotés (« voir 2.3 ») deviennent des liens vers la partie visée, comme les renvois écrits en toutes lettres de `NAMED_REFS` (« la partie Linux »).
- **Encadrés système.** Sur les pages qui en ont, le lecteur choisit son système (Windows, macOS ou Linux) : les encadrés des autres systèmes se replient, et il peut toujours les rouvrir. Son choix vaut pour toutes les pages.
- **Liste de vérification.** Les cases se cochent et restent cochées d'une visite à l'autre.
- **Vie privée.** Le système choisi et les cases cochées restent dans le navigateur du lecteur (`localStorage`) : le site n'a ni cookie, ni mesure d'audience, ni ressource externe. Sans JavaScript, toutes les instructions restent affichées et les cases se cochent, sans être retenues.
- **Mise en cache.** Les pages appellent `site.css` et `site.js` avec une empreinte de leur contenu (`site.css?v=…`) : après une modification de ces fichiers, relancez la génération, pour que les navigateurs chargent la nouvelle version.
- **Politique de sécurité du contenu (CSP).** GitHub Pages ne permet pas d'envoyer d'en-têtes de sécurité : chaque page déclare donc sa CSP dans une balise `<meta>` (`CSP` en haut de `build_site.py`). Une page ne charge que les fichiers du site et n'exécute que `site.js`, plus une ligne placée en tête des pages du guide (`EARLY_JS`), autorisée par son empreinte, qui affiche le choix du système avant le premier affichage, sans décaler la page. N'ajoutez ni style ni script écrit dans une page, ni ressource externe (police, image, statistiques) : le navigateur les bloquerait, et `check.sh` le signale.

### Référencement

Un site de projet GitHub (`casanova-mateo.github.io/securiser-votre-ordinateur/`) ne peut pas avoir de `robots.txt` : ce fichier doit être à la racine du domaine, qui ne dépend pas de ce dépôt. Le plan du site se déclare donc directement auprès des moteurs de recherche, une fois pour toutes :

1. Sur [Google Search Console](https://search.google.com/search-console), ajoutez une propriété de type « Préfixe de l'URL » : `https://casanova-mateo.github.io/securiser-votre-ordinateur/`.
2. Choisissez la validation par « Fichier HTML » : téléchargez le fichier `google….html` proposé, placez-le à la racine du dépôt (à côté de `index.html`, la génération n'y touche pas), commitez, envoyez, puis cliquez sur « Valider ».
3. Dans « Sitemaps », envoyez `sitemap.xml`. Google relit ensuite le plan du site de lui-même à chaque mise à jour.
4. Facultatif : dans [Bing Webmaster Tools](https://www.bing.com/webmasters), « Importer depuis Google Search Console » couvre aussi Bing, DuckDuckGo et Ecosia.

## Publier une nouvelle version

Le site <https://casanova-mateo.github.io/securiser-votre-ordinateur/> est publié par GitHub Pages à partir de la branche `main` : chaque `git push` le met à jour en une ou deux minutes.

1. Modifiez le Markdown, puis changez en haut de `build_pdf.py` la version `VERSION` (1.1 pour des corrections, 2.0 pour une refonte) et sa date `RELEASE_DATE`.
2. Lancez `./build/build.sh` et feuilletez les PDF et le site. Si vous avez modifié les scripts, lancez aussi `./build/check.sh`. La version, la date et le nombre de pages du PDF se mettent à jour d'eux-mêmes sur le site.
3. Dans le `README.md` du dossier principal, ajoutez la version à l'historique.
4. Commitez, puis envoyez : `git push`.
5. Sur GitHub, créez une release `vX.Y` (onglet Releases) et joignez-y les quatre PDF : les versions précédentes restent ainsi téléchargeables.

## Prérequis (macOS)

- Python 3.10 ou plus récent (`python3`)
- La bibliothèque pango, utilisée par WeasyPrint : `sudo port install pango` (MacPorts) ou `brew install pango` (Homebrew)
- Les polices Avenir Next et Menlo, fournies avec macOS

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `build.sh` | Lanceur : prépare l'environnement Python puis lance les scripts |
| `check.sh` | Contrôle du code : shellcheck, pylint, puis les tests |
| `env.sh` | Partagé par les deux lanceurs : environnement Python (mis à jour quand les dépendances changent) et bibliothèque pango |
| `build_pdf.py` | Convertit le Markdown en HTML mis en forme, puis en PDF (option `--fiche` pour la mise en page des fiches) |
| `build_fiches.py` | Assemble le Markdown des trois fiches et les met en page avec `build_pdf.py` (option `--out-dir` pour écrire les PDF ailleurs que dans `fiches/`) |
| `build_site.py` | Découpe le guide mis en forme par `build_pdf.py` en pages web, puis écrit le site (option `--out-dir` pour l'écrire ailleurs que dans le dossier du guide) |
| `accueil.html`, `page.html` | Gabarits de l'accueil et des autres pages du site (les `$nom` sont remplis par `build_site.py`) |
| `style.css` | Mise en page du PDF : couverture, couleurs, polices, en-têtes, encadrés |
| `rule.svg` | Filet sous l'en-tête de chaque page |
| `requirements.txt` | Versions exactes des bibliothèques Python utilisées, dépendances indirectes comprises |
| `requirements-dev.txt` | Versions exactes des outils de contrôle (pylint, pytest, shellcheck) |
| `tests/` | Tests de la mise en page (`test_build_pdf.py`), de l'assemblage des fiches (`test_build_fiches.py`) et du site (`test_build_site.py`) |

## Conventions à respecter dans le Markdown

Le script reconnaît ces éléments et les met en forme automatiquement :

| Dans le Markdown | Dans le PDF |
|---|---|
| `# Titre` (obligatoire, une seule fois, en tête) | Titre de la couverture ; la ligne d'auteur juste en dessous, si elle est entièrement en italique, n'est pas reprise |
| `## Titre` | Chapitre numéroté (« 02 »), dans le sommaire et en en-tête de page |
| `### Titre` | Partie numérotée (« 2.1 »), dans le sommaire |
| `#### Windows`, `#### macOS`, `#### Linux` | Encadré coloré propre au système |
| `> **Exemple :** …` | Encadré bleu |
| `> **Pourquoi c'est important :** …`, `> **Par où commencer :** …` | Encadré bleu-vert |
| `> **Solution :** …`, `> **Pour se faire aider :** …` | Encadré vert |
| `> **Attention :** …` | Encadré orange |
| `**Paramètres > Comptes**` | Chemin de menu avec des flèches › |
| `**Ctrl + Alt + L**` | Touches de clavier dessinées |
| `1.`, `2.`, `3.` (hors citation) | Étapes numérotées dans des pastilles |
| `- [ ] …` | Case à cocher ; le chapitre qui contient la liste n'est jamais coupé entre deux pages |
| Tableau de 3 colonnes ou plus | Tableau comparatif, en plus petit |
| Tableau de plus de 12 lignes | Peut continuer sur la page suivante, avec l'en-tête répété (évitez-les : préférez plusieurs petits tableaux sous des titres `####`) |
| `## Annexe …` | Chapitre qui commence sur une nouvelle page |

Les emojis des titres sont retirés dans le PDF, et les espaces insécables de la typographie française sont ajoutés automatiquement.

## Points d'attention

- **Titres des encadrés.** Les encadrés sont reconnus par leur titre exact, défini dans `OS_HEADING` en haut de `build_pdf.py`. Ce sont « Windows », « macOS », « Linux », « Sécuriser votre session Windows/macOS », « Les bons réflexes en ligne » et « Les bonnes habitudes avec vos appareils ». Si vous renommez l'un de ces titres, mettez aussi `OS_HEADING` à jour.
- **Titres des chapitres et des parties.** Le site retrouve la page de chacun par son titre exact, dans `PAGES` en haut de `build_site.py` (voir « Le site web »). L'encadré « Par où commencer », repris sur l'accueil, doit garder ce libellé et sa liste numérotée.
- **Nouveaux types d'encadrés.** Un libellé de citation inconnu s'affiche en bleu. Pour une autre couleur, ajoutez-le dans `CALLOUT_KIND`. Une citation qui ne commence pas par un libellé en gras s'affiche en bleu, sans titre.
- **Couverture.** Le sous-titre, l'auteur et la liste des thèmes se règlent en haut de `build_pdf.py`. La date (mois et année) est `RELEASE_DATE`.
- **Version, licence et adresse de téléchargement.** `VERSION`, `RELEASE_DATE`, `EDITION`, `LICENSE_NOTE` et `SITE_URL`, en haut de `build_pdf.py`. Changez `VERSION` et `RELEASE_DATE` à chaque nouvelle publication : tant qu'ils ne changent pas, régénérer les PDF sur la même machine donne exactement les mêmes fichiers. Tant que `SITE_URL` est vide, la ligne « Dernière version du guide et des fiches » n'est pas imprimée.
- **Ce qui n'est pas dans le Markdown :** la couverture, le sommaire, l'encadré « Repères », la ligne « Date de la dernière vérification », la quatrième de couverture du guide et la mention finale des fiches (version, licence, adresse). Tous sont produits par le script.
- **Langue.** Le script est prévu pour le guide français (libellés, typographie). La version anglaise demanderait d'adapter ces textes.
- **Mise en page.** Chaque titre (`##`, `###`, `####` ou titre d'encadré système) forme avec son contenu, jusqu'au titre suivant, un bloc jamais coupé entre deux pages : chaque page commence donc par un titre. Un titre suivi d'une courte introduction reste sur la même page que le bloc suivant. Les chapitres s'enchaînent sans saut de page, sauf les annexes. Conséquence : une section plus longue qu'une page entière ne peut pas tenir ; découpez-la avec des sous-titres `####`.
- **Vérification.** Après une modification importante, feuilletez le PDF pour repérer une page presque vide ou un encadré mal coupé. Une page remplie à moitié est normale quand la section suivante ne tient pas dans l'espace restant. Pour la réduire, découpez une longue section en sous-parties titrées.
