import network
import time
import dht
import ujson
import urequests
from machine import Pin, ADC, I2C, RTC, PWM
import ssd1306  

# Konfigurasi Wi-Fi dan Ubidots
SSID = "Pak Coy"
PASSWORD = "hujanterus"
UBIDOTS_API_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/esp32-algo/"
API_TOKEN = "BBUS-aeBXun9ctIbADnaH3A7eYCUWhGAZ41"  # API TOKEN Ubidots
API_URL = "http://192.168.1.14:5000/data"  # IP Server to MongoDB

# Inisialisasi Komponen
led_red = Pin(2, Pin.OUT)
buzzer = PWM(Pin(21))
buzzer.freq(1000)
buzzer.duty(0)
pir = Pin(19, Pin.IN)
ldr = ADC(Pin(32))
ldr.atten(ADC.ATTN_11DB)
dht_sensor = dht.DHT11(Pin(4))
button = Pin(15, Pin.IN, Pin.PULL_UP)

# Inisialisasi OLED (I2C)
i2c = I2C(0, scl=Pin(22), sda=Pin(23))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Inisialisasi RTC
rtc = RTC()
rtc.datetime((2025, 2, 24, 0, 14, 30, 0, 0))

# Koneksi ke Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("🔄 Menghubungkan ke Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(1)

    print("✅ Terhubung ke Wi-Fi")
    print("📡 IP Address:", wlan.ifconfig()[0])
    oled.fill(0)
    oled.text("WiFi Terhubung", 10, 20)
    oled.text(wlan.ifconfig()[0], 10, 40)
    oled.show()
    time.sleep(2)

# Fungsi untuk mengirim data ke Ubidots
def send_data_to_ubidots(temp, humidity, ldr_value, movement, timestamp):
    try:
        payload = {
            "temperature": temp,
            "humidity": humidity,
            "ldr": ldr_value,
            "movement": movement,
            "timestamp": timestamp
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': API_TOKEN  # Menggunakan API Token
        }

        # Mengirim data ke Ubidots
        response = urequests.post(UBIDOTS_API_URL, json=payload, headers=headers)
        
        print(f"📤 Mengirim data ke Ubidots: {payload}")
        print("✅ Respon Ubidots:", response.text)
        response.close()

    except Exception as e:
        print("❌ Gagal mengirim data:", str(e))

# FUNGSI KIRIM DATA KE API MONGODB
def send_data_to_api(temp, humidity, ldr_value, movement, timestamp):
    try:
        payload = {
            "temperature": temp,
            "humidity": humidity,
            "ldr": ldr_value,
            "movement": movement,
            "timestamp": timestamp
        }

        headers = {'Content-Type': 'application/json'}

        # Kirim data ke API
        response = urequests.post(API_URL, json=payload, headers=headers)

        print(f"📤 Mengirim data ke API: {payload}")
        print("✅ Respon API:", response.text)
        response.close()

    except Exception as e:
        print("❌ Gagal mengirim data:", str(e))


# Mulai program
connect_wifi()

while True:
    if button.value() == 0:
        oled.fill(0)
        oled.text("Sistem dimulai!", 20, 30)
        oled.show()
        time.sleep(1)

        while button.value() == 0:
            print("\n📡 Mengukur Data Sensor...")
            tahun, bulan, hari, _, jam, menit, detik, _ = rtc.datetime()
            timestamp = f"{tahun:04d}/{bulan:02d}/{hari:02d} {jam:02d}:{menit:02d}:{detik:02d}"

            try:
                dht_sensor.measure()
                temp, humidity = dht_sensor.temperature(), dht_sensor.humidity()
            except:
                temp, humidity = "N/A", "N/A"

            ldr_value = ldr.read()
            light_intensity = "Terang" if ldr_value > 10 else "Redup"
            movement = "Ya" if pir.value() == 1 else "Tidak"

            if movement == "Ya":
                led_red.value(1)
            else:
                led_red.value(0)

            if temp != "N/A" and float(temp) > 35:
                buzzer.duty(512)
                print("🚨 Peringatan: Suhu tinggi!")
                oled.fill(0)
                oled.text("!! ALERT !!", 20, 10)
                oled.text(f"Temp: {temp}C", 20, 30)
                oled.text("Suhu Terlalu Panas!", 5, 50)
                oled.show()
                time.sleep(3)
            else:
                buzzer.duty(0)
                print("✅ Suhu normal")

            # Kirim data ke Ubidots
            send_data_to_ubidots(temp, humidity, ldr_value, movement, timestamp)
            send_data_to_api(temp, humidity, ldr_value, movement, timestamp)
            
            oled.fill(0)
            oled.text("Sensor Data:", 0, 0)
            oled.text(f"T: {temp}C", 0, 16)
            oled.text(f"H: {humidity}%", 0, 26)
            oled.text(f"LDR: {ldr_value}", 0, 36)
            oled.text(f"Intensitas: {light_intensity}", 0, 46)
            oled.text(f"Gerakan: {movement}", 0, 56)
            oled.show()
            
            print("----------------------------")
            print(f"🌡 Suhu        : {temp}°C")
            print(f"💧 Kelembaban  : {humidity}%")
            print(f"☀ LDR Value   : {ldr_value}")
            print(f"☀ Intensitas  : {light_intensity}")
            print(f"🚶 Gerakan     : {movement}")
            print("----------------------------")
            
            time.sleep(2)  # Tunggu 2 detik sebelum pengiriman data berikutnya
    else:
        oled.fill(0)
        oled.text("Sistem Mati", 20, 30)
        oled.show()
        led_red.value(0)
        buzzer.duty(0)
        time.sleep(0.1)
