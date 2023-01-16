from source.source import StoreCode


def code_string(code, *args):
    if code == StoreCode.DOWNLOADED:
        source = args[0]
        return f"The source '{source}' has been downloaded"
    if code == StoreCode.ALREADY_DOWNLOADED:
        source = args[0]
        return f"The source '{source}' was already downloaded. Read the 'help' to understand how to repeat the process."
    if code == StoreCode.PERSISTED:
        source = args[0]
        return f"The source '{source}' has been persisted"
    if code == StoreCode.ALREADY_PERSISTED:
        source = args[0]
        return f"The source '{source}' was already persisted. Read the 'help' to understand how to repeat the process."
