./graft '
dd=0
^
T(11,F)
d=30*f
d+=dd
T(10,S)
dd+=1
' --max-forks=10000 --frames=40 --lookahead-steps=40 "$@"
