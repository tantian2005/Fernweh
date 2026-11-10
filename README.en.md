# Fernweh · 足迹

[中文](README.md) · **English**

Keep track of the cities you have been to, and see your footprints, distances and postcards on a map.

**Use it online: <https://tantian2005.github.io/Fernweh/>**

Your data stays in your own browser. There is no account, and nothing is uploaded to a server. Before you switch devices or clear your browser, export a backup in Settings → Data & backup.

## Features

- Over 130,000 cities, about 58,000 of them with Chinese names, searchable in Chinese or English
- A map that scrolls sideways without end, with detailed borders when you zoom in, and a choice of vector and online basemaps
- Visit dates, notes and photos for each city; set a home base and your trips are drawn as lines
- Quick layer switches for city names, trip lines and area shading
- Stats: countries, distance and achievements
- Virtual postcards and share cards
- Trip replay and a demo mode
- Chinese and English interface, light and dark themes; install it to your home screen, and what you have viewed works offline

## Run locally

It is a plain static web page with no build step. Start any static server in the project folder:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/>.

## Deploy

Publish the repository root to any static host. This project uses GitHub Pages, served from the root of the `main` branch, and updates on every push.

When you change `data/cities.js` or `data/photos.js`, also bump the version numbers in `fernweh.html` and `sw.js`, or browsers may keep using the old files.

## Files

| Path | Contents |
|---|---|
| `fernweh.html` | The interface and all of the code |
| `data/cities.js` | Cities, Chinese names, country and province borders |
| `data/geo/` | Detailed borders, one file per country, loaded only when you zoom in |
| `data/photos.js` | Credits and addresses of the city photos. The picture files are in their own repository, [fernweh-photos](https://github.com/tantian2005/fernweh-photos) |
| `sw.js`, `manifest.webmanifest`, `icons/` | Offline cache and home screen install |

## Data sources

- Cities: [GeoNames](https://www.geonames.org/) (CC BY 4.0), [Wikidata](https://www.wikidata.org/) (CC0)
- Chinese county and city divisions: National Bureau of Statistics of China, 2020
- Borders: [Natural Earth](https://www.naturalearthdata.com/) (public domain)
- Online basemaps: Esri
- City photos: from Wikipedia and other sources; credits are in each photo's caption in the app and on the About page
