"""Error handling and resilience patterns."""

from typing import List
from ..db_manager import Pattern


def get_error_handling_patterns() -> List[Pattern]:
    """Get error handling patterns."""
    return [
        Pattern(
            name="retry_with_backoff",
            language="python",
            pattern_type="resilience",
            code_snippet="""
def retry_with_backoff(max_retries=3, backoff_factor=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator
""",
            usage_context="Exponential backoff retry mechanism",
            dependencies=["time"],
            success_count=32
        ),
        Pattern(
            name="circuit_breaker",
            language="python",
            pattern_type="resilience",
            code_snippet="""
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            raise
""",
            usage_context="Circuit breaker pattern for fault tolerance",
            dependencies=["time"],
            success_count=26
        ),
        Pattern(
            name="error_collector",
            language="python",
            pattern_type="error_handling",
            code_snippet="""
class ErrorCollector:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, message, context=None):
        self.errors.append({
            'message': message,
            'context': context,
            'timestamp': time.time()
        })
    
    def add_warning(self, message, context=None):
        self.warnings.append({
            'message': message,
            'context': context,
            'timestamp': time.time()
        })
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def get_summary(self):
        return {
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings
        }
""",
            usage_context="Collect and manage multiple errors",
            dependencies=["time"],
            success_count=20
        ),
        Pattern(
            name="fallback_pattern",
            language="python",
            pattern_type="resilience",
            code_snippet="""
def with_fallback(primary_func, fallback_func, exceptions=(Exception,)):
    def wrapper(*args, **kwargs):
        try:
            return primary_func(*args, **kwargs)
        except exceptions:
            return fallback_func(*args, **kwargs)
    return wrapper
""",
            usage_context="Fallback mechanism for failed operations",
            dependencies=[],
            success_count=28
        ),
        Pattern(
            name="timeout_context",
            language="python",
            pattern_type="resilience",
            code_snippet="""
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
""",
            usage_context="Timeout context manager for operations",
            dependencies=["signal", "contextlib"],
            success_count=24
        ),
        Pattern(
            name="error_context_manager",
            language="python",
            pattern_type="error_handling",
            code_snippet="""
@contextmanager
def error_context(operation_name, reraise=True, default_return=None):
    try:
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        if reraise:
            raise
        return default_return
""",
            usage_context="Context manager for error logging and handling",
            dependencies=["contextlib", "logging"],
            success_count=22
        )
    ]