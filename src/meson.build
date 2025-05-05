pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'tuneit'
gnome = import('gnome')

blp_search = run_command('find_blp.sh', '', check: true)


blp_files = blp_search.stdout().splitlines()

blueprints = custom_target('blueprints',
  input: files(
   blp_files,
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('tuneit',
  'tuneit.gresource.xml',
  dependencies: blueprints,
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

conf.set('IS_DEVEL', get_option('is_devel'))

configure_file(
  input: 'tuneit.in',
  output: 'tuneit',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

configure_file(
  input: 'daemon.in',
  output: 'tuneit-daemon',
  configuration: conf,
  install: true,
  install_dir: get_option('sbindir'),
  install_mode: 'r-xr-xr-x'
)

configure_file(
  input: 'config.py',
  output: 'config.py',
  configuration: conf,
  install: true,
  install_dir: moduledir

)

tuneit_sources = [
  '__init__.py',
  'about.py',
  'main.py',
  'window.py',
  'daemon.py',
]

install_data(tuneit_sources, install_dir: moduledir)

blp_search_settings = run_command('find_blp.sh', 'settings', check: true)
blp_search_shop = run_command('find_blp.sh', 'shop', check: true)

blp_files_settings = blp_search_settings.stdout().splitlines()
blp_files_shop = blp_search_shop.stdout().splitlines()

install_subdir('settings', install_dir: moduledir, strip_directory : false, exclude_files: blp_files_settings)

# install_subdir('shop', install_dir: moduledir, strip_directory : false, exclude_files: blp_files_shop)
