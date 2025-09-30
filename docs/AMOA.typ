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
#set text(font: ("Monaspace Xenon NF","New Computer Modern"), size: 11pt, lang: "fr")

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
// Cette section devra être complétée.
// Il conviendra d'analyser les aspects juridiques liés à la collecte
// et au traitement des données personnelles (RGPD), notamment le
// consentement des utilisateurs et l'anonymisation des données pour l'analyse.

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


#image("graphs/matrice_swot_amoa.png")
= Notre, démarche <demarche>
Pour répondre à la problématique de BigMedia, nous proposons la démarche suivante, structurée en plusieurs étapes clés :

- *1. Analyse Stratégique* :
  Définir les avantages, contraintes et risques du Big Data pour la direction de la programmation à l'aide d'une Matrice SWOT.

- *2. Identification des Données et KPIs* :
  - Identifier les sources de données (existantes et à cibler) qui alimenteront la plateforme.
  - Identifier des axes d'analyse et des KPIs pertinents à créer et à suivre pour optimiser les prises de décisions.

- *3. Conception de Tableaux de Bord* :
  Identifier et maquetter des tableaux de bord utilisant ces KPIs, notamment pour le responsable du département Production, afin de matérialiser la valeur ajoutée.

- *4. Proposition d'un POC* :


// = Annexe <annexe>

#bibliography("webographie_amoa.yml", title: "Webographie")