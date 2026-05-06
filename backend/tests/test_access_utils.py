from bson import ObjectId

from app.utils.access import (
    build_display_name,
    build_object_id_candidates,
    ensure_distinct_ids,
    normalize_active_state,
)


def test_build_display_name_prefers_name_and_last_name():
    name, last_name, fullname = build_display_name(
        {
            "name": "Felix",
            "last_name": "Serrano",
            "fullname": "Legacy Name",
        }
    )

    assert name == "Felix"
    assert last_name == "Serrano"
    assert fullname == "Felix Serrano"


def test_build_display_name_falls_back_to_legacy_fullname():
    assert build_display_name({"fullname": "Legacy Name"}) == ("", "", "Legacy Name")


def test_normalize_active_state_accepts_current_and_legacy_fields():
    assert normalize_active_state({"isActive": False, "estado": True}) is False
    assert normalize_active_state({"estado": False}) is False
    assert normalize_active_state({}) is True


def test_ensure_distinct_ids_trims_and_preserves_order():
    assert ensure_distinct_ids([" a ", "b", "a", "", "c"]) == ["a", "b", "c"]


def test_build_object_id_candidates_includes_string_and_object_id():
    object_id = ObjectId()
    candidates = build_object_id_candidates(str(object_id))

    assert str(object_id) in candidates
    assert object_id in candidates
