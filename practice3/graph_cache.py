from index import IndexStore


class StatData:
    def __init__(self, dl: int, tl: int, tf: int) -> None:
        self.dl = dl
        self.tl = tl
        self.tf = tf


class StatCache:
    def __init__(self, store: IndexStore) -> None:
        self.store = store

    def compute_stat(self) -> None:
        pass
