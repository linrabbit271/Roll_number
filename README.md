# 🚀 网页信息跨页提取系统 (Web Information Cross-Page Extractor) v12.0

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=flat&logo=qt&logoColor=white)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

**网页信息跨页提取系统** 是一款基于 Python、PyQt6 和 OpenCV 构建的轻量级桌面端自动化脚本工具。它通过图像识别技术智能定位网页上的“下一页”/翻页按钮，自动全选、复制并汇总多页文本内容，解决需要手动逐页复制网页数据的繁琐问题。

---

## ✨ 核心功能与亮点

* 👁️ **基于 CV 的精准翻页识别**：利用 OpenCV 模版匹配算法识别自定义的翻页按钮（支持常态与高亮两种状态特征）。
* 📋 **自动全选与剪贴板流转**：自动执行全选、复制、取消高亮流程，并将多页文本有序拼接展示。
* 🛑 **全局快捷中断**：基于 `pynput` 的监听机制，运行过程中随时按下 **空格键 (Space)** 即可安全终止流程并保留已提取数据。
* 🎨 **现代化 UI 设计**：内置基于 `QPainter` 绘制的矢量图标、自定义 Splash 启动界面及 Fusion 风格界面。
* 📌 **原生 Windows 任务栏支持**：已集成 `AppUserModelID` 注册，确保应用图标在 Windows 任务栏独立且清晰呈现。

---

## 🛠️ 环境要求与依赖库

在运行本项目之前，请确保已安装 Python 3.8 或更高版本。

### 依赖第三方库

* **PyQt6**：用于构建图形用户界面 (GUI)
* **pyautogui**：用于模拟鼠标点击与键盘快捷键
* **opencv-python** & **numpy**：用于屏幕图像匹配与坐标计算
* **pynput**：用于全局监听中断按键
* **pyperclip**：用于剪贴板数据读取与写入

---

## 📦 快速安装与运行

1. **克隆或下载本仓库代码**：
   ```bash
   git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
   cd your-repo-name
