import pytest
import quadbin


@pytest.mark.parametrize(
    "index,expected",
    [
        (0, False),
        (5209574053332910078, False),
        (6362495557939757055, True),
        (5209574053332910079, True),
    ],
)
def test_is_valid_index(index, expected):
    assert quadbin.is_valid_index(index) is expected


@pytest.mark.parametrize(
    "index,expected",
    [
        (0, False),
        (5209574053332910078, False),
        (6362495557939757055, False),
        (5209574053332910079, True),
    ],
)
def test_is_valid_cell(index, expected):
    assert quadbin.is_valid_cell(index) is expected


def test_cell_to_tile():
    tile = (9, 8, 4)
    assert quadbin.cell_to_tile(5209574053332910079) == tile


def test_tile_to_cell():
    tile = (9, 8, 4)
    assert quadbin.tile_to_cell(tile) == 5209574053332910079


def test_cell_to_point():
    coordinates = [33.75, -11.178401873711776]
    assert quadbin.cell_to_point(5209574053332910079) == coordinates
    assert quadbin.cell_to_point(
        5209574053332910079, geojson=True
    ) == '{{"type": "Point", "coordinates": {0}}}'.format(coordinates)


def test_point_to_cell():
    assert quadbin.point_to_cell(33.75, -11.178401873711776, 4) == 5209574053332910079
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.point_to_cell(33.75, -11.178401873711776, -1)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.point_to_cell(33.75, -11.178401873711776, 27)


def test_cell_to_boundary():
    coordinates = [
        [22.5, 0.0],
        [22.5, -21.943045533438166],
        [45.0, -21.943045533438166],
        [45.0, 0.0],
        [22.5, 0.0],
    ]
    assert quadbin.cell_to_boundary(5209574053332910079) == coordinates
    assert quadbin.cell_to_boundary(
        5209574053332910079, geojson=True
    ) == '{{"type": "Polygon", "coordinates": [{0}]}}'.format(coordinates)


def test_cell_to_bounding_box():
    assert quadbin.cell_to_bounding_box(5209574053332910079) == [
        22.5,
        -21.943045533438166,
        45.0,
        0.0,
    ]
    bbox = quadbin.cell_to_bounding_box(5211632339100106751)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]
    bbox = quadbin.cell_to_bounding_box(5212472365983727615)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]
    bbox = quadbin.cell_to_bounding_box(5226055182877458431)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]
    bbox = quadbin.cell_to_bounding_box(5264708239044902911)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]


def test_get_resolution():
    assert quadbin.get_resolution(5209574053332910079) == 4


def test_index_to_string():
    assert quadbin.index_to_string(5209574053332910079) == "484c1fffffffffff"


def test_string_to_index():
    assert quadbin.string_to_index("484c1fffffffffff") == 5209574053332910079


def test_k_ring():
    assert quadbin.k_ring(5209574053332910079, 0) == [
        5209574053332910079,
    ]
    assert quadbin.k_ring(5209574053332910079, 1) == [
        5208043533147045887,
        5208061125333090303,
        5208113901891223551,
        5209556461146865663,
        5209574053332910079,
        5209626829891043327,
        5209591645518954495,
        5209609237704998911,
        5209662014263132159,
    ]
    assert quadbin.k_ring(5209574053332910079, 2) == [
        5207251884775047167,
        5208008348774957055,
        5208025940961001471,
        5208078717519134719,
        5208096309705179135,
        5207287069147135999,
        5208043533147045887,
        5208061125333090303,
        5208113901891223551,
        5208131494077267967,
        5208799997146955775,
        5209556461146865663,
        5209574053332910079,
        5209626829891043327,
        5209644422077087743,
        5208835181519044607,
        5209591645518954495,
        5209609237704998911,
        5209662014263132159,
        5209679606449176575,
        5208940734635311103,
        5209697198635220991,
        5209714790821265407,
        5209767567379398655,
        5209785159565443071,
    ]
    with pytest.raises(ValueError, match="Invalid negative distance"):
        assert quadbin.k_ring(5209574053332910079, -1)


def test_k_ring_distances():
    assert quadbin.k_ring_distances(5209574053332910079, 0) == [
        {"distance": 0, "index": 5209574053332910079},
    ]
    assert quadbin.k_ring_distances(5209574053332910079, 1) == [
        {"distance": 1, "index": 5208043533147045887},
        {"distance": 1, "index": 5208061125333090303},
        {"distance": 1, "index": 5208113901891223551},
        {"distance": 1, "index": 5209556461146865663},
        {"distance": 0, "index": 5209574053332910079},
        {"distance": 1, "index": 5209626829891043327},
        {"distance": 1, "index": 5209591645518954495},
        {"distance": 1, "index": 5209609237704998911},
        {"distance": 1, "index": 5209662014263132159},
    ]
    assert quadbin.k_ring_distances(5209574053332910079, 2) == [
        {"distance": 2, "index": 5207251884775047167},
        {"distance": 2, "index": 5208008348774957055},
        {"distance": 2, "index": 5208025940961001471},
        {"distance": 2, "index": 5208078717519134719},
        {"distance": 2, "index": 5208096309705179135},
        {"distance": 2, "index": 5207287069147135999},
        {"distance": 1, "index": 5208043533147045887},
        {"distance": 1, "index": 5208061125333090303},
        {"distance": 1, "index": 5208113901891223551},
        {"distance": 2, "index": 5208131494077267967},
        {"distance": 2, "index": 5208799997146955775},
        {"distance": 1, "index": 5209556461146865663},
        {"distance": 0, "index": 5209574053332910079},
        {"distance": 1, "index": 5209626829891043327},
        {"distance": 2, "index": 5209644422077087743},
        {"distance": 2, "index": 5208835181519044607},
        {"distance": 1, "index": 5209591645518954495},
        {"distance": 1, "index": 5209609237704998911},
        {"distance": 1, "index": 5209662014263132159},
        {"distance": 2, "index": 5209679606449176575},
        {"distance": 2, "index": 5208940734635311103},
        {"distance": 2, "index": 5209697198635220991},
        {"distance": 2, "index": 5209714790821265407},
        {"distance": 2, "index": 5209767567379398655},
        {"distance": 2, "index": 5209785159565443071},
    ]
    with pytest.raises(ValueError, match="Invalid negative distance"):
        assert quadbin.k_ring_distances(5209574053332910079, -1)


def test_cell_sibling():
    # Res 0
    assert quadbin.cell_sibling(5192650370358181887, "up") is None
    assert quadbin.cell_sibling(5193776270265024511, "up") is None
    # Res 1
    assert quadbin.cell_sibling(5193776270265024511, "left") is None
    assert quadbin.cell_sibling(5193776270265024511, "down") == 5196028070078709759
    assert quadbin.cell_sibling(5193776270265024511, "right") == 5194902170171867135
    assert quadbin.cell_sibling(5194902170171867135, "up") is None
    assert quadbin.cell_sibling(5194902170171867135, "right") is None
    assert quadbin.cell_sibling(5194902170171867135, "down") == 5197153969985552383
    assert quadbin.cell_sibling(5194902170171867135, "left") == 5193776270265024511
    assert quadbin.cell_sibling(5209574053332910079, "up") == 5208061125333090303
    # Res 4
    assert quadbin.cell_sibling(5209574053332910079, "down") == 5209609237704998911
    assert quadbin.cell_sibling(5209574053332910079, "left") == 5209556461146865663
    assert quadbin.cell_sibling(5209574053332910079, "right") == 5209626829891043327
    with pytest.raises(ValueError, match="Wrong direction argument passed to sibling"):
        assert quadbin.cell_sibling(5209574053332910079, "wrong")


def test_cell_to_parent():
    assert quadbin.cell_to_parent(5209574053332910079, 4) == 5209574053332910079
    assert quadbin.cell_to_parent(5209574053332910079, 2) == 5200813144682790911
    assert quadbin.cell_to_parent(5209574053332910079, 0) == 5192650370358181887
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_parent(5209574053332910079, 5)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_parent(5209574053332910079, -1)

def test_cell_to_parent_and_cell_to_tile_reversibility():
    for cell, res in ((5203557525705719807, 2), (5221564502511714303, 5), (5263677313026883583, 13)):
        parent_cell = quadbin.cell_to_parent(cell, res)
        parent_tile = quadbin.cell_to_tile(parent_cell)
        assert quadbin.tile_to_cell(parent_tile) == parent_cell

def test_cell_to_children():
    assert sorted(quadbin.cell_to_children(5192650370358181887, 1)) == sorted(
        [
            5193776270265024511,
            5196028070078709759,
            5194902170171867135,
            5197153969985552383,
        ]
    )
    assert sorted(quadbin.cell_to_children(5209574053332910079, 5)) == sorted(
        [
            5214064458820747263,
            5214073254913769471,
            5214068856867258367,
            5214077652960280575,
        ]
    )
    assert sorted(quadbin.main.cell_to_children(5209574053332910079, 6)) == sorted(
        [
            5218564759913234431,
            5218565859424862207,
            5218566958936489983,
            5218568058448117759,
            5218569157959745535,
            5218570257471373311,
            5218571356983001087,
            5218572456494628863,
            5218573556006256639,
            5218574655517884415,
            5218575755029512191,
            5218576854541139967,
            5218577954052767743,
            5218579053564395519,
            5218580153076023295,
            5218581252587651071,
        ]
    )
    assert sorted(quadbin.main.cell_to_children(5209574053332910079, 7)) == sorted(
        [
            5223067534906884095,
            5223067809784791039,
            5223068084662697983,
            5223068359540604927,
            5223068634418511871,
            5223068909296418815,
            5223069184174325759,
            5223069459052232703,
            5223069733930139647,
            5223070008808046591,
            5223070283685953535,
            5223070558563860479,
            5223070833441767423,
            5223071108319674367,
            5223071383197581311,
            5223071658075488255,
            5223071932953395199,
            5223072207831302143,
            5223072482709209087,
            5223072757587116031,
            5223073032465022975,
            5223073307342929919,
            5223073582220836863,
            5223073857098743807,
            5223074131976650751,
            5223074406854557695,
            5223074681732464639,
            5223074956610371583,
            5223075231488278527,
            5223075506366185471,
            5223075781244092415,
            5223076056121999359,
            5223076330999906303,
            5223076605877813247,
            5223076880755720191,
            5223077155633627135,
            5223077430511534079,
            5223077705389441023,
            5223077980267347967,
            5223078255145254911,
            5223078530023161855,
            5223078804901068799,
            5223079079778975743,
            5223079354656882687,
            5223079629534789631,
            5223079904412696575,
            5223080179290603519,
            5223080454168510463,
            5223080729046417407,
            5223081003924324351,
            5223081278802231295,
            5223081553680138239,
            5223081828558045183,
            5223082103435952127,
            5223082378313859071,
            5223082653191766015,
            5223082928069672959,
            5223083202947579903,
            5223083477825486847,
            5223083752703393791,
            5223084027581300735,
            5223084302459207679,
            5223084577337114623,
            5223084852215021567,
        ]
    )
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, 27)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, 4)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, -1)


def test_geometry_to_cells_point():
    coordinates = [-3.71219873428345, 40.413365349070865]
    geometry = '{{"type":"Point","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert quadbin.geometry_to_cells(geometry, 17) == [5265786693163941887]
    assert quadbin.geometry_to_cells(geometry, 26) == [5306319089810035706]


def test_geometry_to_cells_multipoint():
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
    ]
    geometry = '{{"type":"MultiPoint","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693153193983,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 26)) == sorted(
        [
            5306319089810035706,
            5306319089799501962,
        ]
    )


def test_geometry_to_cells_linestring():
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
    ]
    geometry = '{{"type":"LineString","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892418453503,
            5274793892418486271,
            5274793892418469887,
            5274793892418568191,
            5274793892418600959,
            5274793892418961407,
            5274793892407771135,
            5274793892407803903,
            5274793892407902207,
            5274793892407885823,
            5274793892407918591,
        ]
    )


def test_geometry_to_cells_multilinestring():
    coordinates = [
        [
            [-3.71219873428345, 40.413365349070865],
            [-3.7144088745117, 40.40965661286395],
        ],
        [
            [-3.714215755462646, 40.41297324565437],
            [-3.710868358612061, 40.412041990883246],
        ],
    ]
    geometry = '{{"type":"MultiLineString","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
            5265786693152669695,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892418453503,
            5274793892418486271,
            5274793892418469887,
            5274793892418568191,
            5274793892418600959,
            5274793892418961407,
            5274793892407771135,
            5274793892407803903,
            5274793892407902207,
            5274793892407885823,
            5274793892407918591,
            5274793892407263231,
            5274793892407279615,
            5274793892418584575,
            5274793892418633727,
            5274793892418650111,
        ]
    )


def test_geometry_to_cells_polygon():
    coordinates = [
        [
            [-3.71219873428345, 40.413365349070865],
            [-3.7144088745117, 40.40965661286395],
            [-3.70659828186035, 40.409525904775634],
            [-3.71219873428345, 40.413365349070865],
        ]
    ]
    geometry = '{{"type":"Polygon","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
            5265786693164728319,
            5265786693165514751,
            5265786693164204031,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892407771135,
            5274793892407803903,
            5274793892407885823,
            5274793892407902207,
            5274793892407918591,
            5274793892407934975,
            5274793892418453503,
            5274793892418469887,
            5274793892418486271,
            5274793892418502655,
            5274793892418535423,
            5274793892418551807,
            5274793892418568191,
            5274793892418584575,
            5274793892418600959,
            5274793892418617343,
            5274793892418633727,
            5274793892418650111,
            5274793892418666495,
            5274793892418682879,
            5274793892418830335,
            5274793892418863103,
            5274793892418879487,
            5274793892418961407,
            5274793892418977791,
            5274793892418994175,
            5274793892419010559,
            5274793892419026943,
            5274793892419043327,
            5274793892419059711,
            5274793892419076095,
            5274793892419092479,
            5274793892419108863,
            5274793892419125247,
            5274793892419141631,
            5274793892419158015,
            5274793892419174399,
            5274793892419190783,
            5274793892419207167,
            5274793892419223551,
            5274793892419239935,
            5274793892419256319,
            5274793892419272703,
            5274793892419289087,
            5274793892419321855,
            5274793892419338239,
            5274793892419354623,
            5274793892419371007,
            5274793892419387391,
            5274793892419403775,
            5274793892419420159,
            5274793892419436543,
            5274793892419452927,
            5274793892419469311,
            5274793892420042751,
            5274793892420141055,
            5274793892420157439,
            5274793892420173823,
            5274793892420190207,
        ]
    )


def test_geometry_to_cells_multipolygon():
    coordinates = [
        [
            [
                [-3.71219873428345, 40.413365349070865],
                [-3.7144088745117, 40.40965661286395],
                [-3.70659828186035, 40.409525904775634],
                [-3.71219873428345, 40.413365349070865],
            ],
            [
                [-3.7118983268737793, 40.4116172037252],
                [-3.7120914459228516, 40.41015493512173],
                [-3.710278272628784, 40.41096367978466],
                [-3.7118983268737793, 40.4116172037252],
            ],
        ],
        [
            [
                [-3.708035945892334, 40.411176075761475],
                [-3.70863676071167, 40.409003069883845],
                [-3.7063729763031006, 40.41048170181224],
                [-3.708035945892334, 40.411176075761475],
            ]
        ],
    ]
    geometry = '{{"type":"MultiPolygon","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693153193983,
            5265786693163941887,
            5265786693164204031,
            5265786693164466175,
            5265786693164728319,
            5265786693165514751,
            5265786693166301183,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892407771135,
            5274793892407803903,
            5274793892407885823,
            5274793892407902207,
            5274793892407918591,
            5274793892407934975,
            5274793892418453503,
            5274793892418469887,
            5274793892418486271,
            5274793892418502655,
            5274793892418535423,
            5274793892418551807,
            5274793892418568191,
            5274793892418584575,
            5274793892418600959,
            5274793892418617343,
            5274793892418633727,
            5274793892418650111,
            5274793892418666495,
            5274793892418682879,
            5274793892418830335,
            5274793892418863103,
            5274793892418879487,
            5274793892418961407,
            5274793892418977791,
            5274793892418994175,
            5274793892419010559,
            5274793892419026943,
            5274793892419043327,
            5274793892419059711,
            5274793892419076095,
            5274793892419092479,
            5274793892419108863,
            5274793892419125247,
            5274793892419141631,
            5274793892419158015,
            5274793892419174399,
            5274793892419190783,
            5274793892419207167,
            5274793892419223551,
            5274793892419239935,
            5274793892419256319,
            5274793892419272703,
            5274793892419289087,
            5274793892419305471,
            5274793892419321855,
            5274793892419338239,
            5274793892419354623,
            5274793892419371007,
            5274793892419387391,
            5274793892419403775,
            5274793892419420159,
            5274793892419436543,
            5274793892419452927,
            5274793892419469311,
            5274793892420009983,
            5274793892420042751,
            5274793892420059135,
            5274793892420108287,
            5274793892420141055,
            5274793892420157439,
            5274793892420173823,
            5274793892420190207,
            5274793892420861951,
            5274793892420878335,
        ]
    )


def test_geometry_to_cells_geometrycollection():
    coordinates = [-3.7118983268737793, 40.4116172037252]
    geometry_point = '{{"type":"Point","coordinates":{0}}}'.format(coordinates)
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
    ]
    geometry_linestring = '{{"type":"LineString","coordinates":{0}}}'.format(
        coordinates
    )
    geometry_collection = (
        '{{"type":"GeometryCollection","geometries":[{0}, {1}]}}'.format(
            geometry_point, geometry_linestring
        )
    )
    assert quadbin.geometry_to_cells(geometry_collection, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry_collection, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry_collection, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry_collection, 19)) == sorted(
        [
            5274793892407771135,
            5274793892407803903,
            5274793892407885823,
            5274793892407902207,
            5274793892407918591,
            5274793892418453503,
            5274793892418469887,
            5274793892418486271,
            5274793892418568191,
            5274793892418600959,
            5274793892418666495,
            5274793892418961407,
        ]
    )


def test_cell_area():
    assert quadbin.cell_area(5209574053332910079) == pytest.approx(
        6023040823252.6641, rel=1e-2
    )
