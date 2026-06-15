# PyEGPS

Python library for controlling [Energenie powerstrips](https://energenie.com/item.aspx?id=7415).

This library is meant to be used with [Home Assistant](https://www.home-assistant.io/) components.

### Installation:
```
pip install pyegps
```
Make sure the user has the necessary rights to access the device. E.g.:
find your device with:
```bash
lsusb
#e.g.: Bus 001 Device 005: ID 04b4:fd15 Cypress Semiconductor Corp. Energenie EG-PMS2
```

```bash
sudo echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="fd15", MODE="0666"' > /lib/udev/rules.d/60-energenie-usb.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```



### Command Line Interace (CLI)
For help, see:
```
python3 -m pyegps --help
```

### Acknowledgment
Thanks go to the author of 'pysispm' for figuring out which HID-Reports are used for communicating with the device:
https://github.com/xypron/pysispm
