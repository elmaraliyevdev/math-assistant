"""PCG64 permuted congruential generator (64-bit output)."""


class PCG64:
    """Permuted congruential generator per O'Neill PCG family."""

    _MULTIPLIER = 6364136223846793005

    def __init__(self, init_state: int, init_seq: int) -> None:
        if init_seq == 0:
            init_seq = 1
        self._inc = (init_seq << 1) | 1
        self._state = 0
        self.next_uint64()
        self._state = (self._state + init_state) & 0xFFFFFFFFFFFFFFFF
        self.next_uint64()

    def next_uint64(self) -> int:
        old_state = self._state
        self._state = (old_state * self._MULTIPLIER + self._inc) & 0xFFFFFFFFFFFFFFFF
        xorshifted = ((old_state >> 18) ^ old_state) >> 27
        rot = old_state >> 59
        mask = 0xFFFFFFFFFFFFFFFF
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & mask
