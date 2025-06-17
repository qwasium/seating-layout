from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser
from warnings import warn

import yaml
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent.resolve()

def draw_student(
    draw: ImageDraw.ImageDraw,
    student_row: pd.DataFrame, # one-row only
    top_left: tuple[int, int], # [x, y]
    config: dict,
):
    """Draw student desk.

    Parametes
    ---------
    draw: PIL.ImageDraw.ImageDraw
        Pillow draw object.
    student_row: pd.DataFrame
        Single row of pandas dataframe with columns:
        - "number": Any
            Student number in top row.
        - "name": str
            Student name in bottom row.
        - "kana": str
            Student kana in 2nd row.
        - Any other column is ignored.
    top_left: tuple[int, int]
        Top-left [x, y] coords on draw of student desk.
    config: dict
        See README.md
    """
    assert len(student_row.shape)==1, "student_row must be only a single row."

    # student number
    num_tl = (
        top_left[0] + config["student_desk"]["padding_x"],
        top_left[1] + config["student_desk"]["padding_y"]
    )
    draw.rectangle(
        [
            num_tl[0],
            num_tl[1],
            num_tl[0] + config["student_desk"]["sz_x"],
            num_tl[1] + config["student_desk"]["student_num"]["sz_y"],
        ],
        fill=config["student_desk"]["student_num"]["fill_clr"],
        outline=config["student_desk"]["student_num"]["line_clr"],
    )
    if pd.isna(student_row["number"]):
        student_number = ""
    else:
        student_number = str(int(student_row["number"]))
    draw.text(
        (
            num_tl[0] + config["student_desk"]["student_num"]["txt_left_offset"],
            num_tl[1] + config["student_desk"]["student_num"]["sz_y"] / 2
        ),
        student_number,
        anchor="lm",
        fill=config["student_desk"]["student_num"]["txt_clr"],
        font=ImageFont.truetype(
            config["font_path"], size=config["student_desk"]["student_num"]["font_pt"]
        )
    )

    # kana
    kana_tl = (
        num_tl[0],
        num_tl[1] + config["student_desk"]["student_num"]["sz_y"],
    )
    draw.rectangle(
        (
            kana_tl[0],
            kana_tl[1],
            kana_tl[0] + config["student_desk"]["sz_x"],
            kana_tl[1] + config["student_desk"]["kana"]["sz_y"]
        ),
        fill=config["student_desk"]["kana"]["fill_clr"],
        outline=config["student_desk"]["kana"]["line_clr"],
    )
    draw.text(
        (
            kana_tl[0] + config["student_desk"]["sz_x"] / 2,
            kana_tl[1] + config["student_desk"]["kana"]["sz_y"] / 2
        ),
        student_row["kana"],
        anchor="mm",
        fill=config["student_desk"]["kana"]["txt_clr"],
        font=ImageFont.truetype(
            config["font_path"], size=config["student_desk"]["kana"]["font_pt"]
        )
    )

    # kanji name
    name_tl = (
        num_tl[0],
        kana_tl[1] + config["student_desk"]["kana"]["sz_y"]
    )
    draw.rectangle(
        (
            name_tl[0],
            name_tl[1],
            name_tl[0] + config["student_desk"]["sz_x"],
            name_tl[1] + config["student_desk"]["name"]["sz_y"]
        ),
        fill=config["student_desk"]["name"]["fill_clr"],
        outline=config["student_desk"]["name"]["line_clr"],
    )
    draw.text(
        (
            name_tl[0] + config["student_desk"]["sz_x"] / 2,
            name_tl[1] + config["student_desk"]["name"]["sz_y"] / 2
        ),
        student_row["name"],
        anchor="mm",
        fill=config["student_desk"]["name"]["txt_clr"],
        font=ImageFont.truetype(
            config["font_path"], size=config["student_desk"]["name"]["font_pt"]
        )
    )

def main(config: dict):
    """Read config and create seating layout image.

    Parameters
    ----------
    config: dict
        See README.md.
    """
    # font path
    font_path = HERE / config["font_path"]
    assert font_path.exists(), f"Font doesn't exist: {font_path}"

    # read csv
    names_df = pd.read_csv(HERE / config["names_path"], header=0)
    layout_df = pd.read_csv(HERE / config["layout_path"], header=0, index_col=0)

    # shuffle
    if isinstance(config["random_seed"], str):
        if config["random_seed"].lower() in ["", "none", "nan"]:
            seed = None
    else:
        seed = config["random_seed"]
    names_df = names_df.sample(frac=1, random_state=seed, ignore_index=True)

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
        if len(names_df[names_df["group"] == grp]) != cnt[i]:
            raise ValueError(
                f"Count for group: {grp} don't match between \
                names csv: {names_df[names_df['group'] == grp]} and layout csv: {cnt[i]}."
            )
        rnd_ary = np.arange(1, cnt[i] + 1)
        np.random.shuffle(rnd_ary)
        grp_rnd[grp] = list(rnd_ary) # starts from 1

    # add shuffld data
    rand_col = []
    for i, row in names_df.iterrows():
        rand_col.append(grp_rnd[row['group']].pop())
    for grp, lst in grp_rnd.items():
        assert lst == [], "Somethings is wrong with random number list."
    names_df["group_shuffle"] = rand_col # starts from 1

    # generate x,y index from layout
    # row wise flatten [(0,0),(1,0),(2,0),...,(x,y)]
    x_index = np.tile(np.arange(1, layout_np.shape[1] + 1), layout_np.shape[0])
    y_index = np.arange(1, layout_np.shape[0] + 1).repeat(layout_np.shape[1])
    layout_flat = layout_np.flatten(order='C')
    grp_idx = {
        grp: {
            'x': list(x_index[layout_flat==grp]), # starts from 1
            'y': list(y_index[layout_flat==grp])  # starts from 1
        } for grp in layout_grps
    }

    # add x,y index to names_df
    x_col = []
    y_col = []
    for i, row in names_df.iterrows():
        x_col.append(grp_idx[row["group"]]["x"].pop())
        y_col.append(grp_idx[row["group"]]["y"].pop())
    names_df["x_idx"] = x_col # starts from 1
    names_df["y_idx"] = y_col # starts from 1
    for i, (x, y) in enumerate(zip(grp_idx["e"]["x"], grp_idx["e"]["y"])):
        names_df = pd.concat(
            [
                names_df,
                pd.DataFrame(
                    [
                        {
                            "name": config["student_desk"]["name"]["empty_txt"],
                            "kana": "",
                            "group": "e",
                            "group_shuffle": i + 1, # starts from 1
                            "x_idx": x, # starts from 1
                            "y_idx": y # starts from 1
                        }
                    ]
                )
            ],
            ignore_index=True
        )
 
    # student desk size
    student_desk_sz_x = (
        config["student_desk"]["padding_x"] # padding left
        + config["student_desk"]["sz_x"] # box size x
        + config["student_desk"]["padding_x"] # padding right
    )
    student_desk_sz_y = (
        config["student_desk"]["padding_y"] # padding above
        + config["student_desk"]["student_num"]["sz_y"] # student number box size x
        + config["student_desk"]["kana"]["sz_y"] # kana box size x
        + config["student_desk"]["name"]["sz_y"] # kanji name box size x
        + config["student_desk"]["padding_y"] # padding below
    )

    # canvas size
    canvas_x = student_desk_sz_x * layout_df.shape[1]
    canvas_y = (
        student_desk_sz_y * layout_df.shape[0]
        # teacher desk
        + config["teacher_desk"]["padding_y"] # padding above
        + config["teacher_desk"]["sz_y"] # teacher desk
        + config["teacher_desk"]["padding_y"] # padding below
    )
    assert canvas_x > config["teacher_desk"]["sz_x"], "teacher desk is wider than student desks."

    # create image
    canvas = Image.new("RGB", (canvas_x, canvas_y), color=config["back_clr"])
    draw = ImageDraw.Draw(canvas)

    # draw teacher desk
    draw.rectangle(
        (
            (canvas_x - config["teacher_desk"]["sz_x"]) / 2, # allign center; no padding
            canvas_y - config["teacher_desk"]["padding_y"] - config["teacher_desk"]["sz_y"],
            (canvas_x + config["teacher_desk"]["sz_x"]) / 2, # allign center; no padding
            canvas_y - config["teacher_desk"]["padding_y"]
        ),
        fill=config["teacher_desk"]["fill_clr"],
        outline=config["teacher_desk"]["line_clr"]
    )
    draw.text(
        (
            canvas_x / 2,
            canvas_y - config["teacher_desk"]["padding_y"] - config["teacher_desk"]["sz_y"] / 2
        ),
        config["teacher_desk"]["txt"],
        anchor="mm",
        fill=config["teacher_desk"]["txt_clr"],
        font=ImageFont.truetype(config["font_path"], size=config["teacher_desk"]["font_pt"])
    )

    # draw title
    draw.text(
        (
            config["title"]["txt_left_offset"],
            canvas_y - config["teacher_desk"]["padding_y"] - config["teacher_desk"]["sz_y"] / 2
        ),
        config["title"]["txt"],
        anchor="lm",
        fill=config["title"]["txt_clr"],
        font=ImageFont.truetype(config["font_path"], size=config["title"]["font_pt"])
    )

    # draw date of layout to take effect
    assert isinstance(config["start_date"]["txt"], str), "start_date must be string."
    if not config["start_date"]["txt"]:
        start_date = "From " + datetime.now().strftime("%b. %d, %Y")
    else:
        start_date = config["start_date"]["txt"]
    draw.text(
        (
            canvas_x - config["start_date"]["txt_right_offset"], 
            canvas_y - config["teacher_desk"]["padding_y"] - config["teacher_desk"]["sz_y"] / 2
        ),
        start_date,
        anchor="rm",
        fill=config["start_date"]["txt_clr"],
        font=ImageFont.truetype(config["font_path"], size=config["start_date"]["font_pt"])
    )


    # draw student desks
    for grp in layout_grps:
        if grp=="x":
            continue
        for i, row in names_df[names_df["group"]==grp].iterrows():
            tl_coord = (
                (layout_np.shape[1] - row["x_idx"]) * student_desk_sz_x,
                (layout_np.shape[0] - row["y_idx"]) * student_desk_sz_y
            )
            if tl_coord[0] > canvas_x or tl_coord[1] > canvas_y:
                warn("Something is wrong; student desk is outside of image.")
            draw_student(draw=draw, student_row=row, top_left=tl_coord, config=config)

    # write to image
    output_path = HERE / config["output_path"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)


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
