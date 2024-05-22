# import time
import threading
import queue

from tqdm import tqdm

from etl.models.extract.ApiToParquetFile import extraction
from etl.models.transform.ResponseSplit import transformation
from etl.models.load.ToParquet import loadToParquet

ControllerQueue = queue.Queue()


class ExecutePipeline:
    """
    Class representing a pipeline execution.

    Args:
        *xargs: Variable number of string arguments representing the parameters for the pipeline execution.

    Attributes:
        params (list): List of parameters passed to the pipeline execution.
        params_count (int): Number of parameters passed to the pipeline execution.
        extractedFiles (list): List of extracted files from the pipeline execution.

    Raises:
        TypeError: If all type of parameters passed to the pipeline execution are invalid.

    Methods:
        pipelineExecute: Executes the pipeline.
        GetExtractedFiles: Returns the list of extracted files.

    """

    def __init__(self, *xargs) -> None:
        self.params = list(xargs)
        self.params_count = len(self.params)

        totalInvalidParams = 0
        for arg in self.params:
            if not isinstance(arg, str):
                totalInvalidParams += 1

        if totalInvalidParams == self.params_count:
            raise TypeError(f"Invalid parameters >>>> {self.params}")

        self._pipeline_execute(InputParams=self.params)

    def _pipeline_execute(self, InputParams: list):
        """
        Executes the pipeline.

        Raises:
            KeyError: If the informed parameters are not available for extraction.
        """
        try:
            extractor = extraction(InputParams)

            # Define a função que será executada pelo thread do produtor
            def produce():
                transformer = transformation(
                    extractor.json_data, extractor.ValidParams, ControllerQueue
                )
                transformer.publish()
                ControllerQueue.put(None)  # Sinaliza que a produção está completa

            # Define a função que será executada pelo thread do consumidor
            def consume():
                with tqdm(
                    desc="Consuming Data", unit=" item", total=len(InputParams)
                ) as pbar:
                    while True:
                        # time.sleep(0.5)
                        item = ControllerQueue.get()
                        if item is None:
                            ControllerQueue.task_done()
                            break
                        loader = loadToParquet(item)
                        loader.load()
                        ControllerQueue.task_done()
                        pbar.update()

            # Criação dos threads
            thread_producer = threading.Thread(target=produce)
            thread_consumer = threading.Thread(target=consume)

            # Inicia os threads
            thread_producer.start()

            thread_consumer.start()

            thread_producer.join()
            thread_consumer.join()
            ControllerQueue.join()

        except Exception as e:
            # Tratamento genérico para outras exceções
            print(f"Erro durante a execução do pipeline: {e}")
            raise e
