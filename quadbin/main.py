from .tilecover import get_tiles
from .utils import (
    clip_latitude,
    clip_longitude,
    point_to_tile,
    tile_to_longitude,
    tile_to_latitude,
)

HEADER = 0x4000000000000000
FOOTER = 0xFFFFFFFFFFFFF
B = [
    0x5555555555555555,
    0x3333333333333333,
    0x0F0F0F0F0F0F0F0F,
    0x00FF00FF00FF00FF,
    0x0000FFFF0000FFFF,
    0x00000000FFFFFFFF,
]
S = [1, 2, 4, 8, 16]


def is_valid_index(index):
    """Return True if this is a valid Quadbin index.

    Parameters
    ----------
    index : int

    Returns
    -------
    bool
    """
    header = HEADER
    mode = (index >> 59) & 7
    resolution = (index >> 52) & 0x1F
    unused = FOOTER >> (resolution << 2)
    return (
        index >= 0
        and (index & header == header)
        and mode in [0, 1, 2, 3, 4, 5, 6]
        and resolution >= 0
        and resolution <= 26
        and (index & unused == unused)
    )


def is_valid_cell(cell):
    """Return True if this is a valid Quadbin cell (mode 1).

    Parameters
    ----------
    index : int

    Returns
    -------
    bool
    """
    header = HEADER
    mode = (cell >> 59) & 7
    resolution = (cell >> 52) & 0x1F
    unused = FOOTER >> (resolution << 2)
    return (
        cell >= 0
        and (cell & header == header)
        and mode == 1
        and resolution >= 0
        and resolution <= 26
        and (cell & unused == unused)
    )


def cell_to_tile(cell):
    # type: (int) -> str
    """Convert a cell into a tile.

    Parameters
    ----------
    cell : int

    Returns
    -------
    tile: tuple (x, y, z)
    """
    # mode = (cell >> 59) & 7
    # extra = (cell >> 57) & 3
    z = cell >> 52 & 31
    q = (cell & FOOTER) << 12
    x = q
    y = q >> 1

    x = x & B[0]
    y = y & B[0]

    x = (x | (x >> S[0])) & B[1]
    y = (y | (y >> S[0])) & B[1]

    x = (x | (x >> S[1])) & B[2]
    y = (y | (y >> S[1])) & B[2]

    x = (x | (x >> S[2])) & B[3]
    y = (y | (y >> S[2])) & B[3]

    x = (x | (x >> S[3])) & B[4]
    y = (y | (y >> S[3])) & B[4]

    x = (x | (x >> S[4])) & B[5]
    y = (y | (y >> S[4])) & B[5]

    x = x >> (32 - z)
    y = y >> (32 - z)

    return (x, y, z)


def tile_to_cell(tile):
    """Convert a tile into a cell.

    Parameters
    ----------
    tile : tuple (x, y, z)

    Returns
    -------
    int
    """
    x, y, z = tile

    x = x << (32 - z)
    y = y << (32 - z)

    x = (x | (x << S[4])) & B[4]
    y = (y | (y << S[4])) & B[4]

    x = (x | (x << S[3])) & B[3]
    y = (y | (y << S[3])) & B[3]

    x = (x | (x << S[2])) & B[2]
    y = (y | (y << S[2])) & B[2]

    x = (x | (x << S[1])) & B[1]
    y = (y | (y << S[1])) & B[1]

    x = (x | (x << S[0])) & B[0]
    y = (y | (y << S[0])) & B[0]

    # -- | (mode << 59) | (mode_dep << 57)
    return HEADER | (1 << 59) | (z << 52) | ((x | (y << 1)) >> 12) | (FOOTER >> (z * 2))


def cell_to_point(cell, geojson=False):
    """Convert a cell into a geographic point.

    Parameters
    ----------
    cell : int
    geojson : bool, optional
        Return the point as a GeoJSON geometry, by default False.

    Returns
    -------
    str
        if geojson is True.
    list
        if geojson is False (default).
    """
    tile = cell_to_tile(cell)

    longitude = tile_to_longitude(tile, 0.5)
    latitude = tile_to_latitude(tile, 0.5)

    if geojson:
        return '{{"type": "Point", "coordinates": {0}}}'.format([longitude, latitude])
    else:
        return [longitude, latitude]


def point_to_cell(longitude, latitude, resolution):
    """Convert a geographic point into a cell.

    Parameters
    ----------
    longitude : float
        Longitude in decimal degrees.
    latitude : float
        Latitude in decimal degrees.
    resolution : int
        The resolution of the cell.

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If the resolution is out of bounds.
    """
    if resolution < 0 or resolution > 26:
        raise ValueError("Invalid resolution: should be between 0 and 26")

    longitude = clip_longitude(longitude)
    latitude = clip_latitude(latitude)

    tile = point_to_tile(longitude, latitude, resolution)

    return tile_to_cell(tile)


def cell_to_boundary(cell, geojson=False):
    """Convert a cell into a geographic polygon.

    Parameters
    ----------
    cell : int
    geojson : bool, optional
        Return the polygon as a GeoJSON geometry, by default False.

    Returns
    -------
    str
        if geojson is True.
    list
        if geojson is False (default).
    """
    bbox = cell_to_bounding_box(cell)

    boundary = [
        [bbox[0], bbox[3]],
        [bbox[0], bbox[1]],
        [bbox[2], bbox[1]],
        [bbox[2], bbox[3]],
        [bbox[0], bbox[3]],
    ]

    if geojson:
        return '{{"type": "Polygon", "coordinates": [{0}]}}'.format(boundary)
    else:
        return boundary


def cell_to_bounding_box(cell):
    """Conver a cell into a geographic bounding box.

    Parameters
    ----------
    cell : int

    Returns
    -------
    list
        Bounding box in degrees [xmin, ymin, xmax, ymax]
    """
    tile = cell_to_tile(cell)

    xmin = tile_to_longitude(tile, 0)
    xmax = tile_to_longitude(tile, 1)
    ymin = tile_to_latitude(tile, 1)
    ymax = tile_to_latitude(tile, 0)

    return [xmin, ymin, xmax, ymax]


def get_resolution(index):
    """Get the resolution of an index.

    Parameters
    ----------
    index : int

    Returns
    -------
    int
    """
    return (index >> 52) & 0x1F


def index_to_string(index):
    """Convert an index into its string representation.

    Parameters
    ----------
    index : int

    Returns
    -------
    str
        The hexadecimal representation of the input decimal integer.
    """
    return hex(index)[2:]


def string_to_index(index):
    """Convert an index into its numeric representation.

    Parameters
    ----------
    index : str

    Returns
    -------
    int
        The decimal representation of the input hexadecimal string.
    """
    return int(index, base=16)


def k_ring(origin, k):
    """Compute the indices within k distance of the origin index.

    Parameters
    ----------
    origin : int
        Origin index.
    k : int
        Distance of the ring.

    Returns
    -------
    list
        Indices in the k-ring.
    """
    # TODO: review code

    corner_quadbin = origin
    # Traverse to top left corner
    for i in range(0, k):
        corner_quadbin = cell_sibling(corner_quadbin, "left")
        corner_quadbin = cell_sibling(corner_quadbin, "up")

    neighbors = []
    traversal_quadbin = 0

    for j in range(0, k * 2 + 1):
        traversal_quadbin = corner_quadbin
        for i in range(0, k * 2 + 1):
            neighbors.append(traversal_quadbin)
            traversal_quadbin = cell_sibling(traversal_quadbin, "right")
        corner_quadbin = cell_sibling(corner_quadbin, "down")

    return neighbors


def k_ring_distances(origin, k):
    """Compute the indices and distances within k distance of the origin index.

    Parameters
    ----------
    origin : int
        Origin index.
    k : int
        Distance of the ring.

    Returns
    -------
    list
        Objects with the index and distance in the k-ring.
    """
    # TODO: review code

    corner_quadbin = origin
    # Traverse to top left corner
    for i in range(0, k):
        corner_quadbin = cell_sibling(corner_quadbin, "left")
        corner_quadbin = cell_sibling(corner_quadbin, "up")

    neighbors = []
    traversal_quadbin = 0

    for j in range(0, k * 2 + 1):
        traversal_quadbin = corner_quadbin
        for i in range(0, k * 2 + 1):
            neighbors.append(
                {
                    "index": traversal_quadbin,
                    "distance": max(abs(i - k), abs(j - k)),  # Chebyshev distance
                }
            )
            traversal_quadbin = cell_sibling(traversal_quadbin, "right")
        corner_quadbin = cell_sibling(corner_quadbin, "down")

    return neighbors


def cell_sibling(cell, direction):
    """Compute the sibling in a specific direction.

    Parameters
    ----------
    cell : int
    direction : str
        Location of the sibling: "left", "right", "up", "down".

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If a wrong direction is passed.
    """
    # TODO: review code

    direction = direction.lower()
    if direction not in ["left", "right", "up", "down"]:
        raise ValueError("Wrong direction argument passed to sibling")

    x, y, z = cell_to_tile(cell)
    if z == 0:
        return None
    tiles_per_level = 2 << (z - 1)
    if direction == "left":
        if x > 0:
            x = x - 1
        else:
            return None

    if direction == "right":
        if x < tiles_per_level - 1:
            x = x + 1
        else:
            return None

    if direction == "up":
        if y > 0:
            y = y - 1
        else:
            return None

    if direction == "down":
        if y < tiles_per_level - 1:
            y = y + 1
        else:
            return None

    return tile_to_cell((x, y, z))


def cell_to_parent(cell, parent_resolution):
    """Compute the parent cell for a specific resolution.

    Parameters
    ----------
    cell : int
    parent_resolution : int

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If the parent resolution is not valid.
    """
    resolution = get_resolution(cell)
    if parent_resolution < 0 or parent_resolution > resolution:
        raise ValueError("Invalid resolution")
    return (
        (cell & ~(0x1F << 52))
        | (parent_resolution << 52)
        | (FOOTER >> (parent_resolution << 2))
    )


def cell_to_children(cell, children_resolution):
    """Compute the children cells for a specific resolution.

    Parameters
    ----------
    cell : int
    children_resolution : int

    Returns
    -------
    list
        Children cells.

    Raises
    ------
    ValueError
        If the children resolution is not valid.
    """
    # TODO: review code

    x, y, z = cell_to_tile(cell)
    if children_resolution < 0 or children_resolution > 26 or children_resolution <= z:
        raise ValueError("Invalid resolution")

    diff_z = children_resolution - z
    mask = (1 << diff_z) - 1
    min_tile_x = x << diff_z
    max_tile_x = min_tile_x | mask
    min_tile_y = y << diff_z
    max_tile_y = min_tile_y | mask
    children = []
    for x in range(min_tile_x, max_tile_x + 1):
        for y in range(min_tile_y, max_tile_y + 1):
            children.append(tile_to_cell((children_resolution, x, y)))
    return children


def geometry_to_cells(geometry, resolution):
    """Compute the cells that fill an input geometry.

    Parameters
    ----------
    geometry : str
        Input geometry as GeoJSON.
    resolution : int
        The resolution of the cells.

    Returns
    -------
    list
        Cells intersecting the geometry.
    """
    # TODO: GeometryCollection

    return [
        tile_to_cell((int(tile[0]), int(tile[1]), int(tile[2])))
        for tile in get_tiles(geometry, resolution)
    ]
