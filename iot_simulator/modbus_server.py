import asyncio
import json
import redis.asyncio as redis
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_modbus_data(context):
    """Redis'ten akan verileri yakalayıp SCADA/Modbus haritasına yazar."""
    r = redis.Redis(host='localhost', port=6380, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe('sensor_data_stream')

    logger.info("📡 Modbus Sunucusu Redis'i dinlemeye başladı. SCADA için veriler hazırlanıyor...")

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
        if message is not None:
            data = json.loads(message['data'])


            register_id = 3
            slave_id = 0x00


            akim_degeri = int(data.get('akim_a', 0))
            context[slave_id].setValues(register_id, 6, [akim_degeri])

            ark_durumu = 1 if data.get('ark_durumu', 0) == 1 else 0
            context[slave_id].setValues(register_id, 1300, [ark_durumu])


            sicaklik_int = int(data.get('sicaklik_c', 0) * 10)
            pd_int = int(data.get('pd_seviyesi_pc', 0))
            ai_karari = 1 if data.get('is_synthetic_anomaly', False) else 0

            context[slave_id].setValues(register_id, 100, [sicaklik_int, pd_int, ai_karari])

        await asyncio.sleep(0.1)


async def run_modbus_server():

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 65536),
        co=ModbusSequentialDataBlock(0, [0] * 65536),
        hr=ModbusSequentialDataBlock(0, [0] * 65536),
        ir=ModbusSequentialDataBlock(0, [0] * 65536)
    )
    context = ModbusServerContext(slaves=store, single=True)

    asyncio.create_task(update_modbus_data(context))

    logger.info("🚀 GridSentinel Modbus TCP Sunucusu Başlatılıyor (Port: 5020)...")
    await StartAsyncTcpServer(context=context, address=("0.0.0.0", 5020))


if __name__ == "__main__":
    asyncio.run(run_modbus_server())