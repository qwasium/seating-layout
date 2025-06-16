from pathlib import Path
from argparse import ArgumentParser

import yaml
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent.resolve()

# def draw_student(
#     draw: ImageDraw.ImageDraw,
#     student_row: pd.DataFrame, # one-row only
#     top_left: list[int], # [x, y]
#     config: dict,
# ):
#     assert len(student_row)==1, "student_row must be only a single row."
#
#     # student number
#     draw.rectangle(
#     )
#     draw.text(
#         ,
#         student_row["number"],
#         fill=config["student_desk"]["student_num"]["txt_clr"],
#         font=ImageFunt.truentype(
#             config["font_path"], size=config["student_desk"]["student_num"]["font_pt"]
#         )
#     )
#
#     # kana
#     draw.rectangle(
#     )
#     draw.text(
#         ,
#         student_row["kana"],
#         fill=config["student_desk"]["kana"]["txt_clr"],
#         font=ImageFunt.truentype(
#             config["font_path"], size=config["student_desk"]["kana"]["font_pt"]
#         )
#     )
#
#     # kanji
#     draw.rectangle(
#     )
#     draw.text(
#         ,
#         student_row["kanji"],
#         fill=config["student_desk"]["kanji"]["txt_clr"],
#         font=ImageFunt.truentype(
#             config["font_path"], size=config["student_desk"]["kanji"]["font_pt"]
#         )
#     )

def main(config: dict):
    """Read config and create seating layout image.

    Parameters
    ----------
    config: dict
        TODO: add docstring
    """
    # font path
    font_path = HERE / config["font_path"]
    assert font_path.exists(), f"Font doesn't exist: {font_path}"

    # read csv
    names_df = pd.read_csv(HERE / config["names_path"], header=0)
    layout_df = pd.read_csv(HERE / config["layout_path"], header=0, index_col=0)

    # data check
    layout_np = layout_df.to_numpy()
    layout_grps, cnt = np.unique(layout_np, return_counts=True)
    names_grps = names_df["group"].unique()
    assert "x" not in names_grps, "x is a reserved group (no desk); don't use in names csv."
    assert "e" not in names_grps, "e is a reserved group (empty desk); don't use in names csv."
    assert np.array_equal(
        np.sort(layout_grps), np.sort(np.append(names_grps, ["e", "x"]))
    ), "Groups in names csv and layout csv don't match."
    grp_rnd = {}
    for i, grp in enumerate(layout_grps):
        if grp == "e" or grp == "x":
            continue
        assert len(
            names_df[names_df["group"] == grp]
        ) == cnt[i], f"Count for group: {grp} don't match between names csv and layout csv."
        rnd_ary = np.arange(1, cnt[i] + 1)
        np.random.shuffle(rnd_ary)
        grp_rnd[grp] = list(rnd_ary)

    # add shuffld data
    rand_col = []
    for i, row in names_df.iterrows():
        rand_col.append(grp_rnd[row['group']].pop())
    for grp, lst in grp_rnd.items():
        assert lst == [], "Somethings is wrong with random number list."
    names_df["group_shuffle"] = rand_col

    # row wise flatten [(0,0),(1,0),(2,0),...,(x,y)]
    x_index = np.tile(np.arange(1, layout_np.shape[1] + 1), layout_np.shape[0])
    y_index = np.arange(1, layout_np.shape[0] + 1).repeat(layout_np.shape[1])
    layout_flat = layout_np.flatten(order='C')
    for i, grp in enumerate(layout_flat):
        # TODO

 
    # student desk size
    student_desk_sz_x = (
        config["student_desk"]["padding_x"] # padding left
        + config["student_desk"]["sz_x"] # box size x
        + config["student_desk"]["padding_x"] # padding right
    )
    student_desk_sz_y = (
        config["student_desk"]["padding_y"] # padding above
        + config["student_desk"]["student_num"]["box_sz_y"] # student number box size x
        + config["student_desk"]["kana"]["box_sz_y"] # kana box size x
        + config["student_desk"]["kanji"]["box_sz_y"] # kanji box size x
        + config["student_desk"]["padding_y"] # padding below
    )

    # canvas size
    canvas_x = student_desk_sz_x * layout_df.shape[1]
    canvas_y = (
        student_desk_sz_y * layout_df.shape[0]
        + config["teacher_desk"]["sz_y"] # teacher desk
    )
    assert canvas_x > config["teacher_desk"]["sz_x"], "teacher desk is wider than student desks."

    # create image
    canvas = Image.new("RGB", (canvas_x, canvas_y), color=config["back_clr"])
    draw = ImageDraw.Draw(canvas)

    # write to image
    # output_path = HERE / config["output_path"]
    # output_path.parent.mkdir(parent=True, exist_ok=True)
    # img.save(output_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '--config_path', '-f',
        type=str,
        default=str(HERE / 'config' / 'config.yaml'),
        help='Path to config file. Default: <repo root>/config/config.yaml.'
    )
    args = parser.parse_args()
    config_path = Path(args.config_path).resolve()
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    main(config)
