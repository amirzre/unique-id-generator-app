import os

from snowflake import SnowflakeIDGenerator

if __name__ == "__main__":
    datacenter_id = os.environ.get("DATACENTER_ID", default=1)
    machine_id = os.environ.get("MACHINE_ID", default=1)
    generator = SnowflakeIDGenerator(
        datacenter_id=int(datacenter_id), machine_id=int(machine_id)
    )
    unique_id = generator.generate_id()
    print(f"Generated unique ID: {unique_id}")
