from bleak import BleakClient, BleakScanner
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from idasen import IdasenDesk


app = FastAPI()
PORT_API = 8000


class BLEDevice(BaseModel):
    address: str
    name: str | None = None


class DeviceNotFoundError(Exception):
    pass


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/discover")
async def discover() -> list[BLEDevice]:
    devices = await BleakScanner.discover()
    response: list[BLEDevice] = []
    for d in devices:
        response.append(BLEDevice(address=d.address, name=d.name))
    return response


@app.get("/monitor")
async def monitor(device: BLEDevice):
    client = BleakClient(device.address)
    try:
        for service in client.services:
            print(f"Service: {service}")
        return {"status": "connected"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"Device {device.name} not found")


@app.post("/connect")
async def connect(device: BLEDevice):
    client = BleakClient(device.address)
    try:
        await client.connect()
        print(f"Connected to {device.name}")
        return {"status": "connected"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"Device {device.name} not found")


@app.post("/disconnect")
async def disconnect(device: BLEDevice):
    client = BleakClient(device.address)
    try:
        await client.disconnect()
        print(f"Disconnected from {device.name}")
        return {"status": "disconnected"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=f"Device {device.name} not found")
    finally:
        await client.disconnect()


@app.post("/set-height")
async def set_height(device: BLEDevice, height: float):
    desk = IdasenDesk(device.address)
    await desk.move_to_target(height)
    return {"status": "set height"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True, port=8080, host="0.0.0.0")

# ({"address": "ED:B1:91:47:29:55", "name": "Desk 0581"},)
