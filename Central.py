#!/usr/bin/env python

import asyncio
import ssl
import logging
from datetime import datetime
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    @on('BootNotification')
    def on_BootNotification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatus.accepted,
        )

    @on('Authorize')
    async def on_Authorize(self, id_tag, **kwargs):
        return call_result.Authorize(
            id_tag_info={
                'status': 'Accepted'
            }
        )

    @on('StartTransaction')
    async def on_StartTransaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        return call_result.StartTransaction(
            transaction_id=1,
            id_tag_info={
                'status': 'Accepted'
            }
        )
    @on('StopTransaction')
    async def on_StopTransaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        return call_result.StopTransaction(
            id_tag_info={
                'status': 'Accepted'
            }
        )

    @on('Heartbeat')
    async def on_heartbeat(self):
        return call_result.Heartbeat(
            current_time=datetime.utcnow().isoformat(),
        )

    @on('SetChargingProfile')
    async def on_set_charging_profile(self, connector_id, cs_charging_profiles, **kwargs):
        return call_result.SetChargingProfile(
            status='Accepted'
        )


async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError:
        logging.error("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning(
            "Protocols Mismatched | Expected Subprotocols: %s,"
            " but client supports  %s | Closing connection",
            websocket.available_subprotocols,
            requested_protocols,
        )
        return await websocket.close()

    charge_point_id = path.strip("/")
    cp = ChargePoint(charge_point_id, websocket)

    try:
        await cp.start()
    except:
        logging.debug('Station has closed the connexion')


async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"], ssl=ssl_context
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


if __name__ == "__main__":
    # asyncio.run() is used when running this example with Python >= 3.7v
    asyncio.run(main())
