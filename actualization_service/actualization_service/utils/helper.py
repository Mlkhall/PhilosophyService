from typing import Generator


def use_chunks_generator(
    iterable: tuple[str, ...],
    chunk_size: int,
) -> Generator[tuple, None, None]:

    yield from (iterable[idx : idx + chunk_size] for idx in range(0, len(iterable), chunk_size))


def use_chunks(iterable: tuple[str, ...], chunk_size: int) -> tuple[tuple, ...]:
    return tuple(use_chunks_generator(iterable, chunk_size))
