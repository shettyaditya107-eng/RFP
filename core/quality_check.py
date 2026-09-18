
def validate_requirements(records, page_count):
    cleaned = []
    seen = set()
    for item in records:
        required = ["business_area","requirement_group","capability",
                    "requirement","page_number","source_excerpt","confidence"]
        if not all(str(item.get(k, "")).strip() for k in required):
            continue
        page = int(item["page_number"])
        if not 1 <= page <= page_count:
            continue
        key = (item["business_area"], item["capability"], item["requirement"], page)
        if key in seen:
            continue
        seen.add(key)
        item["confidence"] = max(0.0, min(1.0, float(item["confidence"])))
        item["page_number"] = page
        cleaned.append(item)
    return cleaned
