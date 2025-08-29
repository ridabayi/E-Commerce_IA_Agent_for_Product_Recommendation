from utils.custom_exception import CustomException


def test_custom_exception_str_contains_message():
    err = CustomException("Boom")
    assert "Boom" in str(err)


def test_custom_exception_with_detail():
    try:
        raise ValueError("X")
    except ValueError as e:
        err = CustomException("Boom", e)
    s = str(err)
    assert "Boom" in s and "ValueError" in s
