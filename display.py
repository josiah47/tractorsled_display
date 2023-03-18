import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLCDNumber, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt

# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the RFM69 radio module.
import adafruit_rfm69

# Configure Packet Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
prev_packet = None

class Timer(QWidget):
	def __init__(self):
		super().__init__()

		self.initUI()

	def initUI(self):
		speedLCD = QLCDNumber(self)
		speedLCD.setStyleSheet("color: #00FF00")
		speedLCD.setDigitCount(7)
		speedLCD.display(5.14)

		distanceLCD = QLCDNumber(self)
		distanceLCD.setStyleSheet("color: #FF0000")
		distanceLCD.setDigitCount(7)
		distanceLCD.display(123)

		layout = QVBoxLayout(self)
		layout.addWidget(speedLCD)
		layout.addWidget(distanceLCD)
		self.setLayout(layout)
		self.setStyleSheet("background-color: black")

		self.speedLCD = speedLCD
		self.distanceLCD = distanceLCD

		self.setGeometry(100, 100, 300, 200)
		self.setWindowTitle('Timers')
		#self.show()
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setCursor(Qt.BlankCursor)
		self.showMaximized()

	def updateSpeedLCD(self,value):
		self.speedLCD.display(value)

	def updateDistanceLCD(self,value):
		self.distanceLCD.display(value)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	timer = Timer()

	def updateLCD():
		packet = None

		# check for packet rx
		packet = rfm69.receive()
		if packet is None:
			timer.updateSpeedLCD(0)
			timer.updateDistanceLCD(0)
		else:
			# Display the packet text and rssi
			prev_packet = packet
			packet_text = str(prev_packet, "utf-8")
			#print(packet_text)
			result = re.search(r"[Ss]([0-9]+)[Dd]([0-9]+)", packet_text)
			#print(result.groups())
			timer.updateSpeedLCD( format( float(result.group(1))/100.00, '.2f') )
			timer.updateDistanceLCD( format( float(result.group(2))/100.00, '.2f') )

	updateTimer = QTimer(app)
	updateTimer.timeout.connect(updateLCD)
	updateTimer.start(100)

	sys.exit(app.exec_())
