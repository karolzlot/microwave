from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from microwave import Microwave


@pytest.mark.asyncio
async def test_get_power():
    with patch("redis_connection.redis", new_callable=AsyncMock) as mock_redis:
        mock_redis.get.return_value = "50"
        microwave = Microwave()
        power = await microwave.get_power()
        assert power == 50
        mock_redis.get.assert_awaited_once_with("microwave_power")


@pytest.mark.asyncio
async def test_get_counter():
    with patch("redis_connection.redis", new_callable=AsyncMock) as mock_redis:
        mock_redis.get.return_value = "30"
        microwave = Microwave()
        counter = await microwave.get_counter()
        assert counter == 30
        mock_redis.get.assert_awaited_once_with("microwave_counter")


@pytest.mark.asyncio
async def test_get_state_on():
    with patch(
        "microwave.Microwave.get_microwave_data", new_callable=AsyncMock
    ) as mock_get_microwave:
        mock_get_microwave.return_value = {"power": 50, "counter": 30, "state": "ON"}
        microwave = Microwave()
        state = await microwave.get_state()
        assert state == "ON"


@pytest.mark.asyncio
async def test_get_state_off():
    with patch(
        "microwave.Microwave.get_microwave_data", new_callable=AsyncMock
    ) as mock_get_microwave:
        mock_get_microwave.return_value = {"power": 0, "counter": 0, "state": "OFF"}
        microwave = Microwave()
        state = await microwave.get_state()
        assert state == "OFF"


# TODO: add more tests, also with real Redis
