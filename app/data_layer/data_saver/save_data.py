from pathlib import Path
from threading import Thread

import hydra
from omegaconf import DictConfig

from app.data_layer.data_saver.data_saver import DataSaver
from app.utils.common import init_from_cfg
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


@hydra.main(config_path="../../configs", config_name="data_saver", version_base=None)
def main(cfg: DictConfig) -> None:
    """
    This is the main function that starts the data saver threads. The data saver
    threads are responsible for retrieving the data from the respective sources
    and saving the data to the respective databases.
    """
    savers = []
    for data_saver_config in cfg.data_saver:
        data_saver_name, config = list(data_saver_config.items())[0]
        data_saver = init_from_cfg(config, DataSaver)

        # Create a thread for each saver
        saver_thread = Thread(target=data_saver.retrieve_and_save)
        logger.info(f"Starting the saver {data_saver_name}")

        # Start the saver thread to retrieve and save the data
        saver_thread.start()
        savers.append(saver)

    for saver in savers:
        saver_thread.join()


if __name__ == "__main__":
    main()
