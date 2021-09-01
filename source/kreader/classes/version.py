class Version:
    def __init__(self, version: str):
        self.big, self.small, self.patch = [ int(part) for part in version.split('.') ]
    
    def __lt__(self, other: 'Version'):
        if self.big == other.big:
            if self.small == other.small:
                return self.patch < other.patch
            return self.small < other.small
        return self.big < other.big

    def __gt__(self, other: 'Version'):
        if self.big == other.big:
            if self.small == other.small:
                return self.patch > other.patch
            return self.small > other.small
        return self.big > other.big
    
    def __eq__(self, other: 'Version'):
        return self.big == other.big and self.small == other.small and self.patch == other.patch

