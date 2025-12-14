class UndoStack:
    def __init__(self, limit=10):
        self.history = []  # Стек действий
        self.limit = limit

    def push(self, command):
        """Добавляет новую команду и выполняет её"""
        # Сначала выполняем действие
        success = command.execute()

        if success:
            # Если стек переполнен, удаляем самое старое действие
            if len(self.history) >= self.limit:
                self.history.pop(0)

            self.history.append(command)
            return True
        return False

    def undo(self):
        """Отменяет последнее действие"""
        if not self.history:
            return False, "Нечего отменять"

        # Достаем последнюю команду
        command = self.history.pop()

        # Вызываем её метод отмены
        success = command.undo()

        if success:
            return True, "Действие отменено"
        else:
            return False, "Ошибка при отмене"


# Глобальный объект стека (один на всё приложение)
undo_manager = UndoStack(limit=10)