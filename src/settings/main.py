import time
import traceback
from .module import Module
from .page import Page
from .sections import SectionFactory

from .tools.yml_tools import load_modules
from .widgets.deps_alert_dialog import TuneItDepsAlertDialog

from .deps import DependencyManager

def init_settings_stack(stack, listbox, split_view):
    yaml_data = load_modules()
    section_factory = SectionFactory()
    modules_dict = {}
    pages_dict = {}

    dep_manager = DependencyManager()

    if stack.get_pages():
        print("Clear pages...")
        listbox.remove_all()
        for page in stack.get_pages():
            stack.remove(page)
    else:
        print("First init...")

    for module_data in yaml_data:
        module = Module(module_data)

        try:
            deps_results = dep_manager.verify_deps(module_data.get('deps', {}))
            conflicts_results = dep_manager.verify_conflicts(module_data.get('conflicts', {}))

            deps_message = dep_manager.format_results(deps_results)
            conflicts_message = dep_manager.format_results(conflicts_results)

            all_deps_ok = all(r['success'] for r in deps_results)
            all_conflicts_ok = all(r['success'] for r in conflicts_results)

            if all_deps_ok and all_conflicts_ok:
                print("Deps: OK")
            else:
                dialog = TuneItDepsAlertDialog()
                dialog.set_body(module_data['name'])

                dialog.deps_message_textbuffer.set_text(
                    f"{deps_message}\n{conflicts_message}"
                )

                while True:
                    w = listbox.get_root()
                    if w.get_visible() and w.get_mapped():
                        response = dialog.user_question(w)
                        break
                    time.sleep(0.1)

                print(f"RESPONSE: {response}")
                if response == "skip":
                    break

            modules_dict[module.name] = module

            for section_data in module_data.get('sections', []):
                page_name = module.get_translation(section_data.get('page', 'Default'))
                module_page_name = section_data.get('page', 'Default')
                print(module_page_name)

                if page_name not in pages_dict:

                    page_info = (
                        module.pages.get(f"_{module_page_name}", {})
                        or module.pages.get(module_page_name, {})
                    )

                    page = Page(
                        name=page_name,
                        icon=page_info.get('icon'),
                    )
                    pages_dict[page_name] = page

                section = section_factory.create_section(section_data, module)
                pages_dict[page_name].add_section(section)
        except Exception as e:
            from ..main import get_error
            error = get_error()

            full_traceback = traceback.format_exc()
            e = f"Module '{module.name}' loading error \nError: {e}\nFull traceback:\n{full_traceback}"

            error(e)

    pages = list(pages_dict.values())
    for page in pages:
        page.sort_sections()

    pages = sorted(pages, key=lambda p: p.name)

    for page in pages:
        page.create_stack_page(stack, listbox)

    if not stack:
        print("Ошибка: settings_pagestack не найден.")

    def on_row_selected(listbox, row):
        if row:
            page_id = row.props.name
            print(f"Selected page: {page_id}")

            visible_child = stack.get_child_by_name(page_id)
            if visible_child:
                stack.set_visible_child(visible_child)
                split_view.set_show_content(True)

    listbox.connect("row-selected", on_row_selected)
