import csv
import git
import copy
import os , sys
from pathlib import Path
repo = git.Repo('.', search_parent_directories=True)
repo_root = repo.working_tree_dir
sys.path.insert(0, os.path.join(repo_root, "framework") )
# from itertools import batched
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from datetime  import datetime


# ---------------------------

# ---------------------------
def read_window(cache_dir):
    manifestfile = os.path.join(cache_dir, "manifest.csv")
    manifest = pd.read_csv(manifestfile)

    for window in manifest.itertuples(index=False):
        datapath = window.path
        df       = pd.read_parquet(datapath)
        # X        = df.drop(columns=["click"])
        # y        = df["click"]
        # yield (X,y, window.winstart, window.winend)
        yield (df, window.winstart, window.winend)


# ---------------------------
# Cache a window
# ---------------------------
def save_window(cache_dir, window_hours, X, y):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    df = X.copy()
    df["click"] = y.numpy() if hasattr(y, "numpy") else y

    winstart = window_hours[0]
    out_path = os.path.join( cache_dir,  f"winstart_{winstart:04d}.parquet")
    df.to_parquet(out_path, index=False)
    return {
        "winstart": winstart,
        "winend": window_hours[-1],
        "num_examples": len(df),
        "path": str(out_path),
    }    

# ---------------------------
# Basic Torch Dataset wrapper
# ---------------------------
class AvazuWindowDataset(Dataset):
    def __init__(self, df, window_hours):
        self.df           = df.reset_index(drop=True)
        self.window_hours = window_hours

        # target
        self.y = torch.tensor(df["click"].values, dtype=torch.float32)

        # drop unused
        self.X = df.drop(columns=["click", "id"], errors="ignore")

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.X.iloc[idx]
        # convert to dict for flexibility (hash later)
        return row.to_dict(), self.y[idx]


# -----------------------------------
# Main Generator (streaming + slicing)
# -----------------------------------
class DataSetGenerator:
    def __init__(
        self,
        csv_path,
        winsize_hours,
        winstride_hours,
        start_time_hour=0,
        chunksize=1_000_000,
        batch_size=1024,
        num_workers=0,
    ):
        self.csv_path = csv_path
        self.winsize = winsize_hours
        self.stride = winstride_hours
        self.start_hour = start_time_hour
        self.chunksize = chunksize
        self.batch_size = batch_size
        self.num_workers = num_workers

    def _hour_to_int(self, hour_val):
        """
        Convert YYMMDDHH -> monotonic integer hour index.
        Example: 14102100 -> hours since 2014-10-21 00:00
        """
        dt = datetime.strptime(str(int(hour_val)), "%y%m%d%H")
        if not hasattr(self, "_t0"):
            self._t0 = dt
        delta = dt - self._t0
        return int(delta.total_seconds() // 3600)

    def __iter__(self):
        # pass 1: collect all rows grouped by hour
        hour_buckets = {}

        reader = pd.read_csv(self.csv_path, chunksize=self.chunksize)
        for idx, chunk in enumerate(reader):
            print(f"Processing chunk={idx}")
            # convert hour → integer index
            chunk["hour_idx"] = chunk["hour"].apply(self._hour_to_int)
            for h, group in chunk.groupby("hour_idx"):
                if h not in hour_buckets:
                    hour_buckets[h] = []
                hour_buckets[h].append(group)

        # merge lists
        for h in hour_buckets:
            hour_buckets[h] = pd.concat(hour_buckets[h], ignore_index=True)

        # sorted hours
        all_hours = sorted(hour_buckets.keys())
        print(f"all_hours = {all_hours}")

        # ---------------------------------------
        # sliding window loop
        # ---------------------------------------
        start_ptr = 0
        while start_ptr < len(all_hours):
            window_hours = all_hours[start_ptr : start_ptr + self.winsize]

            if len(window_hours) < self.winsize:
                break

            # concatenate data for this window
            df_window = pd.concat(
                [hour_buckets[h] for h in window_hours],
                ignore_index=True
            )

            dataset = AvazuWindowDataset(df_window, window_hours)

            loader = DataLoader(
                dataset,
                batch_size=self.batch_size,
                shuffle=False,  # preserve time ordering if needed
                num_workers=self.num_workers,
                pin_memory=True,
            )

            yield loader

            start_ptr += self.stride



# =====================================================
if __name__ == "__main__":
    winsize_hours=10
    winstride_hours=5

    # Data directory
    datadir  = os.path.join(repo_root, "studies", "STUDY_avazu_CTR")
    cachedir = os.path.join(datadir, f"winsize_{winsize_hours}h_stride_{winstride_hours}h")
    datafile = os.path.join(datadir, "train")
    manifestfile = os.path.join(cachedir ,  "manifest.csv" )

    # Load data
    print(f"Loading datafile {datafile} ...")
    gen = DataSetGenerator(
        datafile,
        winsize_hours  = winsize_hours,
        winstride_hours= winstride_hours
    )

    # Save
    records = []
    for i, loader in enumerate(gen):
        ds = loader.dataset
        print(f"Window {i} covering time {ds.window_hours} {len(ds)}")

        rec = save_window(
            cache_dir       =   cachedir,
            window_hours    =   ds.window_hours,
            X               =   ds.X,
            y               =   ds.y,
        )
        records.append(rec)

    manifest = pd.DataFrame(records)
    print(manifest)
    manifest.to_csv( manifestfile , index=False)



