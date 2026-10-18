import asyncio
import logging
from pymodbus.datastore import (
    ModbusDeviceContext,
    ModbusSequentialDataBlock,
    ModbusServerContext,
)
from pymodbus.server import StartAsyncTcpServer

# Standart log formatı yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Adres 1'den başlayan 100 adet Coil (şalter) alanını 1 (TRUE / Kapalı) olarak ilklendiriyoruz
datablock = ModbusSequentialDataBlock(1, [1] * 100)

# Cihaz bellek haritası (co = Coils)
store = ModbusDeviceContext(co=datablock)

# Sunucu bağlamı (PyModbus 3.8+ standart parametre yapısı)
try:
    context = ModbusServerContext(devices=store, single=True)
except TypeError:
    context = ModbusServerContext(slaves=store, single=True)


async def main() -> None:
    logging.info("Modbus TCP Server initialized. Listening on 127.0.0.1:502...")
    await StartAsyncTcpServer(context=context, address=("127.0.0.1", 502))


if __name__ == "__main__":
    asyncio.run(main())