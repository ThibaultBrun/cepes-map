# 🍄 Chantier autonome — Carte à cèpes (cepes.tbrun.dev)

**Mandat** : Thibault m'a demandé (2026-10-18 01:04) de bosser en boucle jusqu'à **dimanche 18/10 ~11h00 Europe/Paris** pour sortir le meilleur résultat possible, style **champêtre & sexy**.

## Garde-fous
- Rester sur le projet cèpes uniquement. Aucune action destructive. Pas d'email/post externe.
- Déployer par incréments (chaque amélioration → live + testée par screenshot).
- Logguer chaque passe ci-dessous. Ne ping Thibault que sur milestones (pas de spam).
- **STOP à 11h00** : poster un récap final avec screenshots, puis supprimer le cron de self-wake.
- Commits éventuels : nuit 22h-01h, sans Co-Authored-By.

## Deadline
2026-10-18 11:00 Europe/Paris.

## Backlog (par priorité)
1. [FAIT] DA champêtre (Fraunces, palette bois/mousse, panneaux, radar restylé) + expo recoloré or.
2. [x] **Croisement strict** : voile doré uniquement SUR la forêt favorable (masque expo×forêt) → vraie couche "spots prime".
3. [x] **Points GBIF Boletus** (observations réelles) → calque validation + popup.
4. [x] **Couche "spots prime"** dédiée : parcelles score 3 ∩ versant sud → surbrillance + liste cliquable "meilleurs coins".
5. [x] **Essences 10 m** (essence10.tif PRÊT: ForestPaths genre arbre, codes Pinus=2 Fagus=3 Quercus=4 broadleaf=6) → calque raster scoré + affiner : Copernicus HRL (feuillu/conifère 10m) ou carte essences Sentinel pour affiner le score.
6. [x] Radar : prévoir la **fenêtre future** (indice sur les 7 j de prévi) + mini courbe pluie.
7. [x] Polish mobile : panel hero collapsible (☰ toggle) + bouton "📍 Où je suis" centré. Partage de spot (permalien) → à faire.
8. [x] Perf : clusters parkings MapLibre (4000 pts → cercles agrégés + count + zoom auto) + click expand.
9. [x] **Espèces GBIF colorées** : 4 couleurs distinctes par espèce (edulis=or, aereus=brun, pinophilus=rouille, reticulatus=ocre) + légende espèces + popup nom FR + nom latin.


## Repo & commits
- Repo: **ThibaultBrun/cepes-map** (public), dossier source `/home/debian/cepes`. Données générées = gitignored (reconstruites par build_*.py).
- Chaque passe : copier les sources modifiées dans ~/cepes, `git add -A`, commit **daté 22h-01h** (GIT_AUTHOR_DATE/COMMITTER_DATE=2026-10-18T00:5X:00), user.name 'Thibault Brun', **sans Co-Authored-By**, puis `git push`.

## Journal
- 2026-10-18 01:1x — Passe 0 : DA champêtre déployée, expo réchauffée (or), radar restylé. STATE+cron à armer.
- 2026-10-18 01:3x — Passe 1 : couche ✨ spots prime (sud ∩ forêt, 1.07M px) + 🍄 202 points GBIF (edulis/aereus/pinophilus/reticulatus) intégrés + légende MAJ.
- 2026-10-18 01:47 — Passe 2 : 🥇 panel "Meilleurs coins" (top-right, queryRenderedFeatures score=3, clickable flyTo+popup) + highlight gold foret-best layers + toggle + légende MAJ.
- 2026-10-18 01:57 — Passe 3 : 🌲 couche Essences 10m (Copernicus) : Quercus or/Fagus rouille/Feuillu vert/Pinus sombre → build_essence.py + tuiles /srv/www/cepes/essence (z9-13) + toggle + légende dynamique (affichée uniquement quand layer actif).
- 2026-10-18 02:10 — Passe 4 : 📊 radar fenêtre future — sparkline 7 barres pluie J+1..J+7 (couleur par intensité) + indice potentiel cèpes futur + push.json enrichi (forecast[] + score_future + rain_fut7).
- 2026-10-18 02:15 — Passe 5 : 📱 polish mobile — hero card collapsible (toggle ☰/⊕), bouton "📍 Où je suis" centré en bas + flyTo, push card repositionné.
- 2026-10-18 02:18 — Passe 6 : 🅿️ clusters parkings (4000 pts → agrégats couleur cuivre + count + click-to-expand).
- 2026-10-18 02:21 — Passe 7 : 🔗 partage de spot (clic droit → popup permalien hash URL + bouton copier).
- 2026-10-18 02:24 — Passe 8 : 🍄 écran d'intro splash (fond brun, typo Fraunces italic, bouton cuivre "Ouvrir la carte").
- 2026-10-18 02:32 — Passe 9 : 📥 export GPX — bouton "Exporter en GPX" dans le panel Meilleurs Coins → télécharge waypoints des top spots visibles, prêt GPS/téléphone.
- 2026-10-18 02:57 — Passe 10 : 🔍 geocoder communes (API IGN Géoplateforme, suggestions live, flyTo) + 🍂 badge saison dynamique (Pleine saison · Oct–Nov) dans le hero panel.
- 2026-10-18 03:09 — Passe 11 : ✅ checklist conditions dans le radar (humidité 14j / température demain / saison / fenêtre future) avec ✅/⚠️/❌ depuis push.json.
- 2026-10-18 03:32 — Passe 12 : 📲 PWA installable — manifest.json (name/icons/shortcuts), SW cache-first, icône champignon SVG champêtre, bouton "Installer" dans le hero (visible si beforeinstallprompt), apple-mobile-web-app meta tags.
- 2026-10-18 03:49 — Passe 13 : 🍄 Espèces GBIF colorées — 4 couleurs data-driven (edulis or/aereus brun/pinophilus rouille/reticulatus ocre), glow matching, légende 4 espèces, popup enrichi avec nom FR + latin + indicateur couleur.
- 2026-10-18 04:29 — Passe 14 : 🎴 Fiches espèces GBIF enrichies — SVG champignon par espèce (forme/couleur chapeau distincts), description habitat + caractéristiques, popup restructurée en fiche ; + 💡 conseil de prospection dans le radar push (4 niveaux, conseils concrets).
- 2026-10-18 04:52 — Passe 15 : 🎯 Tooltip léger au survol des parcelles forêt (score + essence, suit le curseur) + 🗺️ lien "Y aller →" Google Maps dans le popup de chaque parking individuel.
- 2026-10-18 05:55 — Passe 16 : 📊 Pill "stats de zone" en temps réel (bottom-center) — spots 🥇 + obs GBIF + essence dominante dans la vue courante, mis à jour sur moveend (600ms debounce, disparaît si zone vide).
- 2026-10-18 06:29 — Passe 17 : 🔥 Heatmap densité GBIF native MapLibre — palette champêtre or→cuivre→brun-profond, s'intensifie avec le zoom, s'efface à z13.5 quand les points individuels apparaissent. Barre gradient dans la légende. Toggle "Trouvailles réelles" contrôle les 3 couches (heat+glow+pt).
- 2026-10-18 07:09 — Passe 18 : 🔗 OG meta tags (og:image 1200×630, Twitter card) pour partage social + splash enrichi avec score du jour dynamique (anneau SVG, verdict, prochaine pluie).
- 2026-10-18 07:52 — Passe 19 : 🎛️ Filtres espèces GBIF cliquables (chips dans la légende, setFilter MapLibre) + opacité proportionnelle à la fraîcheur de l'observation (step 2005/2015/2020) + météo push.json rafraîchie.
- 2026-10-18 08:12 — Passe 20 : 📅 Calendrier phénologique Sep→Nov (11 semaines, probabilité historique Pays Basque, semaine courante ▾ or) intégré dans le radar de poussée.
- 2026-10-18 08:1x — Passe 20 (dirigée Thibault) : UI façon Google Maps — panneau couches en **tiroir** derrière un bouton rond flottant ☰ (fermé par défaut sur mobile, scrollable max 88vh, ✕ pour fermer) + param ?skipintro. **FIX bug bloquant** : setPaintProperty gbif opacité appelé avant chargement du style (top-level) → cassait le script (TDZ _coinsOpen, splash non retiré) → déplacé dans on('load') + garde isStyleLoaded dans updateCoins.
