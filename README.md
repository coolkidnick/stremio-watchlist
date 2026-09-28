# Picture House · Nick's Picks

A personal watchlist and recommendation app for Nick Moody, plus a static Stremio add-on that puts the same recommendations inside Stremio.

- **Web app:** https://coolkidnick.github.io/stremio-watchlist/
- **Stremio add-on manifest:** https://coolkidnick.github.io/stremio-watchlist/addon/manifest.json
- **One-click install:** `stremio://coolkidnick.github.io/stremio-watchlist/addon/manifest.json`

## The web app (`index.html`)

One self-contained HTML file: vanilla JS and inline CSS, no build step, no backend, no CDN. It works offline once loaded. The only network calls are the optional TMDB lookups and Stremio sync.

- **Discover:** suggestions from a hand-picked catalogue of 350 films and series matched to Nick's taste (arthouse and classic cinema, 70s crime, westerns and samurai, British comedy, crime and prestige TV, anime, documentaries, British working-class realism, mean action). Every card gives a one-line reason tied to something he's watched. You can filter by films, series or all, by genre chips, or by text search. There's also **Shuffle** and **Surprise me**.
- **To Watch:** ships with 20 starter picks (10 series, 10 films). Actions: Watched, Not interested, Remove.
- **Seen:** your imported library plus the built-in taste profile and already-seen list. None of it is ever recommended. It's searchable, and you can remove entries you imported.
- **Import:** paste a plain title list (one per line; years, bullets and blank lines are fine) or Stremio JSON (an array of library items, or `datastoreGet`'s `{ "result": [...] }`). You can also **Sync from Stremio** with your email and password. The password is never stored; only the auth key is kept, and only if you tick "remember".
- **Settings:** add a TMDB v3 API key or v4 read-access token to get posters, ratings and synopses (cached locally). Without one you get typographic cards. Also here: JSON backup and restore, reset, and **Export Stremio add-on**.

Title matching ignores case, punctuation, accents, a leading "The", year suffixes and "&" vs "and". It also matches on IMDb id when both sides have one.

All data lives in the browser's `localStorage`. Nothing is uploaded anywhere.

## The Stremio add-on (`addon/`)

It's a fully static add-on, so GitHub Pages can host it with no server.

```
addon/manifest.json
addon/catalog/movie/nicks-picks-films.json            # To Watch films first, then top suggestions
addon/catalog/movie/nicks-picks-films/genre=Crime.json # one file per genre option in the manifest
addon/catalog/series/nicks-picks-series.json
addon/catalog/movie/nicks-towatch-films.json
addon/catalog/series/nicks-towatch-series.json
```

It only provides catalogs. Stremio's own Cinemeta supplies the detail pages and your usual add-ons supply streams, which is why only titles with a verified IMDb `tt` id are included. Each item's description starts with the reason it was picked.

### Install

- **Desktop app:** open `stremio://coolkidnick.github.io/stremio-watchlist/addon/manifest.json`.
- **Any Stremio client:** go to Add-ons, then the search / "Add-on repository URL" box, and paste `https://coolkidnick.github.io/stremio-watchlist/addon/manifest.json`.

In general the install URL is `stremio://<host>/<path>/manifest.json`, which is the HTTPS manifest URL with `https://` replaced by `stremio://`.

The catalogs then show up on Stremio's Board and in Discover, as "Nick's Picks: Films / Series" and "Nick's To Watch: Films / Series".

### Re-publishing after your list changes

There are two ways to do it.

1. **From the app:** go to Settings and click **Export Stremio add-on (.zip)**. Unzip it at the repo root (it contains `addon/`, so it replaces the old catalog files), then commit and push. GitHub Pages redeploys within a minute or two.
2. **From the command line:** in the app, go to Settings and click **Export data for build-addon.js**. Then run:

   ```sh
   node build-addon.js picture-house-YYYY-MM-DD.json            # writes ./addon
   node build-addon.js --seen my-library.txt                    # optional: extra titles to exclude (filter only)
   git add addon && git commit -m "Refresh Nick's Picks" && git push
   ```

   `build-addon.js` loads the engine straight out of `index.html`, so the app and the CLI always agree. With no export file it builds from the defaults (taste profile plus starter picks). `--seen` files are used only to filter titles out. Nothing from them is written to the add-on.

Stremio caches manifests, so bump the version (both methods do this automatically) and reinstall if a change doesn't show up.

## Hosting on GitHub Pages (from scratch)

1. Create a **public** repo and add `index.html`, `addon/`, `build-addon.js`, `README.md` and an empty `.nojekyll`. The `.nojekyll` file makes Pages serve files like `genre=Prestige TV.json` exactly as they are.
2. Go to Settings, then Pages, then Build and deployment, choose **Deploy from a branch**, and set it to `main` / `(root)`. Or run: `gh api -X POST repos/<user>/<repo>/pages -f 'source[branch]=main' -f 'source[path]=/'`.
3. Wait for the build (`gh api repos/<user>/<repo>/pages/builds/latest`). The app is then at `https://<user>.github.io/<repo>/` and the manifest at `https://<user>.github.io/<repo>/addon/manifest.json`.
4. GitHub Pages sends `Access-Control-Allow-Origin: *`, which Stremio needs.

## Privacy

Never commit your raw Stremio library export or anything containing credentials. `.gitignore` already excludes `library.json`, `library.txt` and `*.local.json`. The published catalogs contain only recommendations: seen titles are filtered out, not listed. If you export the add-on from the app after importing your library, though, some reasons may say "Because you watched X".
