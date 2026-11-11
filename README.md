# Fernweh 足迹

**中文** | [English](README.en.md)

记录去过的城市，在地图上看自己的足迹、里程和明信片。

**在线使用：<https://tantian2005.github.io/Fernweh/>**

数据只存在你自己的浏览器里，没有账号，也不会上传到服务器。换设备或清理浏览器前，请先到「设置 → 数据与备份」导出。

## 功能

- 13 万多座城市，其中约 5.8 万个有中文名，支持中英文搜索；找不到的地方可以自己添加
- 可无限左右滚动的地图，放大后使用高精度边界，有矢量和在线底图可选
- 记录到访日期、笔记和照片；填未来的日期会作为"即将出发"单独列出
- 设置基地城市后自动画出旅程连线，可以调整隔多少天算回过基地
- 从照片添加足迹：读取照片里的拍摄地点和日期，照片不会离开设备
- 导入和导出 JSON、CSV
- 统计页：国家/地区、省州、里程和成就，点国旗查看单个国家
- 虚拟明信片和分享卡片
- 足迹回放和演示模式
- 中英文界面、深浅色主题；可安装到主屏幕，看过的内容可离线查看

## 本地运行

这是一个纯静态网页，没有构建步骤。在项目目录启动任意静态服务器即可：

```bash
python -m http.server 8000
```

然后打开 <http://localhost:8000/>。城市照片从照片站加载，需要联网。

## 部署

把仓库根目录发布到任意静态托管即可。这里使用 GitHub Pages：从 `main` 分支的根目录发布，推送后自动更新。

发布前运行一次：

```bash
node tools/release.js
```

它会提高版本号和缓存名，并给改动过的数据文件换上新的 `?v=` 编号。不这样做，浏览器可能继续使用旧文件。

## 目录

| 路径 | 内容 |
|---|---|
| `fernweh.html` | 界面和全部程序 |
| `data/core.js` | 先加载的部分：国家边界、国旗、人口 5 万以上和有照片的城市 |
| `data/rest.js` | 其余城市、中文名和省州边界，地图显示后在后台加载 |
| `data/geo/` | 高精度边界，每个国家一个文件，放大时才加载 |
| `data/photos.js` | 城市照片的署名和地址。照片文件在单独的仓库 [fernweh-photos](https://github.com/tantian2005/fernweh-photos) |
| `sw.js`、`manifest.webmanifest`、`icons/` | 离线缓存和安装到主屏幕 |
| `tools/` | 维护用的脚本，见下 |
| `ROADMAP.md` | 已知问题和计划 |

## 工具

| 命令 | 用途 |
|---|---|
| `node tools/release.js` | 发布前提高版本号 |
| `node tools/split-cities.js [补丁文件]` | 把城市库拆成 `core.js` 和 `rest.js`；带补丁文件时先加入新城市或隐藏城区条目，补丁放在 `tools/data-patches/` |
| `python tools/photos.py take 编号="文件名.jpg"` | 给一座城市指定维基共享资源里的一张照片 |
| `python tools/photos.py fetch`、`sheet`、`merge` | 批量查找、审图、合并中国城市的照片 |
| `python tools/photos.py credits` | 在照片仓库里生成署名表 `CREDITS.csv` |
| `python tools/audit.py` | 静态检查：没用到的代码和样式、英文文案里的中文 |

加照片后先推送照片仓库，等它的站点更新，再推送本仓库。

## 数据来源

- 城市：[GeoNames](https://www.geonames.org/)（CC BY 4.0）、[Wikidata](https://www.wikidata.org/)（CC0）
- 中国县市级区划：国家统计局 2020
- 边界：[Natural Earth](https://www.naturalearthdata.com/)（公共领域）
- 在线底图：Esri
- 城市照片：维基共享资源和维基百科上的自由版权图片，每张保留各自的许可，署名见应用内的照片说明和关于页

## 许可

程序以 MIT 许可发布，见 [LICENSE](LICENSE)。数据和照片不在此列，各按上面来源的许可使用。
