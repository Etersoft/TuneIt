#!/bin/bash

sslk() {
    gsettings set org.gnome.desktop.wm.keybindings switch-input-source "$1"
}

ck() {
    gsettings set org.gnome.desktop.wm.keybindings switch-input-source "['']"
    gsettings set org.gnome.desktop.wm.keybindings switch-input-source-backward "['']"
    sslk "['']"
    gsettings set org.gnome.desktop.input-sources xkb-options "['']"
}

get_range() {
    echo '["<Ctrl>Shift_L", "<Super>space", "<Alt>Shift_L", "CapsLock"]'
}

set_value() {
    ck
    layout="$1"
    case "$layout" in
        "<Alt>Shift_L")
        sslk "['$layout', '<Shift>Alt_L']"
        ;;
        "<Ctrl>Shift_L")
        sslk "['<Shift>Control_L', '<Ctrl>Shift_L']"
        ;;
        "CapsLock")
        gsettings set org.gnome.desktop.input-sources xkb-options "['grp:caps_toggle']"
        ;;
        *)
        sslk "['$layout']"
        ;;
    esac
}

get_value() {
    current_keybinding=$(gsettings get org.gnome.desktop.wm.keybindings switch-input-source)
    current_xkb_options=$(gsettings get org.gnome.desktop.input-sources xkb-options)

    if [[ "$current_xkb_options" == *"grp:caps_toggle"* ]]; then
        echo "CapsLock"
    else
        case "$current_keybinding" in
            "['<Ctrl>Shift_L', '<Shift>Control_L']")
                echo "<Ctrl>Shift_L"
                ;;
            "['<Alt>Shift_L', '<Shift>Alt_L']")
                echo "<Alt>Shift_L"
                ;;
            "['<Super>space']")
                echo "<Super>space"
                ;;
            "[]")
                echo "No keybinding set"
                ;;
            *)
                echo "Unknown layout"
                ;;
        esac
    fi
}

command="$1"

case "$command" in
    "get_range")
        get_range
        ;;
    "set_value")
        layout="$2"
        set_value "$layout"
        ;;
    "get_value")
        get_value
        ;;
    *)
        echo "Неизвестная команда: $command"
        exit 1
        ;;
esac
