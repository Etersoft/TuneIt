Name: ximper-tuneit
Version: 0.1.0
Release: alt1
License: GPLv3

Summary: A modular configuration tool

Group: System/Configuration/Other

Url: https://gitlab.eterfund.ru/ximperlinux/tuneit

BuildArch: noarch

Source: %name-%version.tar

AutoProv: no

BuildRequires(pre): rpm-macros-meson rpm-macros-systemd
BuildRequires(pre): rpm-build-python3
BuildRequires(pre): rpm-build-gir

BuildRequires: libadwaita-gir-devel
BuildRequires: meson

%add_python3_path %_datadir/%name

%description
A modular configuration tool
where each setting is defined in separate files for flexibility and extensibility.

%prep
%setup

%build
%meson
%meson_build

%install
%meson_install
%find_lang %name

%files -f %name.lang
%_bindir/%name

%_datadir/%name
%_datadir/glib-2.0/schemas/*.gschema.xml
%_datadir/metainfo/*.metainfo.xml

%_desktopdir/ru.ximperlinux.TuteIt.desktop

%_iconsdir/hicolor/*/apps/*.svg

%changelog
* Tue Dec 17 2024 Roman Alifanov <ximper@altlinux.org> 0.1.0-alt1
- initial build

