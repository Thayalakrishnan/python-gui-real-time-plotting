""" @package Helpers
"""
from PyQt5.QtWidgets import QLCDNumber, QLabel, QHBoxLayout, QFrame, QSlider
from PyQt5.QtCore import Qt


def LCDWidgetHelper(
    lcd_object_name, lcd_has_decimal_point, lcd_size_width, lcd_size_height
) -> QLCDNumber:
    lcd = QLCDNumber()
    lcd.setFrameShape(QFrame.NoFrame)
    # lcd.setFrameShape(QFrame.StyledPanel)
    lcd.setFrameShadow(QFrame.Plain)
    lcd.setSmallDecimalPoint(lcd_has_decimal_point)
    lcd.setObjectName(lcd_object_name)
    lcd.setFixedSize(lcd_size_width, lcd_size_height)
    return lcd


def LabelWidgetHelper(label_text, size_width, size_height) -> QLabel:
    label = QLabel()
    label.setFixedSize(size_width, size_height)
    label.setFrameShape(QFrame.StyledPanel)
    label.setAlignment(Qt.AlignCenter)
    label.setText(label_text)
    return label


def SliderWidgetHelper(
    size_width, size_height, slider_min, slider_max, slider_step
) -> QSlider:
    slider = QSlider()
    slider.setFixedSize(size_width, size_height)
    slider.setOrientation(Qt.Horizontal)
    slider.setMinimum(slider_min)
    slider.setMaximum(slider_max)
    slider.setSingleStep(slider_step)
    return slider


def HBoxLayoutHelper(arr_widgets) -> QHBoxLayout:
    h_lay = QHBoxLayout()
    for w in arr_widgets:
        h_lay.addWidget(w)
    return h_lay


def GenericLayoutHelper(layout_box, arr_widgets):
    for w in arr_widgets:
        layout_box.addWidget(w)
    return layout_box
