# generer_qr.py (à la racine du projet)

import qrcode

# URL du site (à adapter selon votre déploiement)
url = "http://127.0.0.1:8000/pointage/"

# Générer le QR Code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code_arrosage.png")

print("✅ QR Code généré : qr_code_arrosage.png")
print(f"📱 URL : {url}")