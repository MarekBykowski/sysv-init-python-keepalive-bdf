#!/usr/bin/env python3
import subprocess
import time
import sys
import argparse

INTERVAL = 5
TIMEOUT = 15

def pci_read(bdf):
    try:
        result = subprocess.run(
            ["setpci", "-s", bdf, "0x0.l"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT,
        )
        return result
    except subprocess.TimeoutExpired:
        return None

def main():
    parser = argparse.ArgumentParser(description="PCI keepalive")
    parser.add_argument("bdfs", nargs="+", help="PCI BDFs (e.g. 01:00.0)")
    parser.add_argument("--interval", type=int, default=INTERVAL)
    args = parser.parse_args()

    print(f"Starting PCI keepalive for: {args.bdfs}")

    while True:
        for bdf in args.bdfs:
            res = pci_read(bdf)

            if res is None:
                print(f"[TIMEOUT] {bdf}")
                continue

            if res.returncode == 0:
                output = res.stdout.decode().strip()
                # Only log if changed
                if last_values.get(bdf) != output:
                    print(f"[OK] {bdf}: {output}")
                    last_values[bdf] = output
            else:
                error = res.stderr.decode().strip()
                print(f"[FAIL] {bdf}: {error}")

        time.sleep(args.interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
