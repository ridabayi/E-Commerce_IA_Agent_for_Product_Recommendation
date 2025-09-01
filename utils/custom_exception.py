import sys


class CustomException(Exception):
    def __init__(self, message: str, error_detail: Exception | None = None):
        self.error_message = self._format_message(message, error_detail)
        super().__init__(self.error_message)

    @staticmethod
    def _format_message(message: str, error_detail: Exception | None) -> str:
        _, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown File"
        line_number_str = str(exc_tb.tb_lineno) if exc_tb else "Unknown Line"
        detail = f"{type(error_detail).__name__}: {error_detail}" if error_detail else "N/A"
        return f"{message} | Detail: {detail} | File: {file_name} | Line: {line_number_str}"

    def __str__(self) -> str:
        return self.error_message
