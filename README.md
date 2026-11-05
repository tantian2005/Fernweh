# Fernweh · 足迹

记录去过的城市，在地图上看自己的足迹、里程和明信片。

**在线使用：<https://tantian2005.github.io/Fernweh/>**

数据只存在你自己的浏览器里，没有账号，也不会上传到服务器。换设备或清理浏览器前，请先到「设置 → 数据与备份」导出。

## 功能

- 13 万多座城市，其中约 5.8 万个有中文名，支持中英文搜索
- 可无限左右滚动的地图，放大后使用高精度边界，有矢量和在线底图可选
- 记录到访日期、笔记和照片，设置基地城市后自动画出旅程连线
- 统计页：国家、里程和成就
- 虚拟明信片和分享卡片
- 足迹回放和演示模式
- 中英文界面、深浅色主题；可安装到主屏幕，看过的内容可离线查看

## 本地运行

这是一个纯静态网页，没有构建步骤。在项目目录启动任意静态服务器即可：

```bash
python -m http.server 8000
```

然后打开 <http://localhost:8000/>。

## 部署

把仓库根目录发布到任意静态托管即可。这里使用 GitHub Pages：从 `main` 分支的根目录发布，推送后自动更新。

更新 `data/cities.js`、`data/photos.js` 后，要同时修改 `fernweh.html` 和 `sw.js` 里的版本号，否则浏览器可能继续使用旧文件。

## 目录

| 路径 | 内容 |
|---|---|
| `fernweh.html` | 界面和全部程序 |
| `data/cities.js` | 城市、中文名、国家边界和省州边界 |
| `data/geo/` | 高精度边界，每个国家一个文件，放大时才加载 |
| `data/photos.js`、`png/` | 城市照片和署名 |
| `sw.js`、`manifest.webmanifest`、`icons/` | 离线缓存和安装到主屏幕 |

## 数据来源

- 城市：[GeoNames](https://www.geonames.org/)（CC BY 4.0）、[Wikidata](https://www.wikidata.org/)（CC0）
- 中国县市级区划：国家统计局 2020
- 边界：[Natural Earth](https://www.naturalearthdata.com/)（公共领域）
- 在线底图：Esri
- 城市照片：来自维基百科等来源，署名见 `png/credits.csv` 和应用内的照片说明
