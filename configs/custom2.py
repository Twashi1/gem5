from m5.objects import *

# ----------------------------
# L1 instruction cache
# ----------------------------
class L1ICache(Cache):
    size = '32kB'
    assoc = 4
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 20

# ----------------------------
# L1 data cache
# ----------------------------
class L1DCache(Cache):
    size = '32kB'
    assoc = 4
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 4
    tgts_per_mshr = 20

# ----------------------------
# L2 cache
# ----------------------------
class L2Cache(Cache):
    size = '256kB'
    assoc = 8
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 20
    tgts_per_mshr = 12

# ----------------------------
# 1. System and domains
# ----------------------------
system = System()

# Voltage domain (descending: high -> low)
voltage_domain = VoltageDomain(
    voltage=["1.0V", "0.9V", "0.8V"]
)

# Clock domain for CPU (matching voltages)
cpu_clk_domain = SrcClockDomain(
    clock=["3GHz", "2.5GHz", "2GHz"],
    voltage_domain=voltage_domain,
    domain_id=0
)
system.clk_domain = cpu_clk_domain

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# ----------------------------
# 2. CPU
# ----------------------------
system.cpu = DerivO3CPU()
system.cpu.clk_domain = cpu_clk_domain
system.cpu.createThreads()

# ----------------------------
# 3. Caches
# ----------------------------
system.membus = SystemXBar()

system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Connect CPU ports manually
system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side

# L1 → L2 bus
system.l2bus = L2XBar()
system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports

# L2 cache → memory
system.l2cache = L2Cache()
system.l2cache.cpu_side = system.l2bus.mem_side_ports
system.l2cache.mem_side = system.membus.cpu_side_ports

# ----------------------------
# 4. Memory bus & controller
# ----------------------------
system.mem_ctrl = DDR3_1600_8x8()
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# ----------------------------
# 5. Simple memory object
# ----------------------------
system.memobj = SimpleMemobj()
system.cpu.icache_port = system.memobj.inst_port
system.cpu.dcache_port = system.memobj.data_port
system.memobj.mem_side = system.membus.cpu_side_ports

# ----------------------------
# 6. Interrupts (x86)
# ----------------------------
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# ----------------------------
# 7. DVFS
# ----------------------------
system.dvfs_handler = DVFSHandler()
system.dvfs_handler.domains = [cpu_clk_domain]
system.dvfs_handler.enable = True

# ----------------------------
# 8. Workload
# ----------------------------
process = Process()
process.cmd = ['./gem5-file-to-run']
system.cpu.workload = process

# ----------------------------
# 9. Root & instantiate
# ----------------------------
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
