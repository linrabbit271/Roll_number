import sys
import os
import time
import traceback
import shutil
import threading
import pyperclip
import pyautogui
import cv2
import numpy as np
import requests  # 🌟 用于双节点远程许可锁核验

# 全局键盘监听库
from pynput import keyboard

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QPlainTextEdit, QMessageBox, QFileDialog,
                             QSplashScreen, QProgressBar, QDialog, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QCursor, QPixmap, QIcon, QPainter, QColor, QPen, QFont


# ==================== 1. 独立法律免责协议窗口 ====================
class DisclaimerWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("软件使用协议与免责声明")
        self.setFixedSize(620, 520)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.CustomizeWindowHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("⚠️ 使用条款与开发者风险责任豁免协议")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c; margin: 5px 0;")
        layout.addWidget(title)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #dee2e6; font-size: 13px; line-height: 1.6; padding: 12px; color: #2c3e50;")

        disclaimer_text = (
            "欢迎使用本自动化视觉同步插件。在正式进入系统前，请使用者务必仔细阅读、充分理解以下条款。一旦点击“我同意并进入系统”，即代表您及您所代表的机构已完全知悉并自愿接受以下所有约束与免责条款：\n\n"
            "1. 版权归属与个人自研声明\n"
            "本插件（包括但不限于所有底层架构、图形识别算法及核心代码）属于原开发者个人独立自研的技术资产，其完整版权、所有权及最终解释权永久归属原作者个人所有。本插件未与任何机构或雇主签署排他性交付协议。原作者当前仅以技术交流与模拟测试目的，授予使用者临时的、非排他性的使用许可。原作者保留在任何时间，无条件收回、终止或撤销授权的绝对权利。\n\n"
            "2. 技术资产保护与禁止滥用\n"
            "未经原作者书面明确授权，严禁任何组织或个人对本插件进行破解、反编译、逆向工程、篡改或将其用于商业售卖。本插件仅供技术学习与个人日常办公效能提升之用，任何机构或个人不得将本插件用于非合规的大规模高频轰炸或恶意扰乱第三方系统运行的场景。\n\n"
            "3. 业务风险与第三方平台变动完全免责\n"
            "本插件作为纯个人研究项目，按“现状（AS-IS）”提供，原作者不对其功能的稳定性、绝对无错性做任何技术担保。因第三方客户端更新升级、界面UI像素调整导致插件失效，或因使用者日常操作不当、误操作引发的任何业务纠纷、数据清洗偏差、经济损失或平台风控处罚，全部风险与法律责任均由使用者自行承担，原开发者不承担任何直接或连带的赔偿责任。\n\n"
            "4. 无技术支持义务与永久责任豁免\n"
            "作为个人自研的免费技术试验品，原作者没有义务对本插件提供长期的技术支持、缺陷修复、版本更新或环境维护。无论在何种时间、何种运行环境下，由本插件引发的任何形式的技术故障、工作延误或业务流转异常，原作者均享有永久、完全且无条件的民事与刑事责任豁免权。"
        )
        self.text_area.setPlainText(disclaimer_text)
        layout.addWidget(self.text_area)

        btn_layout = QHBoxLayout()
        self.btn_exit = QPushButton(" 拒绝并退出 ")
        self.btn_exit.setFixedSize(140, 38)
        self.btn_exit.clicked.connect(self.reject)
        self.btn_exit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_exit.setStyleSheet(
            "background-color: #6c757d; color: white; border-radius: 4px; font-weight: bold; font-size: 13px;")

        self.btn_agree = QPushButton(" 我同意并进入系统 ")
        self.btn_agree.setFixedSize(190, 38)
        self.btn_agree.clicked.connect(self.accept)
        self.btn_agree.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_agree.setStyleSheet(
            "background-color: #198754; color: white; border-radius: 4px; font-weight: bold; font-size: 13px;")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_exit)
        btn_layout.addWidget(self.btn_agree)
        layout.addLayout(btn_layout)


# ==================== 2. 原生矢量 App 图标绘制 ====================
def create_app_icon() -> QIcon:
    """ 使用 QPainter 动态绘制矢量的程序窗口图标 """
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 1. 深蓝底色
    painter.setBrush(QColor("#2c3e50"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, size, size, 24, 24)

    # 2. 白色文档底板
    painter.setBrush(QColor("#ffffff"))
    painter.drawRoundedRect(28, 20, 72, 88, 8, 8)

    # 3. 灰色线条
    pen_line = QPen(QColor("#bdc3c7"))
    pen_line.setWidth(4)
    pen_line.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_line)
    painter.drawLine(40, 36, 88, 36)
    painter.drawLine(40, 50, 78, 50)
    painter.drawLine(40, 64, 88, 64)

    # 4. 绿色 > 翻页箭头
    pen_arrow = QPen(QColor("#27ae60"))
    pen_arrow.setWidth(8)
    pen_arrow.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen_arrow.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen_arrow)
    painter.drawLine(48, 78, 64, 88)
    painter.drawLine(64, 88, 48, 98)

    painter.end()
    return QIcon(pixmap)


# ==================== 3. 极质感闪屏进度条 ====================
class LoadingSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(420, 240)
        pixmap.fill(QColor("#2c3e50"))
        super().__init__(pixmap)

        self.title_label = QLabel(" 网页信息跨页提取系统 ", self)
        self.title_label.setGeometry(20, 45, 380, 45)
        self.title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #1abc9c; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(" 🚀 跨页提取系统运行环境初始化... ", self)
        self.label.setGeometry(20, 135, 380, 25)
        self.label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #ffffff; background: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(20, 175, 380, 18)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #34495e;
                border-radius: 6px;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #1abc9c; 
                border-radius: 5px;
            }
        """)

    def setProgress(self, value: int, text_info: str):
        self.progressBar.setValue(value)
        self.label.setText(text_info)
        QApplication.processEvents()


def smooth_progress_to(splash_widget, start_val, end_val, text_info, step_delay=0.008):
    """ 通过 Qt 事件循环无感刷新，将进度条从 start_val 丝滑地推送到 end_val """
    if not splash_widget:
        return
    for val in range(start_val, end_val + 1):
        splash_widget.setProgress(val, text_info)
        time.sleep(step_delay)


# ==================== 4. 🔐 核心双节点远程许可锁 ====================
def check_remote_license(splash_widget=None):
    gitee_url = "https://raw.giteeusercontent.com/rabbit_14_0/toolbox-license/raw/master/auth.json"
    github_url = "https://raw.githubusercontent.com/linrabbit271/toolbox-license/refs/heads/main/auth.json"

    if splash_widget:
        smooth_progress_to(splash_widget, 31, 45, " 🔐 正在建立双节点安全授权连接... ")

    auth_data = None
    try:
        response = requests.get(gitee_url, timeout=2.5)
        response.raise_for_status()
        auth_data = response.json()
    except requests.exceptions.RequestException:
        if splash_widget:
            smooth_progress_to(splash_widget, 45, 65, " 🌐 主节点无响应，切入国际备用节点... ")
        try:
            response = requests.get(github_url, timeout=4)
            response.raise_for_status()
            auth_data = response.json()
        except requests.exceptions.RequestException:
            pass

    if auth_data is None:
        if splash_widget:
            splash_widget.close()
        QMessageBox.critical(None, "网络异常", "无法连接到系统授权服务器，请检查网络后重试。")
        sys.exit(0)

    if auth_data.get("status") != "active":
        if splash_widget:
            splash_widget.close()
        error_msg = auth_data.get("msg", "系统安全授权已失效，拒绝启动。")
        QMessageBox.critical(None, "授权到期", error_msg)
        sys.exit(0)


# ==================== 5. 跨线程信号通讯器 ====================
class WorkerSignals(QObject):
    log_sig = pyqtSignal(str)          # 日志刷新信号
    finished_sig = pyqtSignal(str)     # 提取结束信号


# ==================== 6. 图像识别引擎 ====================
class VisionEngine:
    @staticmethod
    def locate_image_on_screen(template_path, confidence=0.75):
        """ 利用 OpenCV 识别 > 键，返回【中心偏下】坐标 """
        if not os.path.exists(template_path):
            return None
        try:
            screenshot = pyautogui.screenshot()
            screen_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            template_array = np.fromfile(template_path, dtype=np.uint8)
            template = cv2.imdecode(template_array, cv2.IMREAD_COLOR)
            if template is None:
                return None
            h, w = template.shape[:2]

            result = cv2.matchTemplate(screen_np, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                click_x = max_loc[0] + w // 2
                click_y = max_loc[1] + int(h * 0.75)  # 中心偏下点击
                return click_x, click_y
        except Exception:
            pass
        return None


# ==================== 7. PyQt6 主界面与控制中心 ====================
class TextExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网页信息跨页提取系统 v12.0")
        self.resize(960, 650)
        self.setWindowIcon(create_app_icon())

        self.stop_requested = False
        self.key_listener = None

        # 全路径智能检索定位 assets2
        self.assets_dir = self.locate_or_create_assets_dir()

        self.img_next_normal = os.path.join(self.assets_dir, "1_next_normal.png")
        self.img_next_hover = os.path.join(self.assets_dir, "2_next_hover.png")

        self.signals = WorkerSignals()
        self.signals.log_sig.connect(self.update_log)
        self.signals.finished_sig.connect(self.on_pipeline_finished)

        # 自动检索补全缺少的图片
        self.auto_scan_and_recover_assets()

        self.setup_ui()
        self.refresh_asset_status()

    def locate_or_create_assets_dir(self):
        """ 在多重可能目录下寻找 assets2，没有则自动创建 """
        possible_base_dirs = [
            os.getcwd(),
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "",
            os.path.dirname(os.path.abspath(__file__))
        ]

        for path in possible_base_dirs:
            if path:
                target = os.path.join(path, "assets2")
                if os.path.exists(target):
                    return target

        primary_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
            os.path.abspath(__file__))
        target = os.path.join(primary_dir, "assets2")
        os.makedirs(target, exist_ok=True)
        return target

    def auto_scan_and_recover_assets(self):
        """ 资产智能容错检索：如果在 assets2 里文件名不规范，自动更名归错 """
        if not os.path.exists(self.assets_dir):
            return

        files = os.listdir(self.assets_dir)
        for f in files:
            full_f = os.path.join(self.assets_dir, f)
            if not os.path.isfile(full_f): continue

            f_lower = f.lower()

            if not os.path.exists(self.img_next_normal):
                if "normal" in f_lower or "1_" in f_lower or "常态" in f_lower or "黑白" in f_lower:
                    try: shutil.copy2(full_f, self.img_next_normal)
                    except: pass

            if not os.path.exists(self.img_next_hover):
                if "hover" in f_lower or "2_" in f_lower or "高亮" in f_lower or "橙色" in f_lower:
                    try: shutil.copy2(full_f, self.img_next_hover)
                    except: pass

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ----------------- 左侧：控制面板 -----------------
        left_panel = QFrame()
        left_panel.setFixedWidth(340)
        left_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e0e0e0;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(12)

        title_lbl = QLabel("⚙️ 翻页按键特征配置")
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; border: none;")
        left_layout.addWidget(title_lbl)

        self.asset_mapping = [
            ("1. 下一页(常态/黑白)", self.img_next_normal),
            ("2. 下一页(高亮/橙色)", self.img_next_hover),
        ]

        self.asset_buttons = {}
        self.asset_previews = {}

        for label_text, target_path in self.asset_mapping:
            row = QHBoxLayout()
            btn = QPushButton(f"📂 {label_text}")
            btn.setFixedHeight(36)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda checked, p=target_path: self.import_image(p))

            preview = QLabel("—")
            preview.setFixedSize(65, 36)
            preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

            row.addWidget(btn, stretch=1)
            row.addWidget(preview)
            left_layout.addLayout(row)

            self.asset_buttons[target_path] = btn
            self.asset_previews[target_path] = preview

        left_layout.addSpacing(15)

        # 启动按钮
        self.btn_run = QPushButton("🚀 隐藏窗口并开始提取\n(按下空格键可随时强行停止)")
        self.btn_run.setFixedHeight(55)
        self.btn_run.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_run.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; font-size: 13px; border-radius: 6px; }
            QPushButton:hover { background-color: #219150; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        self.btn_run.clicked.connect(self.start_extraction)
        left_layout.addWidget(self.btn_run)

        # 运行状态栏
        self.lbl_status = QLabel("就绪，等待启动...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet(
            "background-color: #f8f9fa; border: 1px solid #ced4da; padding: 8px; border-radius: 4px; color: #555; font-size: 12px;")
        left_layout.addWidget(self.lbl_status)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # ----------------- 右侧：结果展示栏 -----------------
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e0e0e0;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)

        result_title = QLabel("📄 自动化提取汇总结果栏")
        result_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333333; border: none;")
        right_layout.addWidget(result_title)

        self.txt_result = QPlainTextEdit()
        self.txt_result.setPlaceholderText("提取的内容将会在流转结束后自动汇总呈现在这里...")
        self.txt_result.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.txt_result.setStyleSheet("""
            QPlainTextEdit {
                background-color: #fcfcfc;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                font-size: 12px;
                padding: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #2980b9;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        right_layout.addWidget(self.txt_result, stretch=1)

        # 操作快捷按钮
        btn_row = QHBoxLayout()

        self.btn_copy = QPushButton("📋 复制结果")
        self.btn_copy.setFixedHeight(36)
        self.btn_copy.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_copy.setStyleSheet("""
            QPushButton { background-color: #2980b9; color: white; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #3498db; }
        """)
        self.btn_copy.clicked.connect(self.copy_result_to_clipboard)

        self.btn_clear = QPushButton("🗑️ 清空面板")
        self.btn_clear.setFixedHeight(36)
        self.btn_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_clear.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.btn_clear.clicked.connect(self.clear_panel)

        btn_row.addWidget(self.btn_copy)
        btn_row.addWidget(self.btn_clear)
        right_layout.addLayout(btn_row)

        main_layout.addWidget(right_panel, stretch=1)

    def import_image(self, target_path):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择特征图片", "", "图片文件 (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copy(file_path, target_path)
                self.refresh_asset_status()
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"无法保存文件: {str(e)}")

    def refresh_asset_status(self):
        loaded_count = 0
        for target_path, btn in self.asset_buttons.items():
            preview = self.asset_previews[target_path]
            base_name = [item[0] for item in self.asset_mapping if item[1] == target_path][0]

            if os.path.exists(target_path):
                loaded_count += 1
                btn.setText(f"✅ {base_name}")
                btn.setStyleSheet(
                    "QPushButton { background-color: #e8f8f5; color: #27ae60; border: 1px solid #a3e4d7; text-align: left; padding-left: 8px; font-size: 11px; }")

                pix = QPixmap(target_path)
                if not pix.isNull():
                    scaled = pix.scaled(preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                    preview.setPixmap(scaled)
                    preview.setStyleSheet("border: 1px solid #27ae60; background: #fff;")
            else:
                btn.setText(f"❌ {base_name}")
                btn.setStyleSheet(
                    "QPushButton { background-color: #fadbd8; color: #c0392b; border: 1px solid #f5b7b1; text-align: left; padding-left: 8px; font-size: 11px; }")
                preview.setText("—")
                preview.setStyleSheet("border: 1px dashed #ccc; background: #f8f9fa; color: #aaa;")

        if loaded_count == 2:
            self.lbl_status.setText("✅ 已检索到并自动加载历史配置图片")

    def _on_key_press(self, key):
        if key == keyboard.Key.space:
            self.stop_requested = True
            self.signals.log_sig.emit("🛑 检测到空格键，强行中断提取！")

    def start_key_listener(self):
        self.stop_requested = False
        self.key_listener = keyboard.Listener(on_press=self._on_key_press)
        self.key_listener.start()

    def stop_key_listener(self):
        if self.key_listener and self.key_listener.is_alive():
            self.key_listener.stop()

    def start_extraction(self):
        if not os.path.exists(self.img_next_normal) or not os.path.exists(self.img_next_hover):
            QMessageBox.warning(self, "缺失图像特征", "请确保【常态】和【高亮】两张 > 键图片已导入！")
            return

        self.btn_run.setEnabled(False)
        self.lbl_status.setText("⏳ 准备运行，按空格键可随时终止...")
        QApplication.processEvents()

        self.start_key_listener()
        time.sleep(0.5)
        self.showMinimized()

        threading.Thread(target=self.run_pipeline, daemon=True).start()

    # ==================== 核心执行逻辑 ====================
    def run_pipeline(self):
        page_count = 1
        buffer_text = ""
        last_copied_text = ""

        time.sleep(1.5)

        # 1. 激活网页窗口焦点
        self.signals.log_sig.emit("🖱️ 点击网页以激活焦点...")
        pyautogui.click(300, 300)
        time.sleep(0.5)

        while not self.stop_requested:
            self.signals.log_sig.emit(f"🔄 正在复制第 {page_count} 页数据...")

            # 2. 全选复制当前页
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.4)

            current_page_text = pyperclip.paste()

            if page_count > 1 and current_page_text.strip() == last_copied_text.strip():
                self.signals.log_sig.emit("🛑 复制内容与上一页完全相同 (已到终点)，流程结束！")
                break

            last_copied_text = current_page_text
            buffer_text += f"==================== 第 {page_count} 页内容 ====================\n\n"
            buffer_text += current_page_text + "\n\n"

            # 3. 取消全选蓝色高亮
            pyautogui.click(300, 300)
            time.sleep(0.3)

            if self.stop_requested: break

            # 4. 检索是否存在 > 键（常态 / 高亮）
            self.signals.log_sig.emit("🔍 正在检索 > 翻页键...")
            next_pos = VisionEngine.locate_image_on_screen(self.img_next_hover, confidence=0.75)
            if not next_pos:
                next_pos = VisionEngine.locate_image_on_screen(self.img_next_normal, confidence=0.75)

            if not next_pos:
                self.signals.log_sig.emit("💡 彻底未找到可点击的 > 键，提取完全结束！")
                break

            if self.stop_requested: break

            # 5. 点击 > 翻页键（中心偏下）
            pyautogui.moveTo(next_pos[0], next_pos[1], duration=0.2)
            pyautogui.click()
            self.signals.log_sig.emit("👇 已点击 > 键！进入【死等 20 秒】缓冲...")

            # 6. 死等 20 秒
            for sec in range(20, 0, -1):
                if self.stop_requested:
                    break
                self.signals.log_sig.emit(f"⏳ 正在等待页面加载，剩余时间：{sec} 秒...")
                time.sleep(1.0)

            if self.stop_requested: break

            # 7. 点击 (300, 300) 确保下一轮焦点在网页上
            pyautogui.click(300, 300)
            time.sleep(0.5)

            page_count += 1

        self.stop_key_listener()

        if self.stop_requested:
            buffer_text += "\n⚠️ [用户触发空格键] 程序提前终止。"

        self.signals.finished_sig.emit(buffer_text)

    def update_log(self, text):
        self.lbl_status.setText(text)

    def on_pipeline_finished(self, final_text):
        self.showNormal()
        self.activateWindow()

        self.txt_result.setPlainText(final_text)
        pyperclip.copy(final_text)

        self.btn_run.setEnabled(True)

        if self.stop_requested:
            self.lbl_status.setText("🛑 用户已手动终止程序，结果已保存！")
            QMessageBox.warning(self, "强行终止", "已按空格键停止运行！\n终止前提取的数据已呈现在右侧面板中。")
        else:
            self.lbl_status.setText("🎉 提取完全结束，结果已存入剪贴板！")
            QMessageBox.information(self, "完成", "全页信息自动化提取成功！\n汇总结果已展示在右侧并自动同步至剪贴板。")

    def copy_result_to_clipboard(self):
        text = self.txt_result.toPlainText()
        if text.strip():
            pyperclip.copy(text)
            QMessageBox.information(self, "提示", "已成功复制到剪贴板！")
        else:
            QMessageBox.warning(self, "提示", "面板上没有可复制的内容。")

    def clear_panel(self):
        self.txt_result.clear()
        self.lbl_status.setText("面板已清空，就绪...")


# ==================== 8. 🚀 全新四段式启动总闸门 ====================
if __name__ == "__main__":
    if sys.platform == 'win32':
        import ctypes
        my_appid = 'mycompany.web_extractor.app.v12'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_appid)

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 1. 弹出闪屏
    splash = LoadingSplashScreen()
    splash.show()

    # 2. 推进进度（第一阶段：0% -> 30%）
    smooth_progress_to(splash, 0, 15, " ⚙️ 正在挂载全局核心总线... ")
    smooth_progress_to(splash, 16, 30, " 📂 正在索引图像匹配引擎... ")

    # 3. 双节点安全授权检查（第二阶段：30% -> 65% 会在 check_remote_license 内部接力推送）
    check_remote_license(splash)

    # 4. 授权通过，完成最后装箱（第三阶段：65% -> 100%）
    smooth_progress_to(splash, 66, 85, " 🔒 远程安全防线匹配通过... ")
    smooth_progress_to(splash, 86, 100, " 🎉 初始化就绪 ")
    time.sleep(0.1)

    # 5. 🌟 弹出免责协议与启动主界面
    disclaimer = DisclaimerWindow()
    if disclaimer.exec() == QDialog.DialogCode.Accepted:
        win = TextExtractorApp()
        splash.finish(win)
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)