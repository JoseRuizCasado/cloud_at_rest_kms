def chunk_bytes(size, source):
    """
    Return list with chunks of the source data
    :param size: size of chunks
    :param source: bytes string to separate in chunks
    :return: list with bytes string separate in chunks
    """
    for i in range(0, len(source), size):
        chunk = source[i:i + size]
        if len(chunk) < size:
            padding = size - len(chunk)
            zero_padding = 0
            chunk += zero_padding.to_bytes(1, 'big') * (padding - 1)
            chunk += padding.to_bytes(1, 'big')

        yield chunk
