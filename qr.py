import qrcode
from PIL import Image

url = "https://moneyapptrading-qp9rcuqykkpbb5asaeqkdn.streamlit.app/"
img = qrcode.make(url)
img.save("trading_app_qr.png")
img.show()  # This will open the QR code image