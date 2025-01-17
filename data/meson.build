desktop_file = i18n.merge_file(
        input: 'ru.ximperlinux.TuneIt.desktop.in',
       output: 'ru.ximperlinux.TuneIt.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'applications'
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file])
endif

appstream_file = i18n.merge_file(
        input: 'ru.ximperlinux.TuneIt.metainfo.xml.in',
       output: 'ru.ximperlinux.TuneIt.metainfo.xml',
       po_dir: '../po',
      install: true,
  install_dir: get_option('datadir') / 'metainfo'
)

appstreamcli = find_program('appstreamcli', required: false, disabler: true)
test('Validate appstream file', appstreamcli,
     args: ['validate', '--no-net', '--explain', appstream_file])

install_data('ru.ximperlinux.TuneIt.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

compile_schemas = find_program('glib-compile-schemas', required: false, disabler: true)
test('Validate schema file',
     compile_schemas,
     args: ['--strict', '--dry-run', meson.current_source_dir()])


service_conf = configuration_data()
service_conf.set('bindir', get_option('prefix') / get_option('bindir'))
configure_file(
  input: 'ru.ximperlinux.TuneIt.service.in',
  output: 'ru.ximperlinux.TuneIt.service',
  configuration: service_conf,
  install_dir: get_option('datadir') / 'dbus-1' / 'services'
)

install_data('ru.ximperlinux.TuneIt.Daemon.policy',
  install_dir: get_option('datadir') / 'polkit-1' / 'actions'
)

install_data('ru.ximperlinux.TuneIt.Daemon.conf',
  install_dir: get_option('sysconfdir') / 'dbus-1' / 'system.d'
)

subdir('icons')
