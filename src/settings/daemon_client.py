import dbus
import ast


class DaemonClient:
    def __new__(cls, bus_name="ru.ximperlinux.TuneIt.Daemon", object_path="/Daemon"):
        """
        Создает экземпляр клиента только в случае, если сервис доступен.

        :param bus_name: Имя D-Bus сервиса.
        :param object_path: Путь объекта в D-Bus.
        :return: Экземпляр DaemonClient или None, если сервис недоступен.
        """
        try:
            bus = dbus.SystemBus()
            bus.get_object(bus_name, object_path)  # Проверка доступности объекта
            return super(DaemonClient, cls).__new__(cls)
        except dbus.DBusException:
            print(f"Service '{bus_name}' is not running.")
            return None

    def __init__(self, bus_name="ru.ximperlinux.TuneIt.Daemon", object_path="/Daemon"):
        """
        Инициализация клиента для взаимодействия с D-Bus сервисом.

        :param bus_name: Имя D-Bus сервиса.
        :param object_path: Путь объекта в D-Bus.
        """
        self.bus_name = bus_name
        self.object_path = object_path
        self.bus = dbus.SystemBus()
        self.proxy = self.bus.get_object(bus_name, object_path)
        self.interface = dbus.Interface(
            self.proxy, dbus_interface="ru.ximperlinux.TuneIt.DaemonInterface"
        )
        print("dbus client connected")

        self.backend_name = None
        self.backend_params = None

    def set_backend_name(self, backend_name):
        """
        Устанавливает имя backend.

        :param backend_name: Имя backend.
        """
        self.backend_name = backend_name

    def set_backend_params(self, backend_params):
        """
        Устанавливает параметры backend.

        :param backend_params: Параметры backend в формате JSON.
        """
        self.backend_params = str(backend_params)

    def get_value(self, key, gtype):
        """
        Вызывает метод GetValue на D-Bus сервисе.

        :param key: Ключ для получения значения.
        :param gtype: Тип значения.
        :return: Полученное значение.
        """
        try:
            return ast.literal_eval(str(self.interface.GetValue(self.backend_name, str(self.backend_params), key, gtype)))
        except dbus.DBusException as e:
            print(f"Error in GetValue: {e}")
            return None

    def set_value(self, key, value, gtype):
        """
        Вызывает метод SetValue на D-Bus сервисе.

        :param key: Ключ для установки значения.
        :param value: Устанавливаемое значение.
        :param gtype: Тип значения.
        :return: Результат операции.
        """
        try:
            self.interface.SetValue(self.backend_name, str(self.backend_params), key, str(value), gtype)
        except dbus.DBusException as e:
            print(f"Error in SetValue: {e}")

    def get_range(self, key, gtype):
        """
        Вызывает метод GetRange на D-Bus сервисе.

        :param key: Ключ для получения диапазона.
        :param gtype: Тип значения.
        :return: Диапазон значений.
        """
        try:
            return ast.literal_eval(str(self.interface.GetRange(self.backend_name, str(self.backend_params), key, gtype)))
        except dbus.DBusException as e:
            print(f"Error in GetRange: {e}")
            return None

dclient = DaemonClient()
