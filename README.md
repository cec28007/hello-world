# hello-world
My First repository

I really don't like talking about myself.

## swgoh_pull.py

Pull a SWGOH player's current state by ally code from the public swgoh.gg API
(no auth required):

```sh
python3 swgoh_pull.py 611-121-817            # print a summary
python3 swgoh_pull.py 611-121-817 --json roster.json   # also dump full JSON
```

Requires Python 3 and outbound network access to `swgoh.gg`.
