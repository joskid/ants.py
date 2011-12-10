import pstats
p = pstats.Stats('/home/predmond/ants.py/log-Hedge.profile')
p.strip_dirs().sort_stats('time').print_stats(20)
p.strip_dirs().sort_stats('cumulative').print_stats(10)
