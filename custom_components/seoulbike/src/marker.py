from urllib.parse import quote


LOW_AVAILABILITY_THRESHOLD = 0.3


def get_availability_marker(availability_ratio):
    if availability_ratio is None:
        return "#9e9e9e"

    if availability_ratio == 0:
        return "#e53935"

    if availability_ratio <= LOW_AVAILABILITY_THRESHOLD:
        return "#fb8c00"

    return "#43a047"


def build_marker_svg(availability_ratio, parking_bike_total_count):

    try:
        parking_bike_total_count = int(parking_bike_total_count or 0)
    except (TypeError, ValueError):
        parking_bike_total_count = 0

    color = get_availability_marker(availability_ratio)

    svg = f"""
    <svg width="72" height="72" viewBox="0 0 72 72"
         xmlns="http://www.w3.org/2000/svg"
         role="img"
         aria-label="parking_bike_total_count {parking_bike_total_count}">
        <circle cx="36" cy="36" r="31"
                fill="{color}"
                stroke="white"
                stroke-width="5"/>
        <text x="36" y="33"
              text-anchor="middle"
              dominant-baseline="middle"
              font-family="Arial, sans-serif"
              font-size="22"
              fill="white">🚲</text>
        <text x="36" y="53"
              text-anchor="middle"
              dominant-baseline="middle"
              font-family="Arial, sans-serif"
              font-size="18"
              font-weight="700"
              fill="white">{parking_bike_total_count}</text>
    </svg>
    """

    return "data:image/svg+xml;charset=utf-8," + quote(svg, safe="")