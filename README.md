## How to run


## Technical decisions

- aioredis doesn't support the WATCH command out of the box, but it's still possible to achieve similar transacion-like functionality by using multi/exec transactions.
