from urllib.parse import quote


LOW_BIKE_THRESHOLD = 3


def get_availability_marker(bikes):
    try:
        bikes = int(bikes or 0)
    except (TypeError, ValueError):
        bikes = 0

    if bikes == 0:
        return "#e53935", "empty"

    if bikes <= LOW_BIKE_THRESHOLD:
        return "#fb8c00", "low"

    return "#43a047", "available"


def build_marker_svg(bikes):
    try:
        bikes = int(bikes or 0)
    except (TypeError, ValueError):
        bikes = 0

    color, availability = get_availability_marker(bikes)

    svg = f'''<svg width="72" height="72" viewBox="0 0 72 72" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{availability} bikes {bikes}">
<circle cx="36" cy="36" r="31" fill="{color}" stroke="white" stroke-width="5"/>
<text x="36" y="33" text-anchor="middle" dominant-baseline="middle" font-family="Arial, sans-serif" font-size="22" fill="white">🚲</text>
<text x="36" y="53" text-anchor="middle" dominant-baseline="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="white">{bikes}</text>
</svg>'''

    return "data:image/svg+xml;charset=utf-8," + quote(svg, safe="")
