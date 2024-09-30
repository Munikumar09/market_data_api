from copy import deepcopy
from typing import Any, cast

from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf
from registrable import Registrable
from registrable.exceptions import RegistrationError


def pop_name(cfg: DictConfig) -> DictConfig:
    """
    Remove the 'name' key from the configuration object and return a copy.

    Parameters:
    ----------
    cfg: ``DictConfig``
        The configuration object

    Returns:
    -------
    ``DictConfig``
        A copy of the configuration object with the 'name' key removed
    """
    cfg_copy = deepcopy(cfg)
    OmegaConf.set_struct(cfg_copy, False)
    cfg_copy.pop("name", None)
    OmegaConf.set_struct(cfg_copy, True)

    return cfg_copy


def init_from_cfg(
    cfg: DictConfig,
    base_class: type[Registrable] | None = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Initialize a class instance from a configuration object.

    Parameters
    ----------
    cfg: ``DictConfig``
        The configuration object
    base_class: ``Optional[Type]
        The base class from which the instance should be initialized
    args: Any
        The arguments to pass to the class constructor
    kwargs: Any
        The keyword arguments to pass to the class constructor

    Returns
    -------
    Any
        The instance of the class initialized

    Raises
    ------
    ValueError
        If both name and base_class are None, or if base_class is None after processing
    RegistrationError
        If the name is not registered under the given base_class
    """
    if "_target_" in cfg:
        config_dict = cast(dict[str, Any], OmegaConf.to_container(cfg, resolve=True))
        target = config_dict.pop("_target_")

        return instantiate(
            {"_target_": target}, *list(config_dict.values()), *args, **kwargs
        )

    name = cfg.get("name")

    if name is None and base_class is None:
        raise ValueError("Both name and base_class cannot be None")

    if name:
        try:
            base_class = (
                base_class.by_name(name) if base_class else Registrable.by_name(name)
            )
        except RegistrationError:
            raise RegistrationError(
                f"`{name}` is not a registered name. "
                "Please provide a proper base_class under which the class is registered."
            )

    if base_class is None:
        raise ValueError("base_class cannot be None")

    if hasattr(base_class, "from_cfg") and callable(base_class.from_cfg):
        return base_class.from_cfg(cfg, *args, **kwargs)

    config_dict = cast(
        dict[str, Any], OmegaConf.to_container(pop_name(cfg), resolve=True)
    )

    return base_class(*list(config_dict.values()), *args, **kwargs)
