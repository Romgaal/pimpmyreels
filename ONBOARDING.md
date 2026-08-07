# Démarrage — 5 minutes

**Ce qu'il te faut avant :** [Claude Code](https://claude.com/claude-code) installé, et
un abonnement Claude actif (c'est lui qui choisit les images — sans ça, pas de cerveau).

### 1. Installer le plugin

Dans Claude Code, tape :

```
/plugin marketplace add Romgaal/pimpmyreels
/plugin install pimpmyreels@pimpmyreels
```

Sur **Claude Code Desktop**, `/plugin` n'existe pas — utilise la CLI, c'est pareil :

```bash
claude plugin marketplace add Romgaal/pimpmyreels
claude plugin install pimpmyreels@pimpmyreels
```

Puis **redémarre la conversation** (le plugin se charge au démarrage).

### 2. Premier lancement

```
/pimp
```

Sans fichier, il te fabrique une petite vidéo de démo et déroule tout le pipeline
dessus : tu vois un reel monté en ~3 minutes, sans avoir filmé quoi que ce soit.
Le tout premier lancement télécharge le modèle de transcription (465 Mo, une fois).

### 3. Ta vraie vidéo

```
/pimp ~/Downloads/ma-video.mp4
```

Il transcrit ta voix, choisit les scènes de films, et t'affiche une **planche
numérotée** avec 3 candidats par moment. Tu réponds simplement :

> « garde 1.2, 2.1, mais change la 3 — mets plutôt Rocky »

Il monte et t'exporte `reel.mp4` (+ la miniature `cover.jpg`).

### 4. Tes sous-titres

Le reel sort **sans texte**, exprès. Tu ajoutes titre et sous-titres avec ton outil
habituel (Captions, CapCut…). Le style et la typo restent à toi.

### Mettre à jour plus tard

Le marketplace est mis en cache : rafraîchis-le **avant** le plugin, sinon il te dira
que tu es déjà à jour.

```bash
claude plugin marketplace update pimpmyreels && claude plugin update pimpmyreels@pimpmyreels
```

### 5. Ajuster

Tout ton reel est rangé dans `~/pimpmyreels/<nom>/`. Pour changer une durée ou une
image plus tard, demande simplement — il ne re-rend que le morceau modifié, pas toute
la vidéo.

---

**Deux ou trois choses à savoir**

- macOS marche tout seul (Homebrew installe le reste). Linux demande d'installer
  `ffmpeg`, `whisper.cpp`, `node` à la main. Windows : passe par WSL.
- Les images que tu valides enrichissent automatiquement la banque partagée — tout le
  monde en profite à la mise à jour suivante. Pour désactiver :
  `{"contribution": "off"}` dans `~/.pimpmyreels/config.json`.
- Tu as tes propres memes ? Dépose-les dans `~/.pimpmyreels/mybank/` en les nommant
  par concept (`courage-1.jpg`) : ils passent avant tout le reste.
