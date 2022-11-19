from pathlib import Path
from typing import Set

from nonebot import get_driver
from pydantic import BaseModel, Extra


class PluginConfig(BaseModel, extra=Extra.ignore):
    todayEat_path: Path = Path(__file__).parent / "resource"
    use_preset_menu: bool = False
    use_preset_greetings: bool = False
    eating_limit: int = 5
    greeting_groups_id: Set[str] = set()
    superusers: Set[str] = set()


driver = get_driver()
todayEat_config: PluginConfig = PluginConfig.parse_obj(driver.config.dict())
