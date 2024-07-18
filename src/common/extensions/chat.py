from __future__ import annotations

from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List, Optional

CallbackType = Callable[..., Awaitable[Any]]




class Chat:
    def __init__(self) -> None:
        self.users: Dict[str, List[CallbackType]] = defaultdict(list)
    
    def get_callback(self, identifier: str) -> Optional[CallbackType]:
        stack: List[CallbackType] = self.users.get(identifier, [])
        if len(stack) <= 1:
            return None

        stack.pop() 
        return stack[-1]
    def set_callback(
        self, identifier: str, callback: CallbackType, is_start_callback: bool = False
    ) -> None:
        if is_start_callback:
            self.users[identifier].clear()

        self.users[identifier].append(callback)

