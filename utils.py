import winreg
import os
import shlex

from pydantic import BaseModel, ValidationError


class Config(BaseModel):
    osu_path: str
    osu_exe: str
    replays_path: str
    delay: int = 100


def find_osu_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                             r"osustable.File.osk\Shell\Open\Command")
        command, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        exe_path = shlex.split(command)[0]

        osu_folder = os.path.dirname(exe_path)

        return osu_folder
    except FileNotFoundError:
        return None


def save_config(config: Config, filename="config.json") -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(config.model_dump_json(ensure_ascii=False, indent=4))


def load_config(filename="config.json") -> Config | None:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
            return Config.model_validate_json(content)

    except FileNotFoundError:
        return None
    except ValidationError:
        print(f"got corrupted config, re-creating")
        return None


def update_and_save_config(current_config: Config, **changes) -> Config:
    config_data = current_config.model_dump()

    config_data.update(changes)

    try:
        new_config = Config.model_validate(config_data)

        save_config(new_config)
        return new_config

    except ValidationError as e:
        print(f"error validating config: {e}")
        return current_config


def get_or_create_config() -> Config:
    existing_config = load_config()
    if existing_config:
        return existing_config

    osu_path = find_osu_path()

    if not osu_path:
        raise FileNotFoundError("cannot find osu and get config")

    new_config = Config(
        osu_path=osu_path,
        osu_exe=os.path.join(osu_path, "osu!.exe"),
        replays_path=os.path.join(osu_path, "Replays")
    )

    save_config(new_config)
    return new_config
