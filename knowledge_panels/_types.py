from collections import Counter
from typing import Literal

from openfoodfacts.types import Country, Lang
from pydantic import BaseModel, constr, validator

# Models related to information knowledge panel content


class KnowledgeContentItem(BaseModel):
    value_tag: constr(min_length=3)
    content: constr(min_length=2)
    category_tag: str | None = None


class KnowledgeContentGroup(BaseModel):
    items: list[KnowledgeContentItem]
    tag_type: Literal["labels", "additives", "categories"]
    country: Country
    lang: Lang

    @validator("items")
    def unique_items(cls, v):
        """We check that there is no duplicate items, using as keys:
        value_tag and category tag."""
        count = Counter((item.value_tag, item.category_tag) for item in v)
        most_common = count.most_common(1)
        if most_common and most_common[0][1] > 1:
            raise ValueError(f"more than 1 item with fields={most_common[0][0]}")
        return v


class KnowledgeContent(BaseModel):
    groups: list[KnowledgeContentGroup]
