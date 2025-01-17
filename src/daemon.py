import ast
import logging

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

from .settings.backends import root_backend_factory

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Daemon(dbus.service.Object):
    def __init__(self, bus, object_path):
        super().__init__(bus, object_path)
        self.dbus_info = None
        self.polkit = None

    def _check_polkit_privilege(self, sender, conn, privilege):
        """
        Проверяет привилегии с использованием PolicyKit.

        :param sender: Отправитель D-Bus сообщения.
        :param conn: Соединение D-Bus.
        :param privilege: Проверяемая привилегия.
        :return: True, если авторизация успешна; иначе False.
        """
        if self.dbus_info is None:
            self.dbus_info = dbus.Interface(
                conn.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus"),
                "org.freedesktop.DBus"
            )
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)

        if self.polkit is None:
            try:
                bus_object = dbus.SystemBus().get_object(
                    "org.freedesktop.PolicyKit1",
                    "/org/freedesktop/PolicyKit1/Authority"
                )
                self.polkit = dbus.Interface(bus_object, "org.freedesktop.PolicyKit1.Authority")
            except Exception as e:
                logger.error(f"Failed to connect to PolicyKit: {e}")
                raise

        retry_limit = 3
        retry_count = 0
        while retry_count < retry_limit:
            try:
                auth_response = self.polkit.CheckAuthorization(
                    ("unix-process", {"pid": dbus.UInt32(pid, variant_level=1),
                                      "start-time": dbus.UInt64(0, variant_level=1)}),
                    privilege, {"AllowUserInteraction": "true"}, dbus.UInt32(1), "", timeout=600
                )
                is_auth, _, _ = auth_response
                return is_auth
            except dbus.DBusException as e:
                if e._dbus_error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                    retry_count += 1
                    logger.warning(f"PolicyKit service unavailable, retrying ({retry_count}/{retry_limit})...")
                    self.polkit = None
                else:
                    logger.error(f"DBusException occurred: {e}")
                    raise

        logger.error("Failed to authorize: PolicyKit service unavailable after retries.")
        return False

    @dbus.service.method(
        dbus_interface="ru.ximperlinux.TuneIt.DaemonInterface",
        in_signature="ssss",
        out_signature="s",
        sender_keyword="sender",
        connection_keyword="conn"
    )
    def GetValue(self, backend_name, backend_params, key, gtype, sender=None, conn=None):
        if not self._check_polkit_privilege(sender, conn, "ru.ximperlinux.TuneIt.Daemon.auth"):
            raise dbus.DBusException(
                "org.freedesktop.DBus.Error.AccessDenied",
                "Permission denied"
            )
        try:
            backend_params = ast.literal_eval(backend_params)
            backend = root_backend_factory.get_backend(backend_name, backend_params)
            if backend:
                return str(backend.get_value(key, gtype))
        except Exception as e:
            return dbus.DBusException(
                "ru.ximperlinux.TuneIt.Daemon", e
            )
        return f"backend_name: {backend_name}, params: {backend_params}, key: {key}"

    @dbus.service.method(
        dbus_interface="ru.ximperlinux.TuneIt.DaemonInterface",
        in_signature="sssss",
        out_signature="s",
        sender_keyword="sender",
        connection_keyword="conn"
    )
    def SetValue(self, backend_name, backend_params, key, value, gtype, sender=None, conn=None):
        if not self._check_polkit_privilege(sender, conn, "ru.ximperlinux.TuneIt.Daemon.auth"):
            raise dbus.DBusException(
                "org.freedesktop.DBus.Error.AccessDenied",
                "Permission denied"
            )
        try:
            backend_params = ast.literal_eval(backend_params)
            backend = root_backend_factory.get_backend(backend_name, backend_params)
            if backend:
                backend.set_value(key, value, gtype)
        except Exception as e:
            return dbus.DBusException(
                "ru.ximperlinux.TuneIt.Daemon", e
            )
        return f"Failed to set value for backend_name: {backend_name}, key: {key}"

    @dbus.service.method(
        dbus_interface="ru.ximperlinux.TuneIt.DaemonInterface",
        in_signature="ssss",
        out_signature="s",
        sender_keyword="sender",
        connection_keyword="conn"
    )
    def GetRange(self, backend_name, backend_params, key, gtype, sender=None, conn=None):
        if not self._check_polkit_privilege(sender, conn, "ru.ximperlinux.TuneIt.Daemon.auth"):
            raise dbus.DBusException(
                "org.freedesktop.DBus.Error.AccessDenied",
                "Permission denied"
            )
        try:
            backend_params = ast.literal_eval(backend_params)
            backend = root_backend_factory.get_backend(backend_name, backend_params)
            if backend:
                return str(backend.get_range(key, gtype))
        except Exception as e:
            return dbus.DBusException(
                "ru.ximperlinux.TuneIt.Daemon", e
            )
        return f"Failed to get range for backend_name: {backend_name}, key: {key}"

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    try:
        bus = dbus.SystemBus()
        name = dbus.service.BusName("ru.ximperlinux.TuneIt.Daemon", bus)
        daemon = Daemon(bus, "/Daemon")
        logger.info("Service is running...")
        mainloop = GLib.MainLoop()
        mainloop.run()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user.")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
