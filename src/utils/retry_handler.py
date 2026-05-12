"""Advanced retry mechanism with exponential backoff and circuit breaker."""
import time
import random
from typing import Callable, Any, Optional, List, Dict, Union
from functools import wraps
from enum import Enum
from src.config.settings import get_settings
from src.config.logger import log


class RetryStrategy(Enum):
    """Different retry strategies."""
    
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_DELAY = "no_delay"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovery


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        retry_on: Optional[List[Exception]] = None,
        stop_on: Optional[List[Exception]] = None,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.strategy = strategy
        self.retry_on = retry_on or [Exception]
        self.stop_on = stop_on or []
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""
    
    def __init__(self, threshold: int = 5, timeout: float = 60.0):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
    
    def call_allowed(self) -> bool:
        """Check if call is allowed based on circuit breaker state."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                log.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        
        return True  # HALF_OPEN allows calls
    
    def record_success(self):
        """Record successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            log.info("Circuit breaker transitioning to CLOSED")
    
    def record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.threshold:
            self.state = CircuitBreakerState.OPEN
            log.warning(f"Circuit breaker transitioning to OPEN after {self.failure_count} failures")


class RetryHandler:
    """Advanced retry handler with circuit breaker."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.settings = get_settings()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def get_circuit_breaker(self, key: str) -> CircuitBreaker:
        """Get or create circuit breaker for a key."""
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker(
                threshold=self.config.circuit_breaker_threshold,
                timeout=self.config.circuit_breaker_timeout
            )
        return self.circuit_breakers[key]
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on retry strategy."""
        if self.config.strategy == RetryStrategy.NO_DELAY:
            return 0.0
        
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (self.config.backoff_multiplier ** (attempt - 1))
        
        else:
            delay = self.config.base_delay
        
        # Apply jitter if enabled
        if self.config.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return min(delay, self.config.max_delay)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if operation should be retried."""
        # Check if we've exceeded max attempts
        if attempt >= self.config.max_attempts:
            return False
        
        # Check if exception is in stop_on list
        for stop_exception in self.config.stop_on:
            if isinstance(exception, stop_exception):
                return False
        
        # Check if exception is in retry_on list
        for retry_exception in self.config.retry_on:
            if isinstance(exception, retry_exception):
                return True
        
        return False
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        circuit_breaker_key: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic and circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            circuit_breaker_key: Key for circuit breaker
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        # Check circuit breaker if enabled
        if circuit_breaker_key:
            circuit_breaker = self.get_circuit_breaker(circuit_breaker_key)
            if not circuit_breaker.call_allowed():
                raise Exception(f"Circuit breaker OPEN for key: {circuit_breaker_key}")
        
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                
                # Record success if circuit breaker is used
                if circuit_breaker_key:
                    self.get_circuit_breaker(circuit_breaker_key).record_success()
                
                if attempt > 1:
                    log.info(f"Operation succeeded on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Record failure if circuit breaker is used
                if circuit_breaker_key:
                    self.get_circuit_breaker(circuit_breaker_key).record_failure()
                
                # Check if we should retry
                if not self.should_retry(e, attempt):
                    log.error(f"Exception {type(e).__name__} not in retry list, stopping retries")
                    break
                
                if attempt < self.config.max_attempts:
                    delay = self.calculate_delay(attempt)
                    log.warning(
                        f"Attempt {attempt} failed with {type(e).__name__}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)
        
        log.error(f"All {self.config.max_attempts} attempts failed")
        raise last_exception
    
    def retry(self, circuit_breaker_key: Optional[str] = None):
        """
        Decorator for retry functionality.
        
        Args:
            circuit_breaker_key: Key for circuit breaker
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute_with_retry(
                    func, *args, 
                    circuit_breaker_key=circuit_breaker_key, 
                    **kwargs
                )
            return wrapper
        return decorator


# Global retry handler instance
_retry_handler: Optional[RetryHandler] = None


def get_retry_handler(config: Optional[RetryConfig] = None) -> RetryHandler:
    """Get global retry handler instance."""
    global _retry_handler
    if _retry_handler is None:
        _retry_handler = RetryHandler(config)
    return _retry_handler


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    circuit_breaker_key: Optional[str] = None
):
    """
    Decorator for retry with exponential backoff.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        strategy: Retry strategy
        circuit_breaker_key: Key for circuit breaker
        
    Returns:
        Decorated function
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        strategy=strategy
    )
    
    return get_retry_handler(config).retry(circuit_breaker_key=circuit_breaker_key)


def retry_on_exceptions(
    exceptions: List[type],
    max_attempts: int = 3,
    base_delay: float = 1.0
):
    """
    Decorator for retry on specific exceptions.
    
    Args:
        exceptions: List of exception types to retry on
        max_attempts: Maximum retry attempts
        base_delay: Base delay in seconds
        
    Returns:
        Decorated function
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        retry_on=exceptions
    )
    
    return get_retry_handler(config).retry()
