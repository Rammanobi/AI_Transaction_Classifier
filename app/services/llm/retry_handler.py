from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# We retry on general exceptions. In a real app, we might specifically catch 
# OpenAI API errors, timeouts, or JSON parsing errors.
def with_llm_retries():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
