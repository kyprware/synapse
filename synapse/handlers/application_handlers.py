from ..utils.dispatch_utils import DispatchManager


dispatcher = DispatchManager()

@dispatcher.register("add")
async def add(a: int, b: int) -> int:
    return a + b
