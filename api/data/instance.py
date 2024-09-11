from api.data.data_handler import DataHandler


def get_data_handler() -> DataHandler:
    """
    Returns a singleton instance of the DataHandler.

    :return DataHandler: The singleton instance of DataHandler
    """
    global db_handler
    if "db_handler" not in globals():
        db_handler = DataHandler()
    return db_handler
