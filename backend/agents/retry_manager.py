"""
Retry Manager - Intelligent retry with error classification
Simple, practical, no BS
"""
import asyncio
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import re


class RetryManager:
    """Smart retry with error classification - gets shit done"""

    # Error patterns and how to handle them
    ERROR_STRATEGIES = {
        'timeout': {
            'pattern': r'timeout|timed out|connection timeout',
            'max_retries': 3,
            'backoff': 'exponential',
            'base_delay': 2
        },
        'rate_limit': {
            'pattern': r'rate limit|too many requests|429',
            'max_retries': 5,
            'backoff': 'exponential',
            'base_delay': 10
        },
        'network': {
            'pattern': r'network|connection refused|connection reset|dns',
            'max_retries': 3,
            'backoff': 'exponential',
            'base_delay': 1
        },
        'syntax_error': {
            'pattern': r'syntaxerror|unexpected token|parse error',
            'max_retries': 2,
            'backoff': 'immediate',
            'base_delay': 0
        },
        'type_error': {
            'pattern': r'typeerror|cannot read property|undefined',
            'max_retries': 2,
            'backoff': 'immediate',
            'base_delay': 0
        },
        'api_error': {
            'pattern': r'api error|invalid api key|unauthorized|401|403',
            'max_retries': 0,  # No retry - needs config fix
            'backoff': 'none',
            'escalate': True
        },
        'not_found': {
            'pattern': r'not found|404|enoent|no such file',
            'max_retries': 1,
            'backoff': 'immediate',
            'base_delay': 0
        }
    }

    def classify_error(self, error: Exception) -> str:
        """Figure out what kind of error this is"""
        error_str = str(error).lower()

        for error_type, config in self.ERROR_STRATEGIES.items():
            if re.search(config['pattern'], error_str, re.IGNORECASE):
                return error_type

        return 'unknown'

    def get_retry_config(self, error_type: str) -> Dict:
        """Get retry strategy for error type"""
        return self.ERROR_STRATEGIES.get(error_type, {
            'max_retries': 2,
            'backoff': 'exponential',
            'base_delay': 1
        })

    async def calculate_delay(self, error_type: str, attempt: int) -> float:
        """Calculate wait time before retry"""
        config = self.get_retry_config(error_type)
        base_delay = config['base_delay']
        backoff_type = config['backoff']

        if backoff_type == 'none' or backoff_type == 'immediate':
            return 0

        elif backoff_type == 'exponential':
            # 2^attempt * base_delay (1s, 2s, 4s, 8s...)
            return (2 ** attempt) * base_delay

        elif backoff_type == 'fixed':
            return base_delay

        return 1  # Default 1s

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        task_context: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute function with intelligent retry

        Returns:
            {
                'success': bool,
                'result': Any,
                'error': str | None,
                'attempts': int,
                'should_escalate': bool
            }
        """
        attempts = 0
        last_error = None
        error_type = None

        while True:
            attempts += 1

            try:
                # Try the thing
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

                print(f"✅ Success on attempt {attempts}")

                return {
                    'success': True,
                    'result': result,
                    'error': None,
                    'attempts': attempts,
                    'should_escalate': False
                }

            except Exception as e:
                last_error = e
                error_type = self.classify_error(e)
                config = self.get_retry_config(error_type)

                print(f"⚠️ Attempt {attempts} failed: {error_type} - {str(e)[:100]}")

                # Check if should escalate immediately
                if config.get('escalate', False):
                    print(f"🚨 Error requires escalation: {error_type}")
                    return {
                        'success': False,
                        'result': None,
                        'error': str(e),
                        'error_type': error_type,
                        'attempts': attempts,
                        'should_escalate': True,
                        'escalation_reason': f'{error_type}: {str(e)}'
                    }

                # Check if exceeded max retries
                if attempts >= config['max_retries']:
                    print(f"❌ Max retries ({config['max_retries']}) exceeded for {error_type}")
                    return {
                        'success': False,
                        'result': None,
                        'error': str(e),
                        'error_type': error_type,
                        'attempts': attempts,
                        'should_escalate': attempts >= 3,  # Escalate after 3 tries
                        'escalation_reason': f'Failed after {attempts} attempts: {str(e)}'
                    }

                # Calculate backoff and retry
                delay = await self.calculate_delay(error_type, attempts)

                if delay > 0:
                    print(f"⏳ Retrying in {delay}s... (attempt {attempts + 1}/{config['max_retries']})")
                    await asyncio.sleep(delay)
                else:
                    print(f"🔄 Immediate retry (attempt {attempts + 1}/{config['max_retries']})")

    def should_regenerate_with_error_context(self, error_type: str) -> bool:
        """
        For code errors, should we try regenerating with error in prompt?
        """
        return error_type in ['syntax_error', 'type_error', 'not_found']

    def create_fix_prompt(self, original_prompt: str, error: str, error_type: str) -> str:
        """
        Create enhanced prompt with error context for regeneration
        """
        return f"""
{original_prompt}

⚠️ PREVIOUS ATTEMPT FAILED:

Error Type: {error_type}
Error Message: {error}

INSTRUCTIONS:
1. Analyze the error above
2. Identify what went wrong
3. Fix the issue in your regenerated code
4. Ensure this specific error doesn't happen again

Generate the corrected version now.
"""


# Global singleton
_retry_manager = None


def get_retry_manager() -> RetryManager:
    """Get or create global retry manager"""
    global _retry_manager
    if _retry_manager is None:
        _retry_manager = RetryManager()
    return _retry_manager
