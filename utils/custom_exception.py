import sys


class CustomException(Exception):
    def __init__(self, message: str, error_detail: Exception | None = None) -> None:
        self.error_message = self.get_detailed_error_message(message, error_detail)
        super().__init__(self.error_message)

    @staticmethod
    def get_detailed_error_message(message: str, error_detail: Exception | None) -> str:
        _, _, exc_tb = sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb else "Unknown File"
        line_number = exc_tb.tb_lineno if exc_tb else "Unknown Line"

        if error_detail is not None:
            etype = type(error_detail).__name__
            edesc = f"{etype}: {error_detail}"
        else:
            edesc = "None"

        return f"{message} | Error: {edesc} | File: {file_name} | Line: {line_number}"

    def __str__(self) -> str:
        return self.error_message
