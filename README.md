# AliveGR Kodi Addon

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/D1D11UQ0IO)
[![Paypal](https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg)](https://www.paypal.me/AliveGR)
[![Patreon](https://img.shields.io/badge/Patreon-Support-orange.svg)](https://www.patreon.com/twilight0)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](LICENSES/GPL-3.0-only)

<p align="center">
  <img src="https://raw.githubusercontent.com/Twilight0/plugin.video.alivegr/master/icon.png" alt="AliveGR Logo" width="220"/>
</p>

### *Your one addon for everything Greek-related on Kodi*

**AliveGR** is a feature-rich, high-performance Kodi video addon dedicated to Greek streaming content. It aggregates and streams Greek national and regional live television broadcasts, music television and charts, movies, TV series, shows, theatrical performances, documentaries, and kids content from publicly available internet sources into a cohesive, user-friendly interface.

---

## 🌟 Key Features

### 📺 Live Television
* **Panhellenic & Regional Lineup**: Comprehensive coverage of Greek national networks (ERT, MEGA, ANT1, ALPHA, STAR, SKAI, OPEN, etc.), Cypriot broadcasts, regional stations organized by geographical region, and Web TV channels.
* **Per-Stream DRM & License Handling**: Full support for Widevine/DRM encrypted streams through `inputstream.adaptive`, complete with stream-specific license unpacking and custom HTTP headers.
* **Intelligent Multi-Stream Fallback & Selection**:
  * **"Choose Stream" Context Menu**: Select specific video feeds per channel with persistent user preference saving across reboots.
  * **Silent Auto-Failover**: Automatically cycles through fallback streams if the active link is offline or geo-restricted.
* **"Zap from Here" (Ζάπινγκ από εδώ)**: Context menu action that queues all subsequent channels in the current category into Kodi's video playlist with looping playback, enabling continuous channel flipping (Next / Previous) without returning to the menu.
* **Dynamic Grouping & Switcher Modes**: Filter channels by group (Panhellenic, Pancypriot, Regional, Web TV, Music, Kids, Cinema, etc.) with configurable switching modes and quick group headers.
* **Network Logo Fetching & Caching**: Fast, lightweight remote logo retrieval cached locally via `script.module.unicache` without requiring heavy static logo packs.

### 🎬 On-Demand (VOD) Catalog
* **Extensive Categories**: Greek movies (classic & modern), TV series, shows, documentaries, short films, theater plays, and children's animation.
* **Smart Source Resolving**: Powered by [ResolveURL](https://github.com/Gislayer/script.module.resolveurl) and [PluginsGR](https://github.com/Twilight0/script.module.resolveurl.pluginsgr) for fast, direct video extraction without local proxy overhead.
* **Flexible Directory Navigation**: Configurable pagination, sorting orders, and reverse episode ordering.
* **Bookmarks & Playback History**: Built-in resume points, watch history tracking, and favorite bookmarks stored locally.

### 🎵 Music & Radio
* **Music Television & Video Hits**: Greek music channels and video clip directories.
* **Top 50 Charts**: Scraped and updated music charts powered by Playlist.gr with direct streaming links.

### 🔍 Unified Search & Greeklish Transliteration
* **Search Across All Content**: Single search bar covering Live TV, Movies, TV Series, Shows, Theater, and Animation.
* **Natural Greeklish Transliteration**: Live TV search recognizes both native Greek text and phonetic Greeklish typing (e.g., searching `mega` or `ant1` matches `MEGA` or `ANT1`; searching `ερτ` matches `ERT`).
* **Search History**: Instant access to previous search terms with one-click clearing.

### 🎨 Themes & Customization
* **Multiple Artwork Themes**: Included icon styles including `Gemini`, `Twilight`, and classic themes.
* **Folder Toggle Manager**: Hide or reveal specific sections (Live TV, Movies, Series, Shows, Theater, Docs, Kids, Music, Search, History, Bookmarks) directly from Add-on Settings.
* **Autostart Option**: Optional toggle to automatically launch AliveGR on Kodi startup.
* **Bilingual UI**: Fully localized in English (`en_GB`) and Greek (`el_GR`).

---

## 📋 Compatibility & Requirements

### Tested Kodi Versions
* **Kodi 20 (Nexus)**
* **Kodi 21 (Omega)**
* **Kodi 22 (Piers - in progress)**

### Supported Platforms
* **Linux** (Garuda / Arch, Debian / Ubuntu, LibreELEC, CoreELEC)
* **Android / Android TV / Google TV** (FireTV, Nvidia Shield, smart TVs, mobile)
* **Windows** (x86_64)
* **macOS / iOS / tvOS**

### Core Dependencies
AliveGR leverages lightweight modular dependencies hosted on the Twilight0 Addon Repository:
* [script.module.tulip](https://github.com/Twilight0/script.module.tulip) (v4.1.2+) — Modern Kodi Python framework powering dialogs, directories, player controls, and transliteration.
* [script.module.resolveurl](https://github.com/Gislayer/script.module.resolveurl) — Primary video host resolvers.
* [script.module.resolveurl.pluginsgr](https://github.com/Twilight0/script.module.resolveurl.pluginsgr) — Dedicated resolvers for official Greek broadcast portals.
* [script.module.unicache](https://github.com/Twilight0/script.module.unicache) — Disk and memory caching layer.
* [script.module.netclient](https://github.com/Twilight0/script.module.netclient) — HTTP requests and session management.
* [script.module.scrapetube](https://github.com/Twilight0/script.module.scrapetube) — YouTube playlist and channel scraper.
* [resource.images.alivegr.artwork](https://github.com/Twilight0/resource.images.alivegr.artwork) — Icon packs and backgrounds.
* [inputstream.adaptive](https://github.com/xbmc/inputstream.adaptive) (Kodi built-in binary addon) — Required for HLS/DASH adaptive streaming and DRM playback.

---

## 📥 Installation

### Method 1: Via Twilight0 Repository (Recommended)
Installing via the repository ensures all dependencies, resolvers, and future updates are installed automatically:

1. In Kodi, navigate to **Settings** (gear icon) ➔ **File Manager** ➔ **Add source**.
2. Select `<None>` and enter the following URL:
   ```text
   https://twilight0.github.io/repository.twilight0/
   ```
3. Enter a name for the media source (e.g., `Twilight0 Repo`) and click **OK**.
4. Go back to Kodi's home screen, click **Add-ons** ➔ **Add-on browser** (open box icon at top left).
5. Select **Install from zip file** (enable *Unknown sources* in Kodi settings if prompted).
6. Select `Twilight0 Repo` and click `repository.twilight0-2.0.zip`.
7. Once the repository is installed, select **Install from repository** ➔ **Twilight0 Repository** ➔ **Video add-ons** ➔ **AliveGR** ➔ **Install**.

### Method 2: Direct Zip Download
You can also download the repository ZIP file directly:
* Repository ZIP: [repository.twilight0.zip](https://raw.githubusercontent.com/Twilight0/repository.twilight0/gh-pages/repository.twilight0.zip)

---

## ⚙️ Recommended Configuration

For the best streaming experience:
1. Ensure **InputStream Adaptive** is enabled:
   * Kodi **Settings** ➔ **Add-ons** ➔ **My add-ons** ➔ **VideoPlayer InputStream** ➔ **InputStream Adaptive** ➔ **Enable**.
2. In AliveGR Add-on Settings:
   * **Streams**: Leave *Live TV Stream Switcher* on `Adaptive` or `Best` according to your bandwidth.
   * **Appearance**: Choose your preferred Icon Theme (`Gemini` recommended).
   * **Folders**: Toggle off any categories you do not use for a cleaner root menu.

---

## ☕ Support & Donations

If you appreciate the time and continuous maintenance that goes into AliveGR, consider buying a coffee or supporting future development:

* **Ko-fi**: [ko-fi.com/twilight0](https://ko-fi.com/D1D11UQ0IO)
* **PayPal**: [paypal.me/AliveGR](https://www.paypal.me/AliveGR)
* **Patreon**: [patreon.com/twilight0](https://www.patreon.com/twilight0)

---

## 💬 Community & Bug Reporting

* **Discussions & Feature Requests**: [GitHub Discussions](https://github.com/Twilight0/plugin.video.alivegr/discussions)
* **Issue Tracker**: [GitHub Issues](https://github.com/Twilight0/plugin.video.alivegr/issues)
* **Website**: [alivegr.net](https://alivegr.net/)

> **Disclaimer**: The author of AliveGR does not host, stream, or distribute any of the media content displayed within this software. All streams and on-demand links are parsed from publicly available domains on the internet. AliveGR acts strictly as a directory and search client.

---

## 📄 License & Credits

* **License**: [GNU General Public License v3.0](LICENSES/GPL-3.0-only)
* **Artwork**: UI artwork and iconography crafted by Twilight0, layered with icons from [Flaticon.com](https://www.flaticon.com/).
