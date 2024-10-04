class TaskNotReadyException(Exception):
    pass


class InsufficientMemoryException(Exception):
    pass


class MachineInUseException(Exception):
    pass

class TookMuchLess(Exception):
    pass