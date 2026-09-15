# betterfinder

Free CT-log/passive sources do one bulk query per domain. On big domains
that query silently drops rows — no error, just missing hosts. betterfinder
tells you which subdomain "levels" are worth a second, narrower look, so
you catch what the first pass missed.

## example (real, public domain, reproducible)

```
$ curl -s "https://crt.sh/?q=%25.wikimedia.org&output=json" | jq -r '.[].name_value' | sort -u > subs.txt
$ wc -l subs.txt
148 subs.txt

$ python3 betterfinder.py -d wikimedia.org -i subs.txt
codfw.wikimedia.org
corp.wikimedia.org
eqiad.wikimedia.org
frdev.wikimedia.org

$ # rescan those 4 levels against crt.sh, merge back in
$ wc -l subs.txt
155 subs.txt
```

+7 hosts the first bulk query missed entirely, e.g. `superset.frdev.wikimedia.org`,
`ldap-rw-next.codfw.wikimedia.org`, `payments-listener.frdev.wikimedia.org`.

## use

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u > subs.txt
python3 betterfinder.py -d example.com -i subs.txt > rescan.txt
xargs -I{} curl -s "https://crt.sh/?q=%25.{}&output=json" < rescan.txt | jq -r '.[].name_value' >> subs.txt
sort -u subs.txt -o subs.txt
```

Works with any discovery tool, not just crt.sh — `rescan.txt` is a plain
domain list, feed it to subfinder/amass/whatever you already use.

betterfinder itself makes zero network calls — it just reads a subdomain
list and prints which parent labels have enough children (`--fanout`,
default 2) to be worth a second query. `--seen file.txt` tracks labels
already probed so repeat runs don't re-emit them.

No dependencies.

## license

MIT
