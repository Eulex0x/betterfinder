# betterfinder

Free recon sources — crt.sh, HackerTarget, OTX, whatever — each do *one
bulk lookup per apex domain*. On a big/high-volume domain that single
query can silently come back incomplete: no error, no pagination hint,
just fewer rows than actually exist. Confirmed this on crt.sh with a real
target: the naive bulk query returned 217 hosts, the real number was
310+, including whole subdomain clusters (an acquired brand, internal
tooling) that never showed up at all. No reason to think other free
sources behave better at scale — they're free, rate-limited, and none of
them tell you when they're truncating you.

Fix: once a label shows up more than once in what you've already found
(`staging.domain.com`, `data.domain.com`...), rerun your discovery tools
against *that label alone*. Narrower queries dodge the same truncation
and often surface whole clusters the bulk query hid.

betterfinder does exactly that one step and nothing else — **it doesn't
query anything**. Feed it a subdomain list, it hands back which narrower
domains are worth a fresh discovery pass. You pipe that into whatever you
already use (subfinder, crt.sh, amass...), merge what comes back, and run
betterfinder again on the bigger list if you want another round.

## use

```bash
# get a subdomain list however you normally do
subfinder -d example.com -silent -o subs.txt

# ask what's worth rescanning
python3 betterfinder.py -d example.com -i subs.txt > rescan.txt

# rescan those, merge back in, repeat
while read -r lvl; do subfinder -d "$lvl" -silent; done < rescan.txt >> subs.txt
sort -u subs.txt -o subs.txt
```

`--seen levels.txt` keeps a running record so you don't rescan the same
label twice across rounds — pass the same file each time and it self-excludes.

`--fanout` (default 2) is the min number of known children a label needs
before it counts. Lower it (e.g. `--fanout 1`) on a small target where
there's little request volume to worry about cutting.

No dependencies, no network calls.

## license

MIT
