from multiprocessing import Process, Pipe, Queue

class ProcessBase:
    def __init__(self) -> None:
        recv_queue = Queue()
        put_queue = Queue()
        self.process = Process(target=self.run, args=(put_queue, recv_queue))
        self.recv_queue = recv_queue
        self.put_queue = put_queue

    def start(self):
        self.process.start()

    def finish(self):
        self.process.terminate()

    def run(self, put_queue, recv_queue):
        pass

    