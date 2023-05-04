# Anime1.me 下載器

> **Warning**  
> 2023 年 5 月 5 日 終止維護通知：  
> 由於最近Anime1.me新增了 Cloudflare 「我不是機械人」的驗證程序，導致程式無法運作。這個問題暫時並無任何解決方案，所以只能選擇停止維護。  
> 
> 這個小程式原本只是長假期和朋友一起練習 Python 爬蟲而製作出來，並沒有打算長期維護，而開發者本人在製作完本程式後也甚少使用。近年 [OTT 服務](https://zh.wikipedia.org/zh-hk/OTT%E6%9C%8D%E5%8A%A1#%E7%9F%A5%E5%90%8DOTT%E5%B9%B3%E5%8F%B0)盛行，要找到合法的中文字幕動畫相當容易。在此鼓勵路過的各位支持正版，幫助動漫產業發展。

[![Latest version](https://img.shields.io/github/v/release/icelam/anime1-downloader.svg?sort=semver&label=latest)](https://github.com/icelam/anime1-downloader/releases)
![Build](https://github.com/icelam/anime1-downloader/actions/workflows/build.yml/badge.svg)
![Release](https://github.com/icelam/anime1-downloader/actions/workflows/release.yml/badge.svg)
![Python Version](https://img.shields.io/github/pipenv/locked/python-version/icelam/anime1-downloader)

### 預覽
![預覽](./docs/demo-compressed.gif)

### 使用教學

#### 安裝 Python
本程式使用 Python 3 進行開發，使用前請先確保 Python 3 已正確安裝。

#### 利用 pipenv 建立 Python 虛擬環境
```bash
# 假設用戶已預先安裝好 pipenv 套件，如未安裝請先運行 pip3 install pipenv
pipenv --python 3.9.9
```

#### 安裝所需套件
```bash
pipenv install --dev
```

#### 在虛擬環境運行主程式
```bash
pipenv run python anime1download
```

### 聲明
本程式僅供學習交流，嚴禁用於商業用途，所有透過本程式下載的檔案請盡速刪除。
