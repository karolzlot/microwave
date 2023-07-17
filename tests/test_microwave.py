from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from microwave import Microwave


@patch("main.redis", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_get_power(mock_redis):
    with patch("microwave.redis", new_callable=AsyncMock) as mock_redis:
        mock_redis.get.return_value = "50"
        microwave = Microwave()
        power = await microwave.get_power()
        assert power == 50
        mock_redis.get.assert_awaited_once_with("microwave_power")


@patch("main.redis", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_get_counter(mock_redis):
    with patch("microwave.redis", new_callable=AsyncMock) as mock_redis:
        mock_redis.get.return_value = "30"
        microwave = Microwave()
        counter = await microwave.get_counter()
        assert counter == 30
        mock_redis.get.assert_awaited_once_with("microwave_counter")


@patch("main.redis", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_get_state_on(mock_redis):
    with patch(
        "microwave.Microwave.get_microwave", new_callable=AsyncMock
    ) as mock_get_microwave:
        mock_get_microwave.return_value = {"power": 50, "counter": 30, "state": "ON"}
        microwave = Microwave()
        state = await microwave.get_state()
        assert state == "ON"


@patch("main.redis", new_callable=MagicMock)
@pytest.mark.asyncio
async def test_get_state_off(mock_redis):
    with patch(
        "microwave.Microwave.get_microwave", new_callable=AsyncMock
    ) as mock_get_microwave:
        mock_get_microwave.return_value = {"power": 0, "counter": 0, "state": "OFF"}
        microwave = Microwave()
        state = await microwave.get_state()
        assert state == "OFF"


# TODO: add more tests, also with real Redis
