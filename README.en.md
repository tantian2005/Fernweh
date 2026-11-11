# Fernweh

[中文](README.md) | **English**

Keep track of the cities you have been to, and see your footprints, distances and postcards on a map.

**Use it online: <https://tantian2005.github.io/Fernweh/>**

Your data stays in your own browser. There is no account, and nothing is uploaded to a server. Before you switch devices or clear your browser, export a backup in Settings → Data & backup.

## Features

- Over 130,000 cities, about 58,000 of them with Chinese names, searchable in Chinese or English; add a place yourself when it is not listed
- A map that scrolls sideways without end, with detailed borders when you zoom in, and a choice of vector and online basemaps
- Visit dates, notes and photos for each city; a date in the future is listed apart as an upcoming trip
- Set a base city and your trips are drawn as lines; choose how many days apart count as a return to base
- Footprints from photos: the place and date are read from your photos, which never leave the device
- Import and export as JSON or CSV
- Stats: countries, provinces and states, distance and achievements; tap a flag to see one country
- Virtual postcards and share cards
- Trip replay and a demo mode
- Chinese and English interface, light and dark themes; install it to your home screen, and what you have viewed works offline

## Run locally

It is a plain static web page with no build step. Start any static server in the project folder:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/>. City photos load from the photo site, so they need a connection.

## Deploy

Publish the repository root to any static host. This project uses GitHub Pages, served from the root of the `main` branch, and updates on every push.

Before a release, run:

```bash
node tools/release.js
```

It raises the version and the cache name, and gives each changed data file a new `?v=` number. Without it, browsers may keep using the old files.

## Files

| Path | Contents |
|---|---|
| `fernweh.html` | The interface and all of the code |
| `data/core.js` | Loaded first: country borders, flags, cities of 50,000 people or more and every city with a photo |
| `data/rest.js` | The other cities, Chinese names and state borders, loaded in the background once the map is showing |
| `data/geo/` | Detailed borders, one file per country, loaded only when you zoom in |
| `data/photos.js` | Credits and addresses of the city photos. The picture files are in their own repository, [fernweh-photos](https://github.com/tantian2005/fernweh-photos) |
| `sw.js`, `manifest.webmanifest`, `icons/` | Offline cache and home screen install |
| `tools/` | Maintenance scripts, see below |
| `ROADMAP.md` | Known problems and plans (in Chinese) |

## Tools

| Command | Use |
|---|---|
| `node tools/release.js` | Raise the version numbers before a release |
| `node tools/split-cities.js [patch file]` | Split the city data into `core.js` and `rest.js`; with a patch file, first add cities or hide district entries. Patches are kept in `tools/data-patches/` |
| `python tools/photos.py take ID="File name.jpg"` | Use one named Wikimedia Commons file for one city |
| `python tools/photos.py fetch`, `sheet`, `merge` | Find, review and merge photos of Chinese cities in bulk |
| `python tools/photos.py credits` | Write the credits table `CREDITS.csv` in the photo repository |
| `python tools/audit.py` | Static checks: unused code and styles, Chinese left in English strings |

After adding photos, push the photo repository first, wait for its site to update, then push this one.

## Data sources

- Cities: [GeoNames](https://www.geonames.org/) (CC BY 4.0), [Wikidata](https://www.wikidata.org/) (CC0)
- Chinese county and city divisions: National Bureau of Statistics of China, 2020
- Borders: [Natural Earth](https://www.naturalearthdata.com/) (public domain)
- Online basemaps: Esri
- City photos: freely licensed pictures from Wikimedia Commons and Wikipedia. Each keeps its own licence; credits are in each photo's caption in the app and on the About page

## Licence

The code is released under the MIT licence, see [LICENSE](LICENSE). The data and the photos are not covered by it; each follows the licence of its source above.
