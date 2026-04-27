from m5.objects import *

# System
system = System()
system.clk_domain = SrcClockDomain(clock='1GHz', voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

system.dvfs = DVFSHandler()

# CPU
system.cpu = O3CPU()
cpu_clk = SrcClockDomain(clock='2GHz', voltage_domain=system.clk_domain.voltage_domain)
system.cpu.clk_domain = cpu_clk

# Memory bus
system.membus = SystemXBar()

# Connect CPU to bus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# Wrap DRAM in a MemCtrl
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# System port
system.system_port = system.membus.cpu_side_ports

# Workload
process = Process()
process.executable = '/home/thomas/Documents/gem5/gem5-file-to-run'
process.cmd = [process.executable]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system=False, system=system)
m5.instantiate()
print("Starting simulation")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
