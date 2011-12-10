import pstats
p = pstats.Stats('/home/predmond/ants.py/log-Hedge.profile')
p.sort_stats('cumulative').print_stats(10)
p.sort_stats('time').print_stats(10)
