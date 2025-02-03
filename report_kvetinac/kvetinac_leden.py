from machine import Pin, ADC
import network
import urequests
import time
import gc

# Wi-Fi
SSID = ""  
PASSWORD = ""
SERVER_URL = ""

# co je kde připojený 
rele_pin = Pin(16, Pin.OUT)
soil_sensor = ADC(26)
led = Pin('LED', Pin.OUT)

# Funkce pro připojení k Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Připojuji se k Wi-Fi")
    while not wlan.isconnected():
        time.sleep(1)

    print("Připojeno")
    print("IP Adresa:", wlan.ifconfig()[0])

# Funkce pro získání stavu zavlažování z webu
def get_irrigation_status():
    try:
        response = urequests.get(SERVER_URL + "?action=get_status")
        status = response.text.strip()  # Získáme stav (ON nebo OFF)
        response.close()
        return status
    except Exception as e:
        print("Chyba při získávání stavu:", e)
        return "OFF"  # Pokud nastane chyba, považujeme stav za OFF

# Připojení k Wi-Fi
connect_to_wifi()

while True:
    # Čtení hodnoty vlhkosti půdy
    soil_value = soil_sensor.read_u16()
    print("Vlhkost půdy:", soil_value)

    # Odeslání dat na server
    data = "soil=" + str(soil_value)
    try:
        response = urequests.post(SERVER_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        print("Odpověď serveru:", response.text)
        response.close()
    except Exception as e:
        print("Chyba při odesílání:", e)

    # Získání stavu zavlažování z webu
    irrigation_status = get_irrigation_status()

    # Pokud je zavlažování ručně zapnuto nebo je půda suchá, zapneme relé
    if irrigation_status == "ON" or soil_value > 30000:
        rele_pin.value(1)
        led.value(1)
        print("Relé ZAP")
    else:
        rele_pin.value(0)
        led.value(0)
        print("Relé VYP")

    # Uvolnění paměti a pauza
    gc.collect()
    time.sleep(5)