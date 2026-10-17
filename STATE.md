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
5. [ ] **Essences 10 m** (essence10.tif PRÊT: ForestPaths genre arbre, codes Pinus=2 Fagus=3 Quercus=4 broadleaf=6) → calque raster scoré + affiner : Copernicus HRL (feuillu/conifère 10m) ou carte essences Sentinel pour affiner le score.
6. [ ] Radar : prévoir la **fenêtre future** (indice sur les 7 j de prévi) + mini courbe pluie.
7. [ ] Polish mobile, écran d'intro, bouton "centrer sur moi", partage de spot (permalien).
8. [ ] Perf : vérifier chargement pmtiles, zoom, clusters parkings.


## Repo & commits
- Repo: **ThibaultBrun/cepes-map** (public), dossier source `/home/debian/cepes`. Données générées = gitignored (reconstruites par build_*.py).
- Chaque passe : copier les sources modifiées dans ~/cepes, `git add -A`, commit **daté 22h-01h** (GIT_AUTHOR_DATE/COMMITTER_DATE=2026-10-18T00:5X:00), user.name 'Thibault Brun', **sans Co-Authored-By**, puis `git push`.

## Journal
- 2026-10-18 01:1x — Passe 0 : DA champêtre déployée, expo réchauffée (or), radar restylé. STATE+cron à armer.
- 2026-10-18 01:3x — Passe 1 : couche ✨ spots prime (sud ∩ forêt, 1.07M px) + 🍄 202 points GBIF (edulis/aereus/pinophilus/reticulatus) intégrés + légende MAJ.
- 2026-10-18 01:47 — Passe 2 : 🥇 panel "Meilleurs coins" (top-right, queryRenderedFeatures score=3, clickable flyTo+popup) + highlight gold foret-best layers + toggle + légende MAJ.
