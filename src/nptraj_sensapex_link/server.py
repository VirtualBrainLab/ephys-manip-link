import asyncio

from aiohttp import web
# noinspection PyPackageRequirements
import socketio
import sensapex_handler as sh
from typing import Any

# Setup server
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
is_connected = False


# Handle connection events
@sio.event
async def connect(sid, _, __):
    """
    Acknowledge connection to the server
    :param sid: Socket session ID
    :param _: WSGI formatted dictionary with request info (unused)
    :param __: Authentication details (unused)
    """
    print(f'[CONNECTION]:\t\t {sid}\n')

    global is_connected
    if not is_connected:
        is_connected = True
    else:
        return False


@sio.event
async def disconnect(sid):
    """
    Acknowledge disconnection from the server
    :param sid: Socket session ID
    """
    print(f'[DISCONNECTION]:\t {sid}\n')

    sh.reset()
    global is_connected
    is_connected = False


# Events
@sio.event
async def register_manipulator(_, manipulator_id: int) -> (int, str):
    """
    Register a manipulator with the server
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of the manipulator to register
    :return: Callback parameters (manipulator_id, error message (on error))
    """
    print(f'[EVENT]\t\t Register manipulator: {manipulator_id}')

    return sh.register_manipulator(manipulator_id)


@sio.event
async def get_pos(_, manipulator_id: int) -> (int, tuple[float], str):
    """
    Position of manipulator request
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to pull position from
    :return: Callback parameters (Manipulator ID, position in [x, y, z,
    w] (or an empty array on error), error message)
    """
    print(f'[EVENT]\t\t Get position of manipulator'
          f' {manipulator_id}')

    return sh.get_pos(manipulator_id)


@sio.event
async def goto_pos(_, data: sh.GotoPositionData) -> (int, tuple[float], str):
    """
    Move manipulator to position
    :param _: Socket session ID (unused)
    :param data: Data containing manipulator ID, position, and speed
    :return: Callback parameters (Manipulator ID, position in (x, y, z,
    w) (or an empty tuple on error), error message)
    """
    manipulator_id = data['manipulator_id']
    pos = data['pos']
    speed = data['speed']
    print(
        f'[EVENT]\t\t Move manipulator {manipulator_id} '
        f'to position {pos}'
    )

    return await sh.goto_pos(manipulator_id, pos, speed)


@sio.event
async def calibrate(_, manipulator_id: int) -> (int, str):
    """
    Calibrate manipulator
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to calibrate
    :return: Callback parameters (Manipulator ID, error message)
    """
    print(f'[EVENT]\t\t Calibrate manipulator'
          f' {manipulator_id}')

    return await sh.calibrate(manipulator_id, sio)


@sio.event
async def bypass_calibration(_, manipulator_id: int) -> (int, str):
    """
    Bypass calibration of manipulator
    :param _: Socket session ID (unused)
    :param manipulator_id: ID of manipulator to bypass calibration
    :return: Callback parameters (Manipulator ID, error message)
    """
    print(f'[EVENT]\t\t Bypass calibration of manipulator'
          f' {manipulator_id}')

    return sh.bypass_calibration(manipulator_id)


@sio.on('*')
async def catch_all(_, data: Any) -> None:
    """
    Catch all event
    :param _: Socket session ID (unused)
    :param data: Data received from client
    :return: None
    """
    print(f'[UNKNOWN EVENT]:\t {data}')


def launch() -> None:
    """Launch the server"""
    web.run_app(app)


if __name__ == '__main__':
    launch()
