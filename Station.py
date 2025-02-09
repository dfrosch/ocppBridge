#!/usr/bin/env python3

import asyncio
import logging
from datetime import datetime
import ssl
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus

logging.basicConfig(level=logging.INFO)

_URL = "ws://10.98.182.8:32030/CP_1"

class ChargePoint(cp):
    async def send_BootNotification(self):
        request = call.BootNotification(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )
        response = await self.call(request)
        if response.status == RegistrationStatus.accepted:
            print("Connected to central system.")

    async def send_Authorize(self):
        request = call.Authorize(id_tag='CARD_TAG#1')
        response = await self.call(request)
        print(response)

    async def send_StartTransaction(self, connector_id, id_tag, meter_start):
        request = call.StartTransaction(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=meter_start,
            timestamp=datetime.utcnow().isoformat(),
        )
        response = await self.call(request)
        print(response)

    async def send_StopTransaction(self, meter_stop, transaction_id):
        request = call.StopTransaction(
            meter_stop=meter_stop,
            timestamp=datetime.utcnow().isoformat(),
            transaction_id=transaction_id
        )
        response = await self.call(request)
        print(response)

    async def send_Hearbeat(self):
        request = call.Heartbeat()
        response = await self.call(request)
        print(response)

    async def send_SetChargingProfile(self, connector_id, cs_charging_profiles):
        request = call.SetChargingProfile(
            connector_id=connector_id,
            cs_charging_profiles=cs_charging_profiles
        )
        response = await self.call(request)
        print(response)

    async def send_ClearChargingProfile(self, id, connector_id):
        request = call.ClearChargingProfile(
            id=id,
            connector_id=connector_id
        )
        response = await self.call(request)
        print(response)

    async def send_GetConfiguration(self):
        request = call.GetConfiguration(
            # Provide configuration keys if needed
        )
        response = await self.call(request)
        print(response)

    async def send_ChangeConfiguration(self, key, value):
        request = call.ChangeConfiguration(
            key=key,
            value=value
        )
        response = await self.call(request)
        print(response)

    async def send_status_notification(self, connector_id, error_code, status):
        request = call.StatusNotification(
            connector_id=connector_id,
            error_code=error_code,
            status=status
        )
        response = await self.call(request)
        print(response)


_ssl = False

async def main():
    ssl_context = None
    if _ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations('server.crt')
        ssl_context.check_hostname = False

    ws = await websockets.connect("wss://USER:PASSWD@127.0.0.1:9000/CP_1", subprotocols=["ocpp1.6"],
        ssl=ssl_context
        )

    cp = ChargePoint("CP_1", ws)
    #await asyncio.gather(cp.start(), cp.send_BootNotification())

    asyncio.create_task(cp.start())
    await cp.send_BootNotification()

    await cp.send_Authorize()
    await cp.send_StartTransaction(1, 'CARD_TAG#1', 10000)

    await cp.send_Authorize()
    await cp.send_StopTransaction(11000, 1)

    await cp.send_Hearbeat()

    # Example charging profile
    cs_charging_profiles = {
        "chargingProfileId": 1,
        "transactionId": 1,
        "stackLevel": 0,
        "chargingProfilePurpose": "TxProfile",
        "chargingProfileKind": "Absolute",
        "recurrencyKind": None,
        "validFrom": None,
        "validTo": None,
        "chargingSchedule": {
            "duration": 3600,
            "startSchedule": "2023-07-04T10:00:00Z",
            "chargingRateUnit": "W",
            "chargingSchedulePeriod": [
                {
                    "startPeriod": 0,
                    "limit": 11000,
                    "numberPhases": 3
                }
            ],
            "minChargingRate": 5000
        }
    }
    
    await cp.send_SetChargingProfile(
        connector_id=1,
        cs_charging_profiles=cs_charging_profiles
    )

    await cp.send_ClearChargingProfile(1, 1)
    await cp.send_GetConfiguration()
    await cp.send_ChangeConfiguration('Connectivity', 'Ethernet')
    await cp.send_status_notification(connector_id=1, error_code="NoError", status="Available")

if __name__ == "__main__":
    asyncio.run(main())
