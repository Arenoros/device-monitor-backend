import yaml

class YamlWrapper:
    def __init__(self, path):
        with open(path, 'r') as f:
            self.data = yaml.safe_load(f.read())

    def has(self, path, value):
        elem = self.data
        for name in path.split('.'):
            elem = elem[name] if name in elem else None
            if not elem: break
        return True if elem and value in elem else False

    def __getitem__(self, path):
        elem = self.data
        for name in path.split('.'):
            elem = elem[name] if name in elem else None
            if not elem: break
        return elem

    def __repr__(self):
        return "YamlWrapper()"

    def __str__(self):
        return f'{self.data}'