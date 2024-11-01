'''
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, 
                             QPushButton, QLabel, QGridLayout, QMessageBox, QScrollArea, QListWidgetItem,
                             QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon

class CameraView(QLabel):
    def __init__(self, camera_id):
        super().__init__()
        self.fullscreen = False
        
        
        self.camera_id = camera_id
        self.setStyleSheet("background-color: #2d2d2d; min-height: 200px; min-width: 200px;")
        self.setText(f"Camera {camera_id}\nDisconnected")
        self.setAlignment(Qt.AlignCenter)
        self.status = "disconnected"

    def update_frame(self, frame):
        self.setPixmap(QPixmap.fromImage(frame))

    def set_status(self, status):
        self.status = status
        color = "green" if status == "connected" else "red"
        self.setText(f"Camera {self.camera_id}\n{status.capitalize()}")
        self.setStyleSheet(f"background-color: #2d2d2d; min-height: 200px; min-width: 200px; color: {color};")
        
    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.setWindowFlags(Qt.Window)
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.setWindowFlags(Qt.Widget)
            self.showNormal()
            self.fullscreen = False
class ResultView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.license_plate_label = QLabel("License Plate: ")
        self.license_plate_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.vehicle_image = QLabel()
        self.vehicle_image.setStyleSheet("background-color: #2d2d2d; min-height: 200px; min-width: 200px;")
        self.vehicle_image.setAlignment(Qt.AlignCenter)
        self.vehicle_image.setText("Vehicle Image")

        layout.addWidget(self.license_plate_label)
        layout.addWidget(self.vehicle_image)
        layout.addStretch()

    def update_result(self, license_plate, image):
        self.license_plate_label.setText(f"License Plate: {license_plate}")
        self.vehicle_image.setPixmap(QPixmap.fromImage(image))
        
class ResultView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("font-size: 14px;")
        
        layout.addWidget(QLabel("Detection Results:"))
        layout.addWidget(self.results_list)

    def update_result(self, license_plate, image):
        item = QListWidgetItem(f"License Plate: {license_plate}")
        item.setIcon(QIcon(QPixmap.fromImage(image)))
        self.results_list.insertItem(0, item)  # Add new result at the top
        if self.results_list.count() > 10:  # Keep only the last 10 results
            self.results_list.takeItem(10)

class CameraPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.cameras = {}

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Camera...")
        self.search_bar.textChanged.connect(self.filter_cameras)
        
        self.camera_list = QListWidget()
        
        # Group box for camera controls
        control_group = QGroupBox("Camera Controls")
        control_layout = QVBoxLayout(control_group)
        
        self.add_btn = QPushButton("Add Camera")
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.playback_btn = QPushButton("Playback")
        
        self.add_btn.clicked.connect(self.add_camera)
        self.connect_btn.clicked.connect(self.connect_camera)
        self.disconnect_btn.clicked.connect(self.disconnect_camera)
        self.playback_btn.clicked.connect(self.playback_camera)
        
        control_layout.addWidget(self.add_btn)
        control_layout.addWidget(self.connect_btn)
        control_layout.addWidget(self.disconnect_btn)
        control_layout.addWidget(self.playback_btn)
        
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.camera_list)
        left_layout.addWidget(control_group)
        
        # Right panel (camera grid and result view)
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        
        # Camera grid (3x3)
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.camera_views = []
        for i in range(9):
            view = CameraView(i+1)
            self.grid_layout.addWidget(view, i // 3, i % 3)
            self.camera_views.append(view)
        
        # Make the grid scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidget(grid_widget)
        scroll_area.setWidgetResizable(True)
        
        # Result view
        self.result_view = ResultView()
        
        right_layout.addWidget(scroll_area, 2)
        right_layout.addWidget(self.result_view, 1)
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 4)

    def add_camera(self):
        camera_id = len(self.cameras) + 1
        self.cameras[camera_id] = {"connected": False}
        self.camera_list.addItem(f"Camera {camera_id}")

    def connect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to connect.")
            return
        
        camera_id = int(selected_items[0].text().split()[-1])
        if not self.cameras[camera_id]["connected"]:
            self.cameras[camera_id]["connected"] = True
            QMessageBox.information(self, "Success", f"Camera {camera_id} connected successfully.")

    def disconnect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to disconnect.")
            return
        
        camera_id = int(selected_items[0].text().split()[-1])
        if self.cameras[camera_id]["connected"]:
            self.cameras[camera_id]["connected"] = False
            QMessageBox.information(self, "Success", f"Camera {camera_id} disconnected.")

    def playback_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera for playback.")
            return
        
        camera_id = int(selected_items[0].text().split()[-1])
        QMessageBox.information(self, "Playback", f"Starting playback for Camera {camera_id}")
        # Add your playback logic here

    def filter_cameras(self, text):
        for i in range(self.camera_list.count()):
            item = self.camera_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def update_detection_result(self, license_plate, image):
        self.result_view.update_result(license_plate, image)
        
        '''
import sys
import json
import time
import logging
import cv2
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QFileDialog, QFormLayout,
                            QWidget, QListWidget, QGridLayout, QMessageBox, QScrollArea, 
                            QListWidgetItem, QGroupBox, QProgressBar, QStatusBar, QShortcut)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon, QKeySequence

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CameraConnection(QThread):
    connection_lost = pyqtSignal(int)
    connection_restored = pyqtSignal(int)
    
    def __init__(self, camera_id, camera_info):
        super().__init__()
        self.camera_id = camera_id
        self.camera_info = camera_info
        self.retry_count = 0
        self.max_retries = 3
        self._running = True
        
    def run(self):
        while self._running:
            if not self.check_connection():
                self.connection_lost.emit(self.camera_id)
                self.attempt_reconnect()
            time.sleep(5)
    
    def check_connection(self):
        try:
            # Implement connection check based on protocol
            return True
        except Exception as e:
            logger.error(f"Connection check failed for camera {self.camera_id}: {str(e)}")
            return False
            
    def attempt_reconnect(self):
        while self.retry_count < self.max_retries and self._running:
            try:
                logger.info(f"Attempting to reconnect camera {self.camera_id}")
                # Implement reconnection logic
                self.connection_restored.emit(self.camera_id)
                self.retry_count = 0
                return True
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {str(e)}")
                self.retry_count += 1
                time.sleep(2)
        return False
    
    def stop(self):
        self._running = False

class AddCameraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Camera")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Camera Name
        self.camera_name = QLineEdit()
        form_layout.addRow("Camera Name:", self.camera_name)

        # Protocol
        self.protocol = QComboBox()
        self.protocol.addItems(["RTSP", "HTTP", "Local File"])
        self.protocol.currentTextChanged.connect(self.on_protocol_changed)
        form_layout.addRow("Protocol:", self.protocol)

        # RTSP URL
        self.rtsp_url = QLineEdit()
        form_layout.addRow("RTSP URL:", self.rtsp_url)

        # IP Address
        self.ip_address = QLineEdit()
        form_layout.addRow("IP Address:", self.ip_address)

        # Port
        self.port = QLineEdit()
        form_layout.addRow("Port:", self.port)

        # Username
        self.username = QLineEdit()
        form_layout.addRow("Username:", self.username)

        # Password
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password)

        # File Path
        self.file_path = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_btn)
        form_layout.addRow("File Path:", file_layout)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        self.apply_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.apply_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.on_protocol_changed(self.protocol.currentText())

    def validate_and_accept(self):
        try:
            self.validate_camera_info(self.get_camera_info())
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def validate_camera_info(self, info):
        if not info["name"]:
            raise ValueError("Camera name is required")
            
        if info["protocol"] == "RTSP":
            if not info["rtsp_url"].startswith("rtsp://"):
                raise ValueError("Invalid RTSP URL format")
        elif info["protocol"] == "HTTP":
            if not info["ip_address"]:
                raise ValueError("IP address is required for HTTP protocol")
            try:
                port = int(info["port"])
                if port < 0 or port > 65535:
                    raise ValueError("Port must be between 0 and 65535")
            except ValueError:
                raise ValueError("Port must be a valid number")

    def on_protocol_changed(self, protocol):
        is_rtsp = protocol == "RTSP"
        is_http = protocol == "HTTP"
        is_local = protocol == "Local File"

        self.rtsp_url.setVisible(is_rtsp)
        self.ip_address.setVisible(is_http)
        self.port.setVisible(is_http)
        self.username.setVisible(is_rtsp or is_http)
        self.password.setVisible(is_rtsp or is_http)
        self.file_path.setVisible(is_local)
        self.browse_btn.setVisible(is_local)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Video File", 
            "", 
            "Video Files (*.mp4 *.avi *.mov)"
        )
        if file_name:
            self.file_path.setText(file_name)

    def get_camera_info(self):
        protocol = self.protocol.currentText()
        return {
            "name": self.camera_name.text(),
            "protocol": protocol,
            "rtsp_url": self.rtsp_url.text() if protocol == "RTSP" else "",
            "ip_address": self.ip_address.text() if protocol == "HTTP" else "",
            "port": self.port.text() if protocol == "HTTP" else "",
            "username": self.username.text() if protocol in ["RTSP", "HTTP"] else "",
            "password": self.password.text() if protocol in ["RTSP", "HTTP"] else "",
            "file_path": self.file_path.text() if protocol == "Local File" else ""
        }

class CameraView(QLabel):
    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.fullscreen = False
        self.stream = None
        self._is_running = False
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(640, 320)
        self.setStyleSheet("background-color: #2d2d2d;")
        self.setText(f"Camera {self.camera_id}\nDisconnected")
        self.setAlignment(Qt.AlignCenter)
        self.status = "disconnected"
        
                # Add status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(10, 10)
        self.status_indicator.setStyleSheet("""
            QLabel {
                background-color: red;
                border-radius: 5px;
            }
        """)
        
        # Add overlay layout
        overlay = QHBoxLayout()
        overlay.addWidget(self.status_indicator)
        overlay.addStretch()
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(overlay)
        main_layout.addStretch()
        
        
        
            # Add quick actions
        actions_layout = QHBoxLayout()
        
        self.snapshot_btn = QPushButton("📷")
        self.record_btn = QPushButton("⏺")
        self.settings_btn = QPushButton("⚙")
        
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.record_btn.clicked.connect(self.toggle_recording)
        self.settings_btn.clicked.connect(self.show_settings)
        
        for btn in [self.snapshot_btn, self.record_btn, self.settings_btn]:
            btn.setFixedSize(30, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.5);
                    border: none;
                    color: white;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background-color: rgba(0, 0, 0, 0.7);
                }
            """)
            actions_layout.addWidget(btn)
        
        actions_layout.addStretch()
        main_layout.addLayout(actions_layout)

    def take_snapshot(self):
        # Implement snapshot functionality
        pass

    def toggle_recording(self):
        # Implement recording functionality
        sender = self.sender()
        if sender.isChecked():
            sender.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 0, 0, 0.5);
                }
            """)
        else:
            sender.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 0, 0, 0.5);
                }
            """)

    def show_settings(self):
        # Implement settings dialog
        pass

    def set_status(self, status):
        self.status = status
        color = "green" if status == "connected" else "red"
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    def start_stream(self):
        if not self._is_running:
            self._is_running = True
            self.stream = cv2.VideoCapture()
            logger.info(f"Started stream for camera {self.camera_id}")

    def stop_stream(self):
        if self._is_running:
            self._is_running = False
            if self.stream:
                self.stream.release()
                self.stream = None
            logger.info(f"Stopped stream for camera {self.camera_id}")

    def update_frame(self, frame):
        self.setPixmap(QPixmap.fromImage(frame))

    def set_status(self, status):
        self.status = status
        color = "green" if status == "connected" else "red"
        self.setText(f"Camera {self.camera_id}\n{status.capitalize()}")
        self.setStyleSheet(f"background-color: #2d2d2d; min-height: 200px; min-width: 200px; color: {color};")
        
    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()

    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.setWindowFlags(Qt.Window)
            self.showFullScreen()
            self.fullscreen = True
        else:
            self.setWindowFlags(Qt.Widget)
            self.showNormal()
            self.fullscreen = False

    def closeEvent(self, event):
        self.stop_stream()
        super().closeEvent(event)

class ResultView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("font-size: 14px;")
        
        layout.addWidget(QLabel("Detection Results:"))
        layout.addWidget(self.results_list)

    def update_result(self, license_plate, image):
        item = QListWidgetItem(f"License Plate: {license_plate}")
        item.setIcon(QIcon(QPixmap.fromImage(image)))
        self.results_list.insertItem(0, item)
        if self.results_list.count() > 10:
            self.results_list.takeItem(10)

class CameraPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layout = "3x3"
        self.cameras = {}
        self.camera_connections = {}
        self.init_ui()
        self.load_camera_config()
        self.setup_shortcuts()

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
                # Thêm nút toggle theme
        self.theme_btn = QPushButton()
        self.theme_btn.setCheckable(True)
        self.theme_btn.clicked.connect(self.toggle_theme)
        control_layout.addWidget(self.theme_btn)
        
        # Thêm vào class CameraPage trong init_ui()
        grid_controls = QWidget()
        grid_controls_layout = QHBoxLayout(grid_controls)

        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")
        self.fit_btn = QPushButton("Fit")
        self.rotate_btn = QPushButton("⟳")

        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out) 
        self.fit_btn.clicked.connect(self.fit_to_view)
        self.rotate_btn.clicked.connect(self.rotate_view)

        grid_controls_layout.addWidget(self.zoom_in_btn)
        grid_controls_layout.addWidget(self.zoom_out_btn)
        grid_controls_layout.addWidget(self.fit_btn)
        grid_controls_layout.addWidget(self.rotate_btn)

        control_layout.addWidget(grid_controls)

        # Thêm các phương thức xử lý
        def zoom_in(self):
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, CameraView):
                    current_size = widget.size()
                    widget.setFixedSize(current_size.width() * 1.2, current_size.height() * 1.2)

        def zoom_out(self):
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, CameraView):
                    current_size = widget.size()
                    widget.setFixedSize(current_size.width() / 1.2, current_size.height() / 1.2)

        def fit_to_view(self):
            scroll_area = self.findChild(QScrollArea)
            available_size = scroll_area.viewport().size()
            rows, cols = map(int, self.current_layout.split('x'))
            
            width = available_size.width() / cols
            height = available_size.height() / rows
            
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, CameraView):
                    widget.setFixedSize(width, height)

        def rotate_view(self):
            current = self.layout_selector.currentText()
            rows, cols = map(int, current.split('x'))
            new_layout = f"{cols}x{rows}"
            self.layout_selector.setCurrentText(new_layout)
                
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Camera...")
        self.search_bar.textChanged.connect(self.filter_cameras)
        
        self.camera_list = QListWidget()
        
        # Controls
        control_group = QGroupBox("Camera Controls")
        control_layout = QVBoxLayout(control_group)
        
        self.layout_selector = QComboBox()
        self.layout_selector.addItems(["2x2", "3x3", "4x4", "2x3", "3x2"])
        self.layout_selector.setCurrentText(self.current_layout)
        self.layout_selector.currentTextChanged.connect(self.change_layout)
        
        control_layout.addWidget(QLabel("Select Layout:"))
        control_layout.addWidget(self.layout_selector)
        
        self.loading_spinner = QProgressBar()
        self.loading_spinner.setVisible(False)
        
        self.add_btn = QPushButton("Add Camera")
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.playback_btn = QPushButton("Playback")
        
        self.add_btn.clicked.connect(self.add_camera)
        self.connect_btn.clicked.connect(self.connect_camera)
        self.disconnect_btn.clicked.connect(self.disconnect_camera)
        self.playback_btn.clicked.connect(self.playback_camera)
        
        for btn in [self.add_btn, self.connect_btn, self.disconnect_btn, self.playback_btn]:
            control_layout.addWidget(btn)
        
        control_layout.addWidget(self.loading_spinner)
        
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.camera_list)
        left_layout.addWidget(control_group)
        
        # Right panel
        right_panel = QWidget()
        right_layout = QHBoxLayout(right_panel)
        
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        self.grid_layout.setSpacing(10)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(grid_widget)
        scroll_area.setWidgetResizable(True)
        
        self.result_view = ResultView()
        
        right_layout.addWidget(scroll_area, 1)
        right_layout.addWidget(self.result_view, 1)
        
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 4)
        
        # Status bar
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)
        
    # Thêm phương thức toggle_theme
    def toggle_theme(self):
        if self.theme_btn.isChecked():
            # Dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #404040;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QLineEdit {
                    background-color: #404040;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QComboBox {
                    background-color: #404040;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #404040;
                    border: 1px solid #555555;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 5px;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                }
            """)

    def setup_shortcuts(self):
        self.connect_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.connect_shortcut.activated.connect(self.connect_camera)
        
        self.disconnect_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.disconnect_shortcut.activated.connect(self.disconnect_camera)

    def save_camera_config(self):
        config = {
            'cameras': self.cameras,
            'layout': self.current_layout
        }
        try:
            with open('camera_config.json', 'w') as f:
                json.dump(config, f)
            logger.info("Camera configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save camera configuration: {str(e)}")

    def load_camera_config(self):
        try:
            with open('camera_config.json', 'r') as f:
                config = json.load(f)
                self.cameras = config['cameras']
                self.current_layout = config['layout']
                self.layout_selector.setCurrentText(self.current_layout)
                self.update_camera_list()
            logger.info("Camera configuration loaded successfully")
        except FileNotFoundError:
            logger.info("No camera configuration file found")
        except Exception as e:
            logger.error(f"Failed to load camera configuration: {str(e)}")

    def update_camera_list(self):
        self.camera_list.clear()
        for camera_id, camera_info in self.cameras.items():
            self.camera_list.addItem(f"Camera {camera_id}: {camera_info['info']['name']}")

    def add_camera(self):
        dialog = AddCameraDialog(self)
        if dialog.exec_():
            try:
                camera_info = dialog.get_camera_info()
                camera_id = len(self.cameras) + 1
                self.cameras[camera_id] = {
                    "info": camera_info,
                    "connected": False
                }
                self.camera_list.addItem(f"Camera {camera_id}: {camera_info['name']}")
                self.update_grid_layout()
                self.save_camera_config()
                logger.info(f"Added new camera: {camera_info['name']}")
            except Exception as e:
                logger.error(f"Failed to add camera: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to add camera: {str(e)}")

    def connect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to connect.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        
        try:
            self.loading_spinner.setVisible(True)
            if not self.cameras[camera_id]["connected"]:
                camera_info = self.cameras[camera_id]["info"]
                
                # Start camera connection thread
                connection = CameraConnection(camera_id, camera_info)
                connection.connection_lost.connect(self.handle_connection_lost)
                connection.connection_restored.connect(self.handle_connection_restored)
                self.camera_connections[camera_id] = connection
                connection.start()
                
                self.cameras[camera_id]["connected"] = True
                self.update_camera_status(camera_id, "connected")
                logger.info(f"Camera {camera_id} connected successfully")
                QMessageBox.information(self, "Success", f"Camera {camera_id} connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect camera {camera_id}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to connect camera: {str(e)}")
        finally:
            self.loading_spinner.setVisible(False)

    def disconnect_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera to disconnect.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        
        try:
            if self.cameras[camera_id]["connected"]:
                if camera_id in self.camera_connections:
                    self.camera_connections[camera_id].stop()
                    del self.camera_connections[camera_id]
                
                self.cameras[camera_id]["connected"] = False
                self.update_camera_status(camera_id, "disconnected")
                logger.info(f"Camera {camera_id} disconnected successfully")
                QMessageBox.information(self, "Success", f"Camera {camera_id} disconnected.")
        except Exception as e:
            logger.error(f"Failed to disconnect camera {camera_id}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to disconnect camera: {str(e)}")

    def handle_connection_lost(self, camera_id):
        self.update_camera_status(camera_id, "disconnected")
        self.status_bar.showMessage(f"Connection lost to Camera {camera_id}")
        logger.warning(f"Connection lost to Camera {camera_id}")

    def handle_connection_restored(self, camera_id):
        self.update_camera_status(camera_id, "connected")
        self.status_bar.showMessage(f"Connection restored to Camera {camera_id}")
        logger.info(f"Connection restored to Camera {camera_id}")

    def update_camera_status(self, camera_id, status):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, CameraView) and widget.camera_id == camera_id:
                widget.set_status(status)
                break

    def playback_camera(self):
        selected_items = self.camera_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a camera for playback.")
            return
        
        camera_id = int(selected_items[0].text().split(':')[0].split()[-1])
        logger.info(f"Starting playback for Camera {camera_id}")
        QMessageBox.information(self, "Playback", f"Starting playback for Camera {camera_id}")

    def filter_cameras(self, text):
        for i in range(self.camera_list.count()):
            item = self.camera_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def change_layout(self, new_layout):
        self.current_layout = new_layout
        self.update_grid_layout()
        self.save_camera_config()
        logger.info(f"Changed layout to {new_layout}")

    def update_grid_layout(self):
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Set up new grid
        rows, cols = map(int, self.current_layout.split('x'))
        
        for i, (camera_id, camera_info) in enumerate(self.cameras.items()):
            if i < rows * cols:
                view = CameraView(camera_id)
                if camera_info["connected"]:
                    view.set_status("connected")
                self.grid_layout.addWidget(view, i // cols, i % cols)

        # Resize grid
        grid_widget = self.grid_layout.parentWidget()
        total_width = cols * 210
        total_height = rows * 210
        grid_widget.setFixedSize(total_width, total_height)

    def update_detection_result(self, license_plate, image):
        self.result_view.update_result(license_plate, image)

    def closeEvent(self, event):
        try:
            # Stop all camera connections
            for connection in self.camera_connections.values():
                connection.stop()
            
            # Save configuration
            self.save_camera_config()
            
            logger.info("Application shutting down")
            event.accept()
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = CameraPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()