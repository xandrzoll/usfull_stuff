import time


class PrintStatus:
    status_bar_fmt = '\r|<bar><space>| - <current> из <max>'
    symbol_fill = '#'
    symbol_space = ' '

    def __init__(self, statuses: list):
        self.statuses = statuses
        self.generator = self._generator()

    def _generator(self):
        for status in self.statuses:
            print(status)
            yield

    @staticmethod
    def print_status_bar(current_iter=0, max_iter=0, size=20, **kwargs):
        fill_value = int(size * current_iter / max_iter)
        space_value = int(size * (1 - current_iter / max_iter))
        print(PrintStatus._get_status_bar_string(fill_value, space_value, current_iter, max_iter), end='')
        if current_iter == max_iter:
            print()

    @staticmethod
    def _get_status_bar_string(fill_value, space_value, current_iter, max_iter):
        status_bar = PrintStatus.status_bar_fmt.replace('<bar>', PrintStatus.symbol_fill * fill_value)
        status_bar = status_bar.replace('<space>', PrintStatus.symbol_space * space_value)
        status_bar = status_bar.replace('<current>', str(current_iter))
        status_bar = status_bar.replace('<max>', str(max_iter))
        return status_bar

    def next(self, status_bar=False, **kwargs):
        if status_bar:
            self.print_status_bar(**kwargs)
            return
        try:
            next(self.generator)
        except StopIteration:
            ...


my_statuses = [
        'Получаю данные',
        'Формирую корзину',
        'Кормлю котиков',
        'Заряжаю батарейки',
        'Изменяю пространственно-временной континиум',
]

# создаю объект
print_status = PrintStatus(my_statuses)

# через метод next вызываю первый статус
print_status.next()

# здесь
# может
# быть
# ваш
# код

time.sleep(1)

# печатаю следующий статус
print_status.next()
time.sleep(1)
print_status.next()
time.sleep(1)

# а здесь я запускаю статус-бар
for i in range(10):
    print_status.next(status_bar=True, current_iter=i+1, max_iter=10, size=20)
    time.sleep(1)

print_status.next()
time.sleep(1)

# когда статусы закончились генератор выдает ошибку, но в методе она перехватывается, и статусы больше не печатаются
print_status.next()
time.sleep(1)
print_status.next()
time.sleep(1)
