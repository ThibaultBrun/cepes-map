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
