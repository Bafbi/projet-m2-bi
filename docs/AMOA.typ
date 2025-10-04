// ===============================================
// PREAMBLE: Document Setup and Styling
// ===============================================

// Set document properties. Using French for proper hyphenation.
#set document(
  title: "Fiche d'expertise",
  author: "Groupe de Travail",
)

// Set the main font for the document.
// Calibri is a good match for the original PDF. If you don't have it,
// Typst will fall back to another sans-serif font like "Arial".
#set text(font: "New Computer Modern", size: 11pt, lang: "fr")

// Define the custom blue color used for headings.
#let custom-blue = rgb(1, 41, 105)

// Define custom styles for level 1 and 2 headings.
// They will be bold, blue, and underlined, without a number.
#show heading.where(level: 1): it => {
  v(1.5em, weak: true)
  set text(weight: "bold", fill: custom-blue)
  underline(it.body)
  v(0.8em, weak: true)
}

#show heading.where(level: 2): it => {
  v(1.2em, weak: true)
  set text(weight: "bold", fill: custom-blue)
  underline(it.body)
  v(0.6em, weak: true)
}

// ===============================================
// TITLE PAGE with TABLE OF CONTENTS at the bottom
// ===============================================

// We use the page() function to define a custom layout for the first page.
// The main content (title) goes in the body, and the TOC goes in the footer.
#page(
  // The footer will contain our table of contents.
  footer-descent: -25em,
  footer: [
    #outline(
      title: align(center)[SOMMAIRE],
      depth: 2,
      indent: auto
    )
  ],
  // The body contains the title, vertically centered.
  align(center)[
    #v(8em)
    #text(16pt, weight: "bold")[Fiche d'expertise - Big Data dans le secteur des Médias]
    #v(1.5em)
    #text(14pt, style: "italic")["Apport du Big Data pour la direction de la programmation d'une chaîne de vidéo à la demande"]
  ]
)

#pagebreak()

// The content starts on page 3, as in the PDF.
#counter(page).update(3)


// ===============================================
// DOCUMENT CONTENT
// ===============================================
// Use `=` for main headings (level 1) and `==` for subheadings (level 2).
// The outline will automatically pick them up.
// ===============================================

= Introduction <intro>
== But du document
Cette fiche a pour but de présenter une analyse d'expertise sur l'apport du Big Data pour la société BigMedia. Elle vise à définir une stratégie pour exploiter les données des utilisateurs, valoriser le projet de plateforme Big Data auprès des directions métiers, et proposer une démarche pour convaincre la direction de la production d'investir dans le projet.

== Définition
Dans le contexte de BigMedia, le Big Data désigne l'ensemble des données volumineuses et variées (structurées et non structurées) générées par la consommation de contenus à la demande et les interactions sur les réseaux sociaux. L'enjeu est de les exploiter pour en tirer des informations décisionnelles à forte valeur ajoutée.

= Concepts generaux <concepts>
== Compréhension du contexte
BigMedia est une chaîne de télévision française à diffusion nationale, destinée à la jeunesse. Créée en 2008, la chaîne est proposée sur la TNT gratuite ainsi que sur le web en diffusion linéaire. Après de lourdes pertes de marché, la chaîne a souhaité revoir son positionnement et propose un service gratuit de vidéo à la demande (VoD) depuis l'année dernière.
La chaîne produit également ses propres séries d'animation, proposant ainsi des contenus exclusifs à ses utilisateurs.

La VoD et les contenus exclusifs sont accessibles de façon indifférenciée depuis :
- Une télévision connectée, soit par connexion intégrée, soit par interface dédiée (Apple TV ou Chromecast), soit par un terminal classique (box, câble, satellite)
- Un PC possédant une connexion à Internet
- Un smartphone ou une tablette ayant un accès réseau mobile haut débit (3G/4G) ou en Wi-Fi
- Une console de jeux connectée (XBOX 360 ou One, Playstation 3 ou 4)

== Compréhension de la problématique
Malgré son repositionnement sur la VoD, BigMedia peine à gagner des parts de marché. La DSI souhaite lancer un projet de plateforme Big Data pour exploiter les données des utilisateurs (consommation, commentaires, likes) afin de mieux comprendre l'audience et d'améliorer la performance.

Le projet fait face à deux défis majeurs :
1.  *Un contexte économique contraignant* : La DSI doit faire financer le projet par les directions métiers.
2.  *Une hésitation des directions métiers* : La direction de la production, en particulier, perçoit le projet comme un centre de coût et non comme une source de valeur, et hésite à s'impliquer.

L'enjeu principal est donc de valoriser le projet en démontrant son retour sur investissement potentiel pour les directions de la programmation, de la publicité et de la production afin de sécuriser leur adhésion et leur financement.

== Enjeux et objectifs
Pour répondre à ces enjeux, BigMedia souhaite faire évoluer son système d'information décisionnel. Les objectifs stratégiques de l'exploitation des données sont :
- *Fidéliser les utilisateurs du service* grâce à une connaissance client accrue, en leur proposant des contenus adaptés.
- *Cibler de nouveaux consommateurs* en améliorant la performance de ses productions originales.
- *Exploiter des données déstructurées* telles que les commentaires, les likes, ou autres données postées sur les réseaux sociaux.

== Finalités
La finalité du projet est de transformer BigMedia en une organisation "data-driven". L'objectif est d'utiliser les données pour optimiser l'ensemble de la chaîne de valeur :
- L'acquisition de programmes (politique d'achat).
- La création de contenus originaux (séries d'animation).
- La monétisation via la publicité ciblée.

À terme, cela doit permettre d'améliorer la compétitivité et la rentabilité de la chaîne sur les supports connectés.

== Aspects Juridiques
La collecte et le traitement des données personnelles des utilisateurs sont strictement encadrés par le Règlement Général sur la Protection des Données (RGPD), entré en vigueur le 25 mai 2018. #cite(<cnil-mineurs>) #cite(<cnil-majorite-numerique>) Le respect de ce cadre légal est impératif pour garantir la conformité du projet, protéger la vie privée des utilisateurs et éviter de lourdes sanctions.

*Principes fondamentaux du RGPD*
Tout traitement de données doit reposer sur des bases légales claires. #cite(<cnil-bases-legales>) Pour BigMedia, la base la plus pertinente sera le consentement de l'utilisateur. Ce consentement doit être :
- *Libre* : L'utilisateur doit avoir un véritable choix, sans subir de conséquences négatives en cas de refus. #cite(<cnil-consentement>)
- *Spécifique* : Le consentement doit être donné pour des finalités déterminées. Si les données sont utilisées pour plusieurs objectifs, l'utilisateur doit pouvoir consentir indépendamment à chacun. #cite(<cnil-consentement>)
- *Éclairé* : L'utilisateur doit recevoir une information claire sur l'identité du responsable de traitement, les finalités de la collecte et ses droits. #cite(<cnil-consentement>)
- *Univoque* : Le consentement doit résulter d'un acte positif clair, comme une case à cocher (non pré-cochée). L'inactivité ou le silence ne valent pas consentement. #cite(<cnil-consentement>)

*Protection spécifique des mineurs*
Le public de BigMedia étant la jeunesse, une attention particulière doit être portée à la protection des données des mineurs, considérés comme plus vulnérables. #cite(<haas-avocats-mineurs>) #cite(<cnil-mineurs>) En France, l'âge de la "majorité numérique" est fixé à 15 ans. #cite(<cnil-majorite-numerique>) #cite(<haas-avocats-mineurs>)
- Pour les utilisateurs de moins de 15 ans, le traitement des données n'est licite que si le consentement est donné conjointement par le mineur et le titulaire de l'autorité parentale. #cite(<cnil-mineurs>) #cite(<haas-avocats-mineurs>)
- BigMedia aura l'obligation de mettre en œuvre des efforts raisonnables pour vérifier l'âge de l'utilisateur et l'obtention de cette autorisation parentale. #cite(<haas-avocats-mineurs>)

*Collecte de données sur les réseaux sociaux*
Le fait que des données (commentaires, likes) soient publiquement accessibles sur les réseaux sociaux ne les exclut pas du champ du RGPD. #cite(<cnil-reseaux-sociaux>) Leur collecte et leur traitement par BigMedia doivent également reposer sur une base légale valide et les utilisateurs doivent être informés de cette utilisation. #cite(<cnil-reseaux-sociaux>)

*Anonymisation et Pseudonymisation*
Pour les analyses statistiques et la compréhension des tendances d'audience, il est crucial de distinguer deux techniques :
- *L'anonymisation* : C'est un processus irréversible qui rend impossible toute ré-identification de la personne. #cite(<cnil-anonymisation>) #cite(<cnil-anonymisation-pseudo>) Des données correctement anonymisées ne sont plus considérées comme des données personnelles et sortent du champ d'application du RGPD. #cite(<cnil-anonymisation-pseudo>) #cite(<cnil-donnees-anonymes>) C'est la cible à privilégier pour les analyses globales.
- *La pseudonymisation* : Ce procédé remplace les données directement identifiantes (comme un nom) par un pseudonyme (comme un alias). #cite(<cnil-anonymisation-pseudo>) Cependant, la ré-identification reste possible à l'aide d'informations supplémentaires. Les données pseudonymisées sont donc toujours des données personnelles soumises au RGPD. #cite(<cnil-anonymisation-pseudo>) #cite(<cnil-anonymisation>)

En conclusion, une démarche de conformité rigoureuse ("privacy by design") doit être intégrée dès le début du projet, notamment via la mise en place de processus clairs pour le recueil du consentement, la vérification de l'âge, et l'anonymisation des données destinées à l'analyse.

== Axe méthodologiques
L'axe méthodologique principal consiste à proposer une démarche pragmatique pour démontrer la valeur du projet et limiter les risques.
- Proposer une méthodologie de mise en place d'un *POC (Proof of Concept)*, permettant de valider le concept à échelle réduite et de convaincre la direction de la production d'investir dans le projet à plus grande échelle.

= Le marché des Big Data <marche>
== Les éditeurs et leurs outils
L'étude devra identifier les typologies d'outils Analytics nécessaires pour répondre aux besoins, notamment :
- Outils de collecte de données (ETL/ELT).
- Bases de données adaptées au Big Data (Data Lake, Data Warehouse).
- Outils d'analyse et de traitement du langage naturel (NLP) pour les commentaires.
- Plateformes de Data Visualisation (Tableau, Power BI, etc.) pour créer les tableaux de bord.

== Technologies et architectures
L'architecture cible devra être une plateforme Big Data transverse, capable de collecter, stocker et traiter :
- *Des données structurées* : logs de lecture des vidéos, parcours utilisateur, etc.
- *Des données déstructurées* : commentaires sur la plateforme, mentions et likes sur les réseaux sociaux, etc.
Il faudra également identifier les sources de données existantes et/ou à cibler qui pourront alimenter cette nouvelle base.

== Les clients potentiels
Les clients de ce projet sont internes à BigMedia. Le succès du projet repose sur sa capacité à répondre à leurs besoins spécifiques :
- *La direction de la programmation* : Pour optimiser la grille, la sélection des programmes et la politique d'achat.
- *La direction de la production* : Pour orienter la création des séries originales en fonction des préférences de l'audience.
- *La direction de la publicité* : Pour affiner le ciblage publicitaire et améliorer la monétisation des contenus.

== Matrice SWOT #cite(<swot>)


#image("MSwot.png")

= Notre, démarche <demarche>
Pour répondre à la problématique de BigMedia, nous proposons la démarche suivante, structurée en plusieurs étapes clés :

- *1. Analyse Stratégique* :
  Définir les avantages, contraintes et risques du Big Data pour la direction de la programmation à l'aide d'une Matrice SWOT.

- *2. Identification des Données et KPIs* :
  - Identifier les sources de données (existantes et à cibler) qui alimenteront la plateforme.
  - Identifier des axes d'analyse et des KPIs pertinents à créer et à suivre pour optimiser les prises de décisions.

- *3. Conception de Tableaux de Bord* :
  Identifier et maquetter des tableaux de bord utilisant ces KPIs, notamment pour le responsable du département Production, afin de matérialiser la valeur ajoutée.

- *4. Proposition d'un POC* #cite(<repo>) :
== Proposition d'un POC <poc> 

Objectif: démontrer rapidement la valeur d’une chaîne data de bout en bout pour la programmation/production, avec 1–2 indicateurs métier visibles dans un tableau de bord.

- Périmètre: environnement BigQuery « dev », petit échantillon de données, un modèle métier minimal, un dashboard simple.
- Architecture: Prefect Cloud (orchestration), dbt (transformation et tests), BigQuery (stockage/compute), Terraform/OpenTofu (provisionnement), Power BI (visualisation en DirectQuery).
- Données: échantillon de logs de visionnage et/ou interactions sociales; modèles d’exemple dbt étendus d’un modèle agrégé « contenu × période ».
- KPIs (exemples): taux de complétion par contenu/device, popularité (vues/likes) normalisée, DAU/rétention (si données suffisantes).
- Déroulé: provisionner l’infra → configurer le profil dbt → planifier une exécution quotidienne orchestrée → publier un dashboard lisible par les métiers.
- Succès: runs quotidiens au vert, tests de base OK, KPIs consultables, retour positif des utilisateurs métier.
- Budget: faible (principalement temps d’ingénierie).



// = Annexe <annexe>

#bibliography("webographie_amoa.yml", title: "Webographie")