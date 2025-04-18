import logging
from gi.repository import GLib

import traceback
from .module import Module
from .page import Page
from .sections import SectionFactory

from .tools.yml_tools import load_modules
from .widgets.deps_alert_dialog import TuneItDepsAlertDialog

from .deps import DependencyManager

logger = logging.getLogger("init_settings_stack")

def init_settings_stack(stack, listbox, split_view):
    yaml_data = load_modules()
    section_factory = SectionFactory()
    modules_dict = {}
    pages_dict = {}

    dep_manager = DependencyManager()

    if stack.get_pages():
        logger.info("Clear pages...")
        listbox.remove_all()
        for page in stack.get_pages(): stack.remove(page)
    else:
        logger.info("First init...")

    current_module_index = 0
    modules = list(yaml_data)
    window = listbox.get_root()

    def process_next_module():
        nonlocal current_module_index

        if current_module_index >= len(modules):
            finalize_processing()
            return

        module_data = modules[current_module_index]
        current_module_index += 1

        try:
            deps_results = dep_manager.verify_deps(module_data.get('deps', {}))
            conflicts_results = dep_manager.verify_conflicts(module_data.get('conflicts', {}))

            deps_message = dep_manager.format_results(deps_results)
            conflicts_message = dep_manager.format_results(conflicts_results)

            all_deps_ok = all(r['success'] for r in deps_results)
            all_conflicts_ok = all(r['success'] for r in conflicts_results)

            if all_deps_ok and all_conflicts_ok:
                process_module(module_data)
                GLib.idle_add(process_next_module)
            else:
                show_dialog(module_data, deps_message, conflicts_message)
        except Exception as e:
            handle_error(e, module_data)
            GLib.idle_add(process_next_module)

    def show_dialog(module_data, deps_msg, conflicts_msg):
        dialog = TuneItDepsAlertDialog()
        dialog.set_body(module_data['name'])
        dialog.deps_message_textbuffer.set_text(f"{deps_msg}\n{conflicts_msg}")

        def handle_response(response):
            if response == "skip":
                GLib.idle_add(process_next_module)
            else:
                process_module(module_data)
                GLib.idle_add(process_next_module)

        dialog.ask_user(window, handle_response)

    def process_module(module_data):
        module = Module(module_data)
        modules_dict[module.name] = module

        for section_data in module_data.get('sections', []):
            page_name = module.get_translation(section_data.get('page', 'Default'))
            module_page_name = section_data.get('page', 'Default')

            if page_name not in pages_dict:
                page_info = module.pages.get(f"_{module_page_name}", {}) or module.pages.get(module_page_name, {})
                page = Page(name=page_name, icon=page_info.get('icon'))
                pages_dict[page_name] = page

            section = section_factory.create_section(section_data, module)
            pages_dict[page_name].add_section(section)

    def finalize_processing():
        pages = sorted(pages_dict.values(), key=lambda p: p.name)
        for page in pages:
            page.sort_sections()
            page.create_stack_page(stack, listbox)

        if not stack:
            logger.error("settings_pagestack не найден.")

        def on_row_selected(listbox, row):
            if row:
                page_id = row.props.name
                visible_child = stack.get_child_by_name(page_id)
                if visible_child:
                    stack.set_visible_child(visible_child)
                    split_view.set_show_content(True)

        listbox.connect("row-selected", on_row_selected)

    def handle_error(e, module_data):
        from ..main import get_error
        error = get_error()
        full_traceback = traceback.format_exc()
        error_msg = f"Module '{module_data['name']}' loading error\nError: {e}\nFull traceback:\n{full_traceback}"
        error(error_msg)

    GLib.idle_add(process_next_module)