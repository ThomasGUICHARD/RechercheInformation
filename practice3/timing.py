# Cool log manager wrote in few minutes, useless, but easier to read compared to print()

import time


class TimingWriting:
    def __init__(self) -> None:
        self.latest_print = ""
        self.start_time = 0
        self.end_time = 0

    def start(self) -> None:
        """
        Start of the record
        """
        self.start_time = time.process_time()

    def end(self) -> None:
        """
        End of the record
        """
        self.end_thread = True
        self.end_time = time.process_time()
        print()

    def get_time(self) -> float:
        """
        Get elapsed time (second)
        """
        return self.end_time - self.start_time

    def write(self, text: str) -> None:
        s = self.get_text(text)
        print(s)
        self.latest_print = s

    def write_no_endl(self, text: str) -> None:
        """

        """
        self.remove_text()

        s = self.get_text(text)
        print(s, end="", flush=True)
        self.latest_print = s

    def get_text(self, text: str):
        return "[{0:.3f}s] {1}".format(time.process_time() - self.start_time, text)

    def rewrite_text(self) -> None:
        self.write_no_endl(self.latest_print)

    def remove_text(self) -> None:
        print("\b" * len(self.latest_print) + " " *
              len(self.latest_print) + "\b" * len(self.latest_print), end="", flush=True)


logger = TimingWriting()
