import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# 1. STANDART LOGLAMA: Ekrana çıkacak mesajların saatli ve düzenli olmasını sağlar
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def read_plc_status(host: str = '127.0.0.1', port: int = 502) -> None:
    """
    SCADA İstemcisi (Master): Belirtilen IP ve Port üzerinden Sanal PLC'ye bağlanır,
    0. adresteki Trafo Şalteri (Coil) durumunu okur ve ekrana yazdırır.
    """
    # 2. İSTEMCİ (ELÇİ) OLUŞTURMA: "Şu adrese gitmek üzere hazırlan" diyoruz.
    client = ModbusTcpClient(host, port=port)

    try:
        # 3. KAPIYI ÇALMA (BAĞLANTI): Sunucuya TCP üzerinden bağlanmaya çalış.
        if client.connect():
            logging.info(f"✅ Sanal PLC'ye ({host}:{port}) basariyla baglanildi.")

            # 4. SORGULAMA (Function Code 1: Read Coils)
            # address=0 : Modbus'ta 1. adres, kodlamada 0. indekse denk gelir.
            # count=1   : Sadece 1 adet şalterin bilgisini getir.
            result = client.read_coils(address=0, count=1)

            # 5. YANITI YORUMLAMA (SCADA / HMI EKRANI)
            if not result.isError():
                salter_durumu = result.bits[0] # Gelen verinin ilk elemanını al
                
                if salter_durumu: # Eğer True (1) ise
                    logging.info("⚡ Trafo Salteri Durumu: TRUE (Enerji Var, Akim Geciyor)")
                else: # Eğer False (0) ise
                    logging.warning("❌ Trafo Salteri Durumu: FALSE (Enerji Kesik!)")
            else:
                logging.error("PLC'den veri okunamadi! Cihaz hata dondurdu.")
        else:
            logging.error(f"Baglanti reddedildi! {host}:{port} uzerinde PLC calisiyor mu?")
            
    # 6. GÜVENLİK AĞI (HATA YAKALAMA): Sistem çökerse buraya düşer, hatayı loglar.
    except ModbusException as e:
        logging.error(f"Modbus Haberlesme Hatasi: {e}")
    except Exception as e:
        logging.error(f"Bilinmeyen bir hata olustu: {e}")
        
    # 7. TEMİZLİK (FINALLY): Kod başarılı da olsa çökse de bu blok KESİNLİKLE çalışır.
    finally:
        client.close() # Portu serbest bırak (Açık unutulan portlar güvenlik açığıdır!)
        logging.info("🔌 PLC baglantisi guvenli sekilde kapatildi.")

# 8. MOTORU ÇALIŞTIRMA (TETİKLEYİCİ)
if __name__ == "__main__":
    read_plc_status()