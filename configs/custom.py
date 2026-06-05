"""

Usage:
------

scons build/ALL/gem5.opt
./build/ALL/gem5.opt \
    configs/custom.py

# Will run resource gem5-file-to-run

# Note: This config script will only run on an X86 host.
# Each run takes ~2 hours

"""

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory.single_channel import SingleChannelDDR4_2400
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.isas import ISA
from gem5.resources.resource import obtain_resource
from gem5.simulate.simulator import Simulator
from gem5.resources.resource import BinaryResource
from m5.stats import periodicStatDump, dump, reset
from m5.objects import VoltageDomain, SrcClockDomain, DVFSHandler
import m5
from gem5.simulate.exit_event import ExitEvent

def marker(val):
    print("marker value:", val)
    yield False

# TODO: in order to be more in line with the original paper, set L2 size to a MB, ensure these values are being read as kilobytes, not kilibits; seems like its converting to KiB

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="64kB",
    l1i_size="64kB",
    l2_size="512kB",
)

memory = SingleChannelDDR4_2400("4GB")

# using 9 cores because when using openmp in SE mode, the number of cores
# should be # cores + 1
processor = SimpleProcessor(cpu_type=CPUTypes.O3, num_cores=1, isa=ISA.X86)

voltages_all = ["1.0V", "0.9V", "0.8V", "0.7V", "0.6V", "0.5V"]
frequencies_all = ["2.5GHz", "2.25GHz", "2.0GHz", "1.75GHz", "1.5GHz", "1.25GHz"]

voltages_baseline = ["1.0V"]
frequencies_baseline = ["2.5GHz"]

selected_voltages = voltages_all 
selected_frequencies = frequencies_all 

# selected_voltages = voltages_baseline 
# selected_frequencies = frequencies_baseline 

# Voltage domain (for all perf levels)
voltage_domain = VoltageDomain(voltage=selected_voltages)
clock_domain = SrcClockDomain(clock=selected_frequencies, voltage_domain=voltage_domain, domain_id=0)

# Attach the frequency domain to the CPU
processor.cores[0].core.clk_domain = clock_domain

board = SimpleBoard(
    clk_freq="2.5GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_se_binary_workload(
    binary=BinaryResource(local_path="./testprogram/marker")
)

board.dvfs_handler = DVFSHandler(domains=[clock_domain], enable=True, transition_latency="50ns")

simulator = Simulator(
    board=board,
)

simulator.run()

print(f"Interval ended at tick {m5.curTick()}")

event = simulator.get_last_exit_event_cause()
    
