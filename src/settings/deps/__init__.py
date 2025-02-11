from .os import OSReleaseChecker
from .path import PathChecker
from .binary import BinaryChecker

class DependencyCheckerFactory:
    def __init__(self):
        self._checkers = {
            'os': OSReleaseChecker,
            'path': PathChecker,
            'binary': BinaryChecker,
        }
        
    def create_checker(self, dependency_type):
        checker_class = self._checkers.get(dependency_type)
        if not checker_class:
            raise ValueError(f"Unfinished type of dependence: {dependency_type}")
        return checker_class()

class DependencyManager:
    def __init__(self):
        self.factory = DependencyCheckerFactory()
    
    def _verify(self, items, check_type):
        results = []
        for item_type, expected_value in items.items():
            try:
                checker = self.factory.create_checker(item_type)
                result = checker.check(expected_value, is_conflict=(check_type == "conflict"))
                results.append({
                    'type': check_type,
                    'name': item_type,
                    'success': result['success'],
                    'actual': result['actual'],
                    'expected': result['expected'],
                    'error': result.get('error', '')
                })
            except Exception as e:
                print(f"Error when checking {item_type}: {str(e)}")
                results.append({
                    'type': check_type,
                    'name': item_type,
                    'success': False,
                    'error': str(e)
                })
        return results

    def verify_deps(self, dependencies):
        return self._verify(dependencies, "dependency")

    def verify_conflicts(self, conflicts):
        return self._verify(conflicts, "conflict")

    def format_results(self, results):
        message = ""
        for result in results:
            label = {
                'dependency': f"{result['name']} {_("dependency")}",
                'conflict': f"{result['name']} {_("conflict")}"
            }[result['type']]

            status = "✓" if result['success'] else "✕"

            message += f"{label} {status}\n"
            if 'actual' in result:
                message += f"   {_("Actual")} {result['actual']}\n"
                message += f"   {_("Expected")}: {result['expected']}\n"
            if result['error']:
                message += f"   {_("Error")} {result['error']}\n"
        return message
