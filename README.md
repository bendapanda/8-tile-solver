# 8-tile-solver
This is an extension of a project I worked on in class. The previous
solver was only able to solve simple problems but I have extended it
to be able to solve any 8-tile arrangement in a reasonable time.

## Adjustments
- I have changed the BFS search implementation to make use of a priority queue
so that more likely options are investigated first.
- I have added some caching so that no state is investigated twice. 

## TODO:
- currently I need to clean up the structure a little. This was just a 
simple project so I haven't done much with it yet.
- I would like to investigate further optimisations as well.

