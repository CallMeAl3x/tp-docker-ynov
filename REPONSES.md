# TP Docker — Réponses

J'ai mis un dossier par partie pour qu'on puisse voir l'évolution du Dockerfile :

| Dossier | Ce qu'il y a dedans | Build |
|---|---|---|
| `partie-02-06/` | le Dockerfile de base | `docker build -t docker-lab:v1 partie-02-06` |
| `partie-07/` | la version mal optimisée | `docker build -t docker-lab:v3 partie-07` |
| `partie-12/` | multi-stage + `.dockerignore` | `docker build -t docker-lab:multistage partie-12` |
| `partie-13/` | utilisateur non-root | `docker build -t docker-lab:nonroot partie-13` |
| `partie-14/` | message via `APP_MESSAGE` | `docker build -t docker-lab:env partie-14` |
| `partie-15/` | healthcheck (version finale) | `docker build -t docker-lab:health partie-15` |

## Partie 2 — Dockerfile

**Q1.** `RUN` s'exécute pendant le build : la commande tourne une fois et son résultat est enregistré dans un layer alors que `CMD` s'exécute pas au démarrage du conteneur. On peut la remplacer au `docker run`.

**Q2.** `WORKDIR /app` définit le dossier de travail pour toutes les instructions qui suivent, et pour le conteneur. Le dossier est créé s'il n'existe pas. C'est pour ça que `COPY app.py .` met le fichier dans `/app`.

**Q3.** `EXPOSE 5000` ça dit que l'appli écoute sur le port 5000 (pas confondre avec exposer qui est autre chose).

## Partie 3 — Build

**Q4.** `docker images` (ou `docker image ls`).

**Q5.** L'image fait 223 Mo. ça vient principalement de l'image de base `python:3.12-slim`, les fichiers et Flask ne rajoutent qu'environ 15 Mo.

## Partie 4 — Lancement

`docker run -d --name docker-lab -p 8080:5000 docker-lab:v1`, puis sur `localhost:8080` j'ai bien « Bonjour depuis mon conteneur Docker ! » (ce que j'ai mis dans le .txt).

**Q6.** `-p 8080:5000` ça redirige le port 8080 de ma machine vers le port 5000 du conteneur (d'où le `0.0.0.0` dans Flask, sinon il écoute que dans le conteneur).

**Q7.** `docker ps` (`-a` pour voir aussi ceux arrêtés).

**Q8.** `docker logs docker-lab` (`-f` pour suivre en direct).

## Partie 5 — Layers

**Q9.** On retrouve toutes les instructions du Dockerfile : `WORKDIR`, `COPY requirements.txt`, `RUN pip install`, `COPY app.py`, `COPY message.txt`, `EXPOSE` et `CMD`. Tout ce qu'il y a en dessous c'est l'image de base (le `FROM`).

**Q10.** `FROM`, `WORKDIR`, `COPY` et `RUN`. `EXPOSE` et `CMD` ça change juste les métadonnées (0 B dans l'historique).

**Q11.** C'est le layer Debian de l'image de base (110 Mo) vu que c'est tout le système. Dans mon Dockerfile c'est le `pip install` (15,5 Mo) à cause de Flask et ses dépendances.

## Partie 6 — Cache

**Q12.** `WORKDIR`, `COPY requirements.txt`, `RUN pip install` et `COPY app.py`. Y a que `COPY message.txt` qui est refait.

**Q13.** `requirements.txt` a pas changé et il est copié avant `message.txt`, donc Docker reprend le layer du `pip install` direct depuis le cache.

**Q14.** À partir de `COPY message.txt`, et tout ce qui vient après est refait.

## Partie 7 — Mauvaise optimisation

**Q15.** Non, le `pip install` est relancé à chaque build (2,6 s chez moi).

**Q16.** Avec `COPY . .` tout le projet est dans le même layer, donc dès qu'on touche un fichier (même le .txt) le cache saute et Flask est réinstallé. Sur un gros projet ça peut faire perdre plusieurs minutes à chaque build.

**Q17.** Il faut mettre ce qui bouge le moins en premier : copier juste `requirements.txt`, faire le `pip install`, et copier le code après (c'est ce que fait `partie-02-06/Dockerfile`) :

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py message.txt ./
EXPOSE 5000
CMD ["python", "app.py"]
```

## Partie 11 — `.dockerignore`

**Q26.** Ça sert à exclure des fichiers de ce qu'on envoie à Docker au build, donc ils peuvent pas finir dans l'image (même avec un `COPY . .`).

**Q27.**
- Sécurité : pas de `.env`, de mot de passe ou de `.git` dans l'image par erreur.
- Taille : on envoie pas les fichiers inutiles (archives, caches…).
- Vitesse : moins de choses à envoyer, et le cache saute moins souvent pour rien.

## Partie 12 — Multi-stage

**Q28.** `AS builder` ça donne un nom à l'étape pour pouvoir la réutiliser après.

**Q29.** `COPY --from=builder` copie depuis l'étape `builder` et pas depuis le projet (ici juste les paquets installés dans `/install`, le reste on le garde pas).

**Q30.** L'image est plus légère et y a moins d'outils dedans, donc moins de failles (et si quelqu'un rentre dans le conteneur il a pas de compilateur sous la main).

**Q31.** 210 Mo en multi-stage contre 223 Mo pour la v1. Le gain est petit vu qu'en Python y a pas grand chose à compiler, mais pour du Go, Java ou Node le SDK fait des centaines de Mo et il reste dans l'étape de build (l'image finale garde juste le binaire ou le `dist/`).

## Partie 13 — Utilisateur non-root

`whoami` donne `root` avec la v1 et `appuser` avec l'image `nonroot`.

**Q32.** Si l'appli se fait pirater, l'attaquant est root dans le conteneur, il peut tout modifier et il a plus de chances de sortir vers la machine hôte. Faut donner le minimum de droits.

**Q33.** `USER appuser` ça fait tourner la suite et l'appli avec cet utilisateur au lieu de root (à mettre après le `pip install` et le `chown` qui ont besoin de root).

**Q34.** `whoami` donne `appuser` et `id` donne `uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)`. J'ai testé, il peut pas écrire dans `/etc` ni faire de `apt-get`.

## Partie 14 — Variables d'environnement

Sans `-e` j'ai le message par défaut, avec `-e APP_MESSAGE="Bonjour depuis une variable Docker !"` j'ai le nouveau.

**Q35.** `-e` ça définit une variable d'environnement dans le conteneur au lancement (l'appli la lit avec `os.getenv`).

**Q36.** Non, c'est la même image, y a que le `docker run` qui change.

**Q37.** On fait une seule image qu'on déploie en dev, recette et prod en changeant juste la config. Pas besoin de rebuild pour un paramètre, et ce qui a été testé c'est exactement ce qui part en prod.

**Q38.** Non, j'ai testé et le mot de passe apparait en clair dans `docker inspect` et `docker history`. Tout ceux qui récupèrent l'image peuvent le lire, et pour le changer faut tout reconstruire. Faut plutôt le passer au lancement (`-e`, `.env` pas versionné, secrets Docker/Kubernetes).

## Partie 15 — Healthcheck

Dans `docker ps` on voit `health: starting` puis `healthy` au bout d'une dizaine de secondes.

**Q39.** `running` c'est juste que le processus tourne, `healthy` c'est que l'appli répond vraiment au test (`/health`). Un conteneur peut être running mais unhealthy si l'appli est bloquée.

**Q40.** `--interval` : le temps entre deux tests (10 s).

**Q41.** `--timeout` : le temps max d'un test (3 s), s'il répond pas avant c'est compté comme raté.

**Q42.** `--retries` : le nombre d'échecs d'affilée avant de passer en `unhealthy` (3), comme ça un petit ralentissement suffit pas.

**Q43.** Elle peut redémarrer ou recréer le conteneur, arrêter de lui envoyer du trafic, annuler un déploiement et envoyer une alerte.

## Partie 16 — Registry

L'image finale (partie 15) est sur Docker Hub : https://hub.docker.com/r/callmeal3x/docker-lab

```bash
docker login
docker tag docker-lab:health callmeal3x/docker-lab:v1
docker push callmeal3x/docker-lab:v1
docker pull callmeal3x/docker-lab:v1
docker run --rm -p 8080:5000 callmeal3x/docker-lab:v1
```

J'ai supprimé l'image en local avant le `pull` pour vérifier, et le conteneur répond bien sur `localhost:8080`.

**Q44.** L'`IMAGE ID` c'est un hash unique calculé à partir du contenu, le `TAG` c'est juste un nom lisible qui pointe vers une image (une image peut en avoir plusieurs, `docker-lab:health` et `callmeal3x/docker-lab:v1` ont le même ID).

**Q45.** Non, ça crée juste une nouvelle référence vers la même image, rien n'est copié.

**Q46.** `docker push` envoie l'image sur le registry (que les layers qui y sont pas déjà).

**Q47.** `docker pull` la télécharge depuis le registry (`docker run` le fait tout seul si l'image est pas là).

**Q48.** Les images contiennent le code de la boîte donc on veut pas qu'elles soient publiques. Et un registry privé permet de gérer qui a accès, de scanner les images et d'être proche des serveurs.

**Q49.** La CI build l'image une fois, la pousse avec un tag (version ou commit) et tous les environnements utilisent la même. On sait quelle version tourne où, et pour revenir en arrière on redéploie juste le tag d'avant.

## Partie 17 — Synthèse

**Q50.**
- **Dockerfile** : la recette pour construire l'image.
- **Image** : le résultat du build, figée et faite de layers (le modèle).
- **Conteneur** : une image qui tourne (on peut en lancer plusieurs depuis la même image).
- **Registry** : là où on stocke et partage les images (Docker Hub, GHCR…).

**Q51.** Une image c'est fait pour être partagé, donc tous ceux qui l'ont peuvent lire ce qu'il y a dedans. Et avec les layers, même un fichier supprimé plus loin reste dans l'image. En plus on peut pas changer le secret sans tout reconstruire.

**Q52.**
- Image de base légère avec une version précise (pas `latest`).
- Multi-stage build.
- Utilisateur non-root.
- Aucun secret dans l'image.
- Un `.dockerignore`.
- Dockerfile ordonné pour le cache.
- Un healthcheck.
- La config en variables d'environnement.
- Scanner l'image (Trivy, Docker Scout).
