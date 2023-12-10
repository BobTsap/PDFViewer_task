import sys
import fitz
from PyQt5.Qt import *
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QPushButton, QFileDialog, QVBoxLayout,
    QWidget, QScrollArea, QGroupBox, QHBoxLayout)

from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint


class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        self.setGeometry(100, 100, 1100, 900)

        main_layout = QVBoxLayout()
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(main_layout)
        self.setCentralWidget(self.central_widget)

        button_group = QGroupBox()
        button_layout = QHBoxLayout(button_group)

        self.prev_button = QPushButton("< Previous")
        self.prev_button.clicked.connect(self.previous_page)
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next >")
        self.next_button.clicked.connect(self.next_page)
        button_layout.addWidget(self.next_button)

        self.select_button = QPushButton("Select PDF")
        self.select_button.clicked.connect(self.select_pdf)
        button_layout.addWidget(self.select_button)

        self.draw_button = QPushButton("Draw Rectangle")
        self.draw_button.clicked.connect(self.start_drawing)
        button_layout.addWidget(self.draw_button)

        main_layout.addWidget(button_group)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.label)
        self.scroll_layout.setAlignment(Qt.AlignLeft)

        self.pdf_document = None
        self.current_page = 0
        self.drawing = False
        self.start_pos = None
        self.end_pos = None
        self.rectangles = {}

    def select_pdf(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_document = fitz.open(file_path)
            self.show_page()

    def show_page(self):
        if self.pdf_document:
            pixmap = self.pdf_document[self.current_page].get_pixmap(
                matrix=fitz.Matrix(2, 2))
            pixmap.save('temp.png', 'PNG')
            pixmap = QPixmap('temp.png')
            self.label.setPixmap(pixmap)

            painter = QPainter(pixmap)
            pen = QPen(Qt.red)
            pen.setWidth(2)
            painter.setPen(pen)
            for rect in self.rectangles.get(self.current_page, []):
                start, end = rect
                painter.drawRect(start.x(), start.y(), end.x() -
                                 start.x(), end.y() - start.y())
            painter.end()

            self.label.setPixmap(pixmap)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()

    def next_page(self):
        if self.pdf_document and self.current_page < self.pdf_document.page_count - 1:
            self.current_page += 1
            self.show_page()

    def start_drawing(self):
        self.drawing = True

    def mousePressEvent(self, event):
        if self.drawing:
            self.start_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.end_pos = event.pos()
            self.draw_rectangle()

    def draw_rectangle(self):
        if self.start_pos and self.end_pos:
            pixmap = self.label.pixmap()
            painter = QPainter(pixmap)
            pen = QPen(Qt.red)
            pen.setWidth(2)
            painter.setPen(pen)

            start = self.start_pos
            end = self.end_pos

            start = start - self.scroll_area.pos() - self.label.pos() + \
                QPoint(0, self.scroll_area.verticalScrollBar().value())
            end = end - self.scroll_area.pos() - self.label.pos() + \
                QPoint(0, self.scroll_area.verticalScrollBar().value())

            painter.drawRect(start.x(), start.y(), end.x() -
                             start.x(), end.y() - start.y())
            painter.end()

            self.rectangles.setdefault(
                self.current_page, []).append((start, end))
            self.label.setPixmap(pixmap)
            self.drawing = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec_())
