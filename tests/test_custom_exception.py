from utils.custom_exception import CustomException


def test_custom_exception_includes_type_and_message():
    try:
        raise ValueError("X")
    except ValueError as e:
        err = CustomException("Boom", e)
    s = str(err)
    assert "Boom" in s and "ValueError" in s and "X" in s
