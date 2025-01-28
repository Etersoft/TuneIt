from .module import Module
from .page import Page
from .sections import SectionFactory

from .tools.yml_tools import load_modules


def init_settings_stack(stack, listbox, split_view):
    yaml_data = load_modules()
    section_factory = SectionFactory()
    modules_dict = {}
    pages_dict = {}

    if stack.get_pages():
        print("Clear pages...")
        listbox.remove_all()
        for page in stack.get_pages():
            stack.remove(page)
    else:
        print("First init...")

    for module_data in yaml_data:
        module = Module(module_data)
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
