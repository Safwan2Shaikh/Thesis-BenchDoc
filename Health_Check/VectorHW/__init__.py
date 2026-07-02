"""
__init__.py

VectorHW subpackage initialization for hardware device detection.
"""

from .device_detect import VectorDeviceDetector
from .ch_device_detect import ChannelDetector

__all__ = ['VectorDeviceDetector', 'ChannelDetector']
