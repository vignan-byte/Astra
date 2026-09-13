from .models import Permission


class PolicyEngine:
    """Single policy boundary for all adapters."""
    destructive_terms = ("delete", "remove", "send", "email", "message", "call", "purchase", "submit", "pay")
    blocked_terms = ("password", "credential", "bypass", "disable security")

    def classify(self, action: str) -> Permission:
        normalized = action.lower()
        if any(term in normalized for term in self.blocked_terms):
            return Permission.blocked
        if any(term in normalized for term in self.destructive_terms):
            return Permission.confirm
        return Permission.read
