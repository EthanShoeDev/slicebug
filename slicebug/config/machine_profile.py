import json
import os.path
from dataclasses import dataclass

from slicebug.exceptions import UserError


@dataclass
class MachineProfile:
    serial: str
    profile_root: str

    @classmethod
    def from_json(cls, serialized, version, profiles_root):
        if version != 1:
            raise UserError(
                f"Wrong machine profile version {version}.",
                "Your profile might be corrupted. Try running `slicebug bootstrap` again.",
            )

        serial = serialized["serial"]
        profile_root = os.path.join(profiles_root, serial)

        return cls(
            serial=serial,
            profile_root=profile_root,
        )

    def to_json(self):
        return {"serial": self.serial}

    def material_settings_path(self):
        return os.path.join(self.profile_root, "material_settings.json")


@dataclass
class MachineProfiles:
    profiles: dict[str, MachineProfile]

    @classmethod
    def profiles_root(cls, config_root):
        return os.path.join(config_root, "profiles")

    @classmethod
    def load(cls, config_root):
        path = os.path.join(config_root, "profiles.json")
        if not os.path.exists(path):
            return None

        with open(path) as profiles_file:
            saved = json.load(profiles_file)

        if (version := saved.get("version")) != 1:
            raise UserError(
                f"Wrong profiles.json version {version}",
                "Your profile might be corrupted. Try running `slicebug bootstrap` again.",
            )

        return cls(
            profiles={
                profile_name: MachineProfile.from_json(
                    profile_json, version, cls.profiles_root(config_root)
                )
                for profile_name, profile_json in saved["profiles"].items()
            }
        )

    def save(self, config_root):
        path = os.path.join(config_root, "profiles.json")

        with open(path, "w") as profiles_file:
            json.dump(
                {
                    "version": 1,
                    "profiles": {
                        profile_name: profile.to_json()
                        for profile_name, profile in self.profiles.items()
                    },
                },
                profiles_file,
                indent=4,
            )
