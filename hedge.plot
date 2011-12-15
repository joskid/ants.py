set title "Ants Strategies over time"
set xlabel "Game Turn"
set ylabel "Hedge Faith"
set key top right
set terminal png
set output "hedge.png"
plot "log-Hedge.log" using :1 with lines title "betterexplore", \
     "log-Hedge.log" using :2 with lines title "brownian", \
     "log-Hedge.log" using :3 with lines title "clump", \
     "log-Hedge.log" using :4 with lines title "defend", \
     "log-Hedge.log" using :5 with lines title "explore", \
     "log-Hedge.log" using :6 with lines title "foodcalling", \
     "log-Hedge.log" using :7 with lines title "glomfood", \
     "log-Hedge.log" using :8 with lines title "glomhill", \
     "log-Hedge.log" using :9 with lines title "keepdistance", \
     "log-Hedge.log" using :10 with lines title "mob", \
     "log-Hedge.log" using :11 with lines title "movein", \
     "log-Hedge.log" using :12 with lines title "stayoffhill", \
     "log-Hedge.log" using :13 with lines title "unstuck"

set title "log(Ants Strategies) over time"
set xlabel "Game Turn"
set ylabel "log(Hedge Faith)"
set log y
set key left bottom
set terminal png
set output "hedge-log.png"
plot "log-Hedge.log" using :1 with lines title "betterexplore", \
     "log-Hedge.log" using :2 with lines title "brownian", \
     "log-Hedge.log" using :3 with lines title "clump", \
     "log-Hedge.log" using :4 with lines title "defend", \
     "log-Hedge.log" using :5 with lines title "explore", \
     "log-Hedge.log" using :6 with lines title "foodcalling", \
     "log-Hedge.log" using :7 with lines title "glomfood", \
     "log-Hedge.log" using :8 with lines title "glomhill", \
     "log-Hedge.log" using :9 with lines title "keepdistance", \
     "log-Hedge.log" using :10 with lines title "mob", \
     "log-Hedge.log" using :11 with lines title "movein", \
     "log-Hedge.log" using :12 with lines title "stayoffhill", \
     "log-Hedge.log" using :13 with lines title "unstuck"
