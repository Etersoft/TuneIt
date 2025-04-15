import logging


logger = logging.getLogger(f"{__name__}")

def convert_by_gvariant(value, gtype):
    """
    Приводит значение к нужному типу в зависимости от GVariant gtype.

    :param value: Исходное значение
    :param gtype: Тип GVariant ('b', 'y', 'n', 'q', 'i', 'u', 'x', 't', 'd', 's')
    :return: Значение, приведенное к указанному типу
    """
    try:
        if gtype == 'b':  # Boolean
            return bool(value)
        elif gtype == 'y':  # Byte
            return max(0, min(255, int(value)))  # Ограничение диапазона
        elif gtype == 'n':  # Int16
            return max(-32768, min(32767, int(value)))  # Ограничение диапазона
        elif gtype == 'q':  # Uint16
            return max(0, min(65535, int(value)))  # Ограничение диапазона
        elif gtype == 'i':  # Int32
            return max(-2147483648, min(2147483647, int(value)))
        elif gtype == 'u':  # Uint32
            return max(0, min(4294967295, int(value)))
        elif gtype == 'x':  # Int64
            return max(-9223372036854775808, min(9223372036854775807, int(value)))
        elif gtype == 't':  # Uint64
            return max(0, min(18446744073709551615, int(value)))
        elif gtype == 'd':  # Double
            return float(value)
        elif gtype == 's':  # String
            return str(value)
        else:
            raise ValueError(f"Неизвестный GVariant тип: {gtype}")
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка приведения типа: {e}")
        return None
