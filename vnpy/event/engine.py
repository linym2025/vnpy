"""
Event-driven framework of VeighNa framework.
"""

    from collections import defaultdict
    from queue import Empty, Queue
    from threading import Thread
    from time import sleep
    from typing import Any, Callable, List

    EVENT_TIMER = "eTimer"


    class Event:
        """
        Event object consists of a type string which is used
        by event engine for distributing event, and a data
        object which contains the real data.
        """

        def __init__(self, type: str, data: Any = None) -> None:
            """
            初始化事件对象。

            :param type: 事件的类型。
            :param data: 事件的数据，默认为None。
            """
            # 设置事件的类型
            self.type: str = type
            # 设置事件的数据
            self.data: Any = data


    # Defines handler function to be used in event engine.
    HandlerType: callable = Callable[[Event], None]


    class EventEngine:
        """
        Event engine distributes event object based on its type
        to those handlers registered.

        It also generates timer event by every interval seconds,
        which can be used for timing purpose.
        """

        def __init__(self, interval: int = 1) -> None:
            """
            初始化事件引擎。

            :param interval: 定时器事件的生成间隔，默认为1秒。
            """
            # 设置定时器事件的生成间隔
            self._interval: int = interval
            # 创建一个事件队列
            self._queue: Queue = Queue()
            # 设置事件引擎的活动状态为False
            self._active: bool = False
            # 创建一个线程来运行事件处理循环
            self._thread: Thread = Thread(target=self._run)
            # 创建一个线程来运行定时器事件生成循环
            self._timer: Thread = Thread(target=self._run_timer)
            # 创建一个默认字典来存储事件处理程序
            self._handlers: defaultdict = defaultdict(list)
            # 创建一个列表来存储通用事件处理程序
            self._general_handlers: List = []

        def _run(self) -> None:
            """
            从事件队列中获取事件并进行处理。

            该方法会在事件引擎处于活动状态时，不断从事件队列中获取事件，并调用_process方法进行处理。如果队列为空，则会等待1秒后再次尝试获取。

            :return: 无返回值
            """
            while self._active:
                try:
                    # 从事件队列中获取事件，设置阻塞并等待1秒超时
                    event: Event = self._queue.get(block=True, timeout=1)
                    # 处理获取到的事件
                    self._process(event)
                except Empty:
                    # 如果队列为空，则捕获Empty异常并继续循环
                    pass

        def _process(self, event: Event) -> None:
            """
            处理事件。

            该方法首先将事件分发给注册了该事件类型的处理程序，然后分发给所有通用处理程序。

            :param event: 要处理的事件对象。
            :return: 无返回值
            """
            # 检查事件类型是否在已注册的处理程序中
            if event.type in self._handlers:
                # 遍历并调用注册的处理程序来处理事件
                [handler(event) for handler in self._handlers[event.type]]

            # 检查是否有通用处理程序
            if self._general_handlers:
                # 遍历并调用通用处理程序来处理事件
                [handler(event) for handler in self._general_handlers]

        def _run_timer(self) -> None:
            """
            按照指定的时间间隔生成定时器事件。

            该方法会在事件引擎处于活动状态时，每隔指定的时间间隔生成一个定时器事件，并将其放入事件队列中。

            :return: 无返回值
            """
            while self._active:
                # 按照指定的时间间隔休眠
                sleep(self._interval)
                # 创建一个定时器事件
                event: Event = Event(EVENT_TIMER)
                # 将定时器事件放入事件队列中
                self.put(event)

        def start(self) -> None:
            """
            启动事件引擎。

            该方法将启动事件引擎的运行，包括启动事件处理线程和定时器线程。

            :return: 无返回值
            """
            # 设置事件引擎的活动状态为True，启动事件处理线程和定时器线程
            self._active = True
            self._thread.start()
            self._timer.start()
    def stop(self) -> None:
        """
        停止事件引擎。
        该方法将停止事件引擎的运行，包括停止事件处理线程和定时器线程。
        :return: 无返回值
        """
        # 设置事件引擎的活动状态为False，停止事件处理线程和定时器线程
        self._active = False
        # 等待定时器线程结束
        self._timer.join()
        # 等待事件处理线程结束
        self._thread.join()

    def put(self, event: Event) -> None:
        """
        将事件对象放入事件队列。

        :param event: 要放入队列的事件对象。
        """
        self._queue.put(event)

    def register(self, type: str, handler: HandlerType) -> None:
        """
        注册一个事件处理程序。

        :param type: 事件类型。
        :param handler: 事件处理程序。
        """
        handler_list: list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, type: str, handler: HandlerType) -> None:
        """
        注销一个事件处理程序。

        :param type: 事件类型。
        :param handler: 事件处理程序。
        """
        handler_list: list = self._handlers[type]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(type)

    def register_general(self, handler: HandlerType) -> None:
        """
        注册一个通用事件处理程序。

        :param handler: 通用事件处理程序。
        """
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler: HandlerType) -> None:
        """
        注销一个通用事件处理程序。

        :param handler: 通用事件处理程序。
        """
        # 检查处理程序是否在通用处理程序列表中
        if handler in self._general_handlers:
            # 如果在列表中，则移除该处理程序
            self._general_handlers.remove(handler)
