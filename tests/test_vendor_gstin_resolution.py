from app.vendor_resolution import normalize_vendor_name


def test_vendor_name_normalization():

    assert normalize_vendor_name(
        " ABC Technologies "
    ) == "abc technologies"

    assert normalize_vendor_name(
        "ABC   Technologies"
    ) == "abc technologies"


def test_vendor_name_case_insensitive():

    assert normalize_vendor_name(
        "MICROSOFT"
    ) == normalize_vendor_name(
        "Microsoft"
    )


def test_empty_vendor_name():

    assert normalize_vendor_name("") == ""

    assert normalize_vendor_name(None) == ""