# Importare le librerie necessarie
from blue_st_sdk.manager import Manager
from blue_st_sdk.node import NodeListener
from blue_st_sdk.feature import FeatureListener

# Creare una classe di ascolto per ricevere le notifiche dai sensori
class Listener(FeatureListener):
    def on_update(self, feature, sample):
        print(feature)

# Connessione al dispositivo
SENSORTILE_MAC = 'E8:C4:2D:B4:00:5B'  # Inserire l'indirizzo MAC del dispositivo
bt_manager = Manager.instance()
bt_manager.discover(3)  # Scansione dispositivi per 3 secondi

# Filtrare per trovare il SensorTile.box PRO
discovered_devices = bt_manager.get_nodes()
device = None
for dev in discovered_devices:
    if dev.get_name() == "STBP_03":  # Sostituire con il nome del vostro dispositivo
        device = dev
        break

# Connessione al dispositivo
if device and device.connect():
    print("Connesso al dispositivo")
    # Ottenere le caratteristiche (sensori) disponibili
    features = device.get_features()
    # Selezionare un sensore (esempio: accelerometro)
    accelerometer = features[5]  # L'indice potrebbe variare a seconda del firmware
    # Aggiungere un listener per ricevere i dati
    accelerometer.add_listener(Listener())
    # Abilitare le notifiche
    device.enable_notifications(accelerometer)
    # Mantenere la connessione attiva per un certo periodo
    while True:
        if device.wait_for_notifications(10):
            continue
else:
    print("Impossibile connettersi al dispositivo")
