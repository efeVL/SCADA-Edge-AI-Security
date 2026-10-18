import time
import random
import csv  
import logging 
from datetime import datetime 
from pymodbus.client import ModbusTcpClient

#Sadece hata loglarinin goster ki terminal tertemiz kalsin
logging.basicConfig(level=logging.ERROR)

CSV_DOSYA_ADI = "Veri_Setleri/scada_egitim_verisi.csv"
SUTUN_BASLIKLARI = ["Zaman_Damgasi","Gecikme_ms","Fonksiyon_Kodu","Deger","Etiket"]

def csv_hazirla():
    #Dosyayi "w" (write) moduyla acip basliklari yaziyoruz (Eski veriyi siler, sifirlar)
    with open(CSV_DOSYA_ADI, mode= 'w', newline='') as dosya: 
        yazici = csv.writer(dosya)
        yazici.writerow(SUTUN_BASLIKLARI)

def veri_uret(dongu_sayisi=100, host='127.0.0.1', port=502):
    """
    Belirlenen dongu sayisi kadar ag trafigi uretir.
    %80 Normal Trafik (Okuma), %20 Saldiri Trafigi simule eder.
    """
    print(f"🚀 Veri uretimi basliyor... Toplam {dongu_sayisi} paket gonderilecek ve kaydedilecek.")
    client= ModbusTcpClient(host, port=port)

    if not client.connect():
        print("❌ Sunucuya baglanilamadi! sanal_plc.py calisiyor mu?")
        return

    #Dosyayi "a" (append/ekle) moduyla aciyoruz ki eski veriler silinmesin, altina eklensin
    with open(CSV_DOSYA_ADI, mode='a', newline='') as dosya:
        yazici= csv.writer(dosya)

        for i in range (dongu_sayisi):
            #Anlik zaman (Milisaniye Hassasiyetinde)
            zaman_damgasi = datetime.now().strftime("Y-%m-%d %H:%M:%S.%f")[:-3]

            # %20 ihtimalle siber saldiri (Anomali), %80 ihtimalle normal akis
            saldiri_mi = random.random() < 0.20

            #Kronometreyi Baslat (Zaman gecikmesi siber guvenlikte en onemli tespittir)
            baslangic_zamani = time.perf_counter()

            if not saldiri_mi:
                #------------------NORMAL AKIS (Etiket:0)-------------------
                result = client.read_coils(address=0, count=1)
                fonksiyon_kodu = 1
                deger = 1 if not result.isError() and result.bits[0] else 0
                etiket = 0
            else:
                #-----------------SALDIRI AKISI (Etiket: 1)-----------------
                result = client.write_coil(address=0, value=False) #Salteri indir!
                fonksiyon_kodu= 5
                deger = 0
                etiket = 1

            #Kronometreyi durdur ve milisaniyeye (ms) cevir
            bitis_zamani = time.perf_counter()
            gecikme_ms = round((bitis_zamani - baslangic_zamani) * 1000, 4)

            #CSV dosyasina (Excel'e) o anki islemin raporunu yazdir
            yazici.writerow([zaman_damgasi, gecikme_ms, fonksiyon_kodu, deger, etiket])

            #Terminale de havali bir gidisat ekrani basalim
            durum = "🔥 SALDIRI" if saldiri_mi else "✅ NORMAL  "
            print(f"[{i+1}/{dongu_sayisi}] {durum} | Gecikme: {gecikme_ms}ms | Func: {fonksiyon_kodu} | Etiket: {etiket}")

            #Gercek SCADA Sistemleri surekli paket atmaz (cokerler)
            #O yuzden her an paket arasi 0.5 ile 1.5 saniye rastgele bir bekleme (Polling) koyduk.
            time.sleep(random.uniform(0.5, 1.5))

            #Onemli: Eger saldiri yaptiysak (Salter 0 olduysa), sistemin devam etmesi icin
            #Sanki operator gelmis ve salteri geri kaldirmis (Sistem kurtarilmis) gibi sessizce 1 yapiyoruz
            if saldiri_mi:
                client.write_coil(address=0, value= True)

        client.close()
        print("🎯 Veri seti basariyla uretildi ve dosyaya yazildi!")

if __name__ == "__main__":
    csv_hazirla()
    # Test icin simdilik 50 paket uretelim (Ileride bunu 5000 yapacagiz!)
    veri_uret(dongu_sayisi=5000)