from typing import Generator, Tuple


def use_chunks_generator(
    iterable: Tuple[str, ...],
    chunk_size: int,
) -> Generator[tuple, None, None]:

    yield from (iterable[idx : idx + chunk_size] for idx in range(0, len(iterable), chunk_size))


def use_chunks(iterable: Tuple[str, ...], chunk_size: int) -> Tuple[Tuple, ...]:
    return tuple(use_chunks_generator(iterable, chunk_size))
