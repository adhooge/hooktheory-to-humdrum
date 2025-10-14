import json
import pathlib

from tqdm import tqdm

from src.converter import convert

print("Processing of full Hooktheory dataset starting...")

with open("data/Hooktheory.json", "r") as f:
    data = json.load(f)

print(f"json file was loaded! There are {len(data)} entries.")

OUTPATH = pathlib.Path("data/kern/")
OUTPATH.mkdir(exist_ok=True)

print(
    f"{len(list(OUTPATH.glob('*.krn')))} files were already processed, they will be skipped automatically."
)

SKIP = ["pJkmZNKkmqn", "RZwxKnNjged", "-kwxANXDoKG"]

for k, v in (pbar := tqdm(data.items())):
    pbar.set_description(f"Processing id: {k}")
    if k in SKIP:
        continue
    filename = f"{k}.krn"
    if (OUTPATH / filename).exists():
        continue
    s = convert(v)

    with open(OUTPATH / filename, "w") as f:
        f.write(s)
