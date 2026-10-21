"""Unit tests for the merchant_detail / merchant_social_link REST mappers. The proto already carries `%Y-%m-%d %H:%M:%S.mmm` strings, so the mapper passes timestamps through unchanged. `social_media_links` is built from the proto list (empty -> `None`, i.e. JSON `null`); `deleted_at` renders `""` when no wrapper is attached. The social command mapper copies only id/merchant_detail_id/platform/url, so the REST `created_at`/`updated_at` stay `""` (struct serialises the zero strings even though the proto carries values)."""

from __future__ import annotations

from pb.merchant_detail import merchant_detail_common_pb2
from pb.merchant_social_link import merchant_social_link_common_pb2
from shared.mapper.merchant_detail import (
    map_merchant_detail_response,
    map_merchant_detail_response_delete_at,
    map_merchant_detail_response_relation,
    map_merchant_social_media_link,
    map_pagination_meta,
    to_api_response_merchant_detail,
    to_api_response_merchant_detail_relation,
    to_api_response_pagination_merchant_detail,
    to_api_response_pagination_merchant_detail_delete_at,
)
from shared.mapper.merchant_social_link import to_api_response_merchant_social_link


def _proto_detail(**overrides):
    values = {
        "id": 7,
        "merchant_id": 20,
        "display_name": "Techno Store",
        "cover_image_url": "cover/techno.jpg",
        "logo_url": "logo/techno.png",
        "short_description": "desc",
        "website_url": "https://technostore.com",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
    }
    values.update(overrides)
    return merchant_detail_common_pb2.MerchantDetailResponse(**values)


def test_detail_proto_mapping_passes_strings_through() -> None:
    message = merchant_detail_common_pb2.ApiResponseMerchantDetail(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_detail())
    dumped = to_api_response_merchant_detail(message).model_dump()
    assert dumped["data"] == {
        "id": 7,
        "merchant_id": 20,
        "display_name": "Techno Store",
        "cover_image_url": "cover/techno.jpg",
        "logo_url": "logo/techno.png",
        "short_description": "desc",
        "website_url": "https://technostore.com",
        "created_at": "2026-05-06 01:02:03.000",
        "updated_at": "2026-05-07 04:05:06.000",
        "social_media_links": None,
    }


def test_detail_plain_mapper_always_has_nil_links() -> None:
    proto = _proto_detail()
    proto.social_media_links.add(id=1, platform="Facebook", url="https://fb.com/x")
    # never reads the links list.
    assert map_merchant_detail_response(proto).social_media_links is None


def test_detail_relation_mapper_builds_links_and_empty_is_none() -> None:
    proto = _proto_detail()
    assert map_merchant_detail_response_relation(proto).social_media_links is None

    proto.social_media_links.add(id=1, platform="Facebook", url="https://fb.com/x")
    proto.social_media_links.add(id=2, platform="Twitter", url="https://tw.com/x")
    links = map_merchant_detail_response_relation(proto).social_media_links
    assert links is not None
    assert len(links) == 2
    assert links[0].platform == "Facebook"
    assert links[1].url == "https://tw.com/x"


def test_map_merchant_social_media_link() -> None:
    link = map_merchant_social_media_link(
        merchant_detail_common_pb2.MerchantSocialMediaLinkResponse(
            id=3, platform="Instagram", url="https://ig.com/x"
        )
    )
    assert (link.id, link.platform, link.url) == (3, "Instagram", "https://ig.com/x")


def test_detail_delete_at_missing_renders_empty_and_present_passes_through() -> None:
    proto = merchant_detail_common_pb2.MerchantDetailResponseDeleteAt(id=1, merchant_id=2)
    assert map_merchant_detail_response_delete_at(proto).deleted_at == ""

    proto.deleted_at.value = "2026-02-03 00:00:00.000"
    assert map_merchant_detail_response_delete_at(proto).deleted_at == (
        "2026-02-03 00:00:00.000"
    )


def test_detail_relation_api_response() -> None:
    message = merchant_detail_common_pb2.ApiResponseMerchantDetail(
        status="success", message="ok"
    )
    message.data.CopyFrom(_proto_detail())
    message.data.social_media_links.add(id=1, platform="Facebook", url="https://fb.com/x")
    dumped = to_api_response_merchant_detail_relation(message).model_dump()
    assert dumped["data"]["social_media_links"] == [
        {"id": 1, "platform": "Facebook", "url": "https://fb.com/x"}
    ]


def test_detail_pagination_mapping() -> None:
    message = merchant_detail_common_pb2.ApiResponsePaginationMerchantDetail(
        status="success", message="ok"
    )
    message.data.add(id=1, merchant_id=2, display_name="N")
    message.pagination.current_page = 2
    message.pagination.page_size = 5
    message.pagination.total_pages = 3
    message.pagination.total_records = 11
    dumped = to_api_response_pagination_merchant_detail(message).model_dump()
    assert dumped["data"][0]["id"] == 1
    assert dumped["pagination"] == {
        "current_page": 2,
        "page_size": 5,
        "total_pages": 3,
        "total_records": 11,
    }


def test_detail_trashed_pagination_delete_at() -> None:
    message = merchant_detail_common_pb2.ApiResponsePaginationMerchantDetailDeleteAt(
        status="success", message="ok"
    )
    message.data.add(id=9, merchant_id=2, display_name="N")
    message.data[0].deleted_at.value = "2026-02-03 00:00:00.000"
    dumped = to_api_response_pagination_merchant_detail_delete_at(message).model_dump()
    assert dumped["data"][0]["deleted_at"] == "2026-02-03 00:00:00.000"


def test_social_link_api_response_drops_timestamps_to_empty() -> None:
    message = merchant_social_link_common_pb2.ApiResponseMerchantSocial(
        status="success", message="ok"
    )
    message.data.id = 5
    message.data.merchant_detail_id = 1
    message.data.platform = "Facebook"
    message.data.url = "https://facebook.com/merchant1"
    message.data.created_at = "2026-05-06 01:02:03.000"
    message.data.updated_at = "2026-05-07 04:05:06.000"
    dumped = to_api_response_merchant_social_link(message).model_dump()
    assert dumped == {
        "status": "success",
        "message": "ok",
        "data": {
            "id": 5,
            "merchant_detail_id": 1,
            "platform": "Facebook",
            "url": "https://facebook.com/merchant1",
            "created_at": "",
            "updated_at": "",
        },
    }


def test_map_pagination_meta_none_defaults() -> None:
    meta = map_pagination_meta(None)
    assert meta.current_page == 1
    assert meta.total_records == 0


__all__ = []
