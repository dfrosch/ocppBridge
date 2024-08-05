#!/usr/bin/env python3

import asyncio
import ssl
import logging
from datetime import datetime
import websockets
import base64
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus

logging.basicConfig(level=logging.INFO)

SkipSchemVal=False

class ChargePoint(cp):
    @on('BootNotification', skip_schema_validation=SkipSchemVal)
    def on_BootNotification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=60,
            status=RegistrationStatus.accepted,
        )

    @on('Authorize', skip_schema_validation=SkipSchemVal)
    async def on_Authorize(self, id_tag, **kwargs):
        return call_result.Authorize(
            id_tag_info={
                'status': 'Accepted'
            }
        )

    @on('StartTransaction', skip_schema_validation=SkipSchemVal)
    async def on_StartTransaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        return call_result.StartTransaction(
            transaction_id=1,
            id_tag_info={
                'status': 'Accepted'
            }
        )
    @on('StopTransaction', skip_schema_validation=SkipSchemVal)
    async def on_StopTransaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        return call_result.StopTransaction(
            id_tag_info={
                'status': 'Accepted'
            }
        )

    @on('Heartbeat', skip_schema_validation=SkipSchemVal)
    async def on_Heartbeat(self):
        return call_result.Heartbeat(
            current_time=datetime.utcnow().isoformat(),
        )

    @on('SetChargingProfile', skip_schema_validation=SkipSchemVal)
    async def on_SetChargingProfile(self, connector_id, cs_charging_profiles, **kwargs):
        return call_result.SetChargingProfile(
            status='Accepted'
        )

    @on('ClearChargingProfile', skip_schema_validation=SkipSchemVal)
    async def on_ClearChargingProfile(self, **kwargs):
        return call_result.ClearChargingProfile(
            status='Accepted'
        )

    @on('GetConfiguration', skip_schema_validation=SkipSchemVal)
    async def on_GetConfiguration(self, **kwargs):
        # Configuration example
        configuration = [
            {
                'key': 'ChargePointModel',
                'readonly': True,
                'value': 'Sample Model'
            },
            {
                'key': 'ChargePointVendor',
                'readonly': True,
                'value': 'Sample Vendor'
            },
            {
                'key': 'FirmwareVersion',
                'readonly': True,
                'value': '1.0.0'
            },
            {
                'key': 'Connectivity',
                'readonly': False,
                'value': 'WiFi'
            }
        ] 
        return call_result.GetConfiguration(
            configuration_key=configuration
        )

    @on('ChangeConfiguration', skip_schema_validation=SkipSchemVal)
    async def on_ChangeConfiguration(self, key, value, **kwargs):
        # For simplicity, just log the configuration change request
        print(f"ChangeConfiguration request received: key={key}, value={value}")

        # Simulate applying the configuration change
        if key in {'ChargePointModel', 'ChargePointVendor', 'FirmwareVersion'}:
            status = 'Rejected'
        else:
            status = 'Accepted'

        return call_result.ChangeConfiguration(
            status=status
        )

    @on('StatusNotification', skip_schema_validation=SkipSchemVal)
    async def on_StatusNotification(self, connector_id, error_code, status, **kwargs):
        print(f"StatusNotification received: connector_id={connector_id}, error_code={error_code}, status={status}")
        return call_result.StatusNotification()




async def on_connect(websocket, path):
    """For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        auth = websocket.request_headers["Authorization"]
        if not auth:
            raise ValueError('Missing Authorization header')
        if not 'Basic ' in auth:
            raise ValueError('Invalid Authorization header format')
        logging.info(f'Authorization {auth}')
        decoded_bytes = base64.b64decode(auth[6:])
        decoded_string = decoded_bytes.decode("utf-8")
        user, password = decoded_string.split(":")
        logging.info(f' Authorization {user} {password}')
        requested_protocols = websocket.request_headers["Sec-WebSocket-Protocol"]
    except KeyError as e:
        logging.error(f'{e}')
        return await websocket.close()
    except ValueError:
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

_ssl = False

async def main():
    ssl_context = None
    if _ssl:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    server = await websockets.serve(
        on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"],
        ssl=ssl_context
    )

    logging.info(f'Server Started listening to new connections (ssl={_ssl})')
    await server.wait_closed()


if __name__ == "__main__":
    # asyncio.run() is used when running this example with Python >= 3.7v
    asyncio.run(main())
