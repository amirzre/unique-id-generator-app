import threading
import time

import pytest

from src import SnowflakeIDGenerator


class TestSnowflakeIDGenerator:
    generator = SnowflakeIDGenerator(datacenter_id=1, machine_id=1)
    
    def test_unique_ids(self):
        """Test that all IDs are unique."""    
        id1 = self.generator.generate_id()
        id2 = self.generator.generate_id()
        assert id1 != id2, "Generated IDs should be unique."

    def test_sequential_ids_within_same_millisecond(self):
        """Test IDs within the same millisecond should be unique."""
        ids = [self.generator.generate_id() for _ in range(SnowflakeIDGenerator.MAX_SEQUENCE + 1)]
        assert len(set(ids)) == len(ids), "IDs within the same millisecond should be unique."
    
    def test_sequence_reset_on_new_millisecond(self):
        """Test ID should increase across milliseconds."""
        self.generator.last_timestamp = self.generator._current_time_millis() - 1
        id1 = self.generator.generate_id()
        time.sleep(0.001)  # Sleep for 1 millisecond
        id2 = self.generator.generate_id()
        assert id2 > id1, "ID should increase across milliseconds"

    def test_clock_backward_handling(self):
        """Test clock backward handling."""
        self.generator.last_timestamp = self.generator._current_time_millis() + 1
        with pytest.raises(Exception, match="Clock moved backwards. Refusing to generate id"):
            self.generator.generate_id()
    
    def test_max_datacenter_id(self):
        """Test max datacenter ID."""
        with pytest.raises(ValueError, match="Datacenter ID must be between 0 and 31"):
            SnowflakeIDGenerator(
                datacenter_id=SnowflakeIDGenerator.MAX_DATACENTER_ID + 1, machine_id=1
            )
    
    def test_max_machine_id(self):
        """Test max machine id."""
        with pytest.raises(ValueError, match="Machine ID must be between 0 and 31"):
            SnowflakeIDGenerator(
                datacenter_id=1, machine_id=SnowflakeIDGenerator.MAX_MACHINE_ID + 1
            )

    def test_thread_safety(self):
        """Test generated IDs should be unique even in a multithreaded context."""
        ids = set()
        lock = threading.Lock()

        def generate_ids():
            for _ in range(1000):
                with lock:
                    ids.add(self.generator.generate_id())

        threads = [threading.Thread(target=generate_ids) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(ids) == 10000, "All generated IDs should be unique even in a multithreaded context."

    def test_datacenter_id_zero(self):
        """Test if datacenter ID is zero."""
        generator = SnowflakeIDGenerator(datacenter_id=0, machine_id=1)
        id1 = generator.generate_id()
        assert id1 > 0, "Generated ID should be positive even with datacenter_id = 0."
    
    def test_machine_id_zero(self):
        """Test if machin ID is zero."""
        generator = SnowflakeIDGenerator(datacenter_id=1, machine_id=0)
        id1 = generator.generate_id()
        assert id1 > 0, "Generated ID should be positive even with machine_id = 0."

    def test_edge_datacenter_and_machine_id(self):
        """Test edge datacenter and machine id."""
        generator = SnowflakeIDGenerator(SnowflakeIDGenerator.MAX_DATACENTER_ID, SnowflakeIDGenerator.MAX_MACHINE_ID)
        id1 = generator.generate_id()
        assert id1 > 0, "Generated ID should be positive with max datacenter_id and machine_id."

    def test_timestamp_with_custom_epoch(self):
        """Test timestamp with custom epoch."""
        custom_epoch = int(time.time() * 1000)
        SnowflakeIDGenerator.EPOCH = custom_epoch

        id1 = self.generator.generate_id()
        timestamp_part = (id1 >> SnowflakeIDGenerator.TIMESTAMP_SHIFT) + custom_epoch
        current_time = int(time.time() * 1000)
        assert abs(timestamp_part - current_time) < 10, "Timestamp should match the current time."

    def test_max_sequence(self):
        """Test max sequence."""
        self.generator.last_timestamp = self.generator._current_time_millis()
        self.generator.sequence = SnowflakeIDGenerator.MAX_SEQUENCE
        id1 = self.generator.generate_id()
        assert id1 > 0, "Generated ID should be positive at max sequence number."

    def test_no_collision_in_multithreaded_environment(self):
        """Test no collision in multithreaded environment."""
        def generate_ids(generator, num_ids, results):
            for _ in range(num_ids):
                results.append(generator.generate_id())

        num_threads = 10
        num_ids = 1000
        threads = []
        results = []

        for _ in range(num_threads):
            thread = threading.Thread(target=generate_ids, args=(self.generator, num_ids, results))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        unique_results = set(results)
        assert len(unique_results) == len(results), "There should be no duplicate IDs in a multithreaded environment." 
