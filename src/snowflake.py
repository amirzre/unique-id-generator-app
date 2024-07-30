import threading
import time


class SnowflakeIDGenerator:
    EPOCH = 1288834974657
    SIGN_BITS = 1
    TIMESTAMP_BITS = 41
    DATACENTER_BITS = 5
    MACHINE_BITS = 5
    SEQUENCE_BITS = 12

    MAX_DATACENTER_ID = (1 << DATACENTER_BITS) - 1
    MAX_MACHINE_ID = (1 << MACHINE_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

    TIMESTAMP_SHIFT = SEQUENCE_BITS + MACHINE_BITS + DATACENTER_BITS
    DATACENTER_SHIFT = SEQUENCE_BITS + MACHINE_BITS
    MACHINE_SHIFT = SEQUENCE_BITS

    def __init__(self, datacenter_id: int, machine_id: int):
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(
                f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}"
            )
        if machine_id > self.MAX_MACHINE_ID or machine_id < 0:
            raise ValueError(f"Machine ID must be between 0 and {self.MAX_MACHINE_ID}")

        self.datacenter_id = datacenter_id
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

        self.lock = threading.Lock()

    def _current_time_millis(self) -> int:
        return int(time.time() * 1000)

    def _wait_for_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._current_time_millis()
        while timestamp <= last_timestamp:
            timestamp = self._current_time_millis()
        return timestamp

    def generate_id(self) -> int:
        with self.lock:
            timestamp = self._current_time_millis()

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards. Refusing to generate id!")

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            id_bits = (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT)
                | (self.datacenter_id << self.DATACENTER_SHIFT)
                | (self.machine_id << self.MACHINE_SHIFT)
                | self.sequence
            )

            return id_bits
