# Seating Layout Generator

This application generates a seating layout chart for classrooms based on configuration files.
It supports multiple groups, random seat assignment, and customizable appearance.

## Usage

The application will:

1. Read the configuration files
2. Randomly assign students to seats within their groups
3. Generate a seating chart image with the specified layout and appearance
4. Save the output image to the specified path

### If you know Python

This program is tested on Python 3.13.

```bash
git clone https://github.com/qwasium/seating-layout.git
cd seating-layout
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python3 main.py -f path/to/config.yaml
```

### If you have no idea

Go ahead and copy & paste this `README.md` file into ChatGPT/Claude/Gemini/etc. to give you guidance.

Regarding `names.csv`: **Be carefull NOT to prompt personal information!**

Doiwnload and test run:

1. Install `Python`
2. [Download this repo](https://github.com/qwasium/seating-layout/archive/refs/heads/main.zip) and unzip.
3. Run the main script to test if it actually runs (see below)
4. Output image is in `output/seating.png`

Creating your own layout images:

1. Configure the appearance in `config.yaml`
2. Define the seating layout in `layout.csv`
3. Add student information in `names.csv`
4. Run the main script (see below)

See [config file section](#configuration-files) for details on configuration.

#### Running the script (Windows)

Run the script `run-me.ps1`.

Open `powershell` and run the following.

```powershell
# You only need to run this one time
# This gives the script the permission to be ran
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the program; create image
.\run-me.ps1
```

#### Running the script (Linux/MacOS)

Run the script `run-me.sh`.

Open the terminal and run the following.

```bash
# You only need to run this one time
# This gives the script the permission to be ran
chmod +x run-me.sh

# Run the program; create image
./run-me.sh
```

## Configuration Files

The application uses three main configuration files located in the `config` directory by default.

If each feels unclear, play around by tweaking the config and see how the output changed.

### 1. config.yaml

The default path is `config/config.yaml`, but could be overridden with the `--config_file` argument of `main.py`.

This is the main configuration file that controls the appearance and behavior of the seating chart.

```yaml
# File paths
names_path: "config/names.csv"     # Path to student names file
layout_path: "config/layout.csv"   # Path to seating layout file
font_path: "fonts/IPAexfont00401/ipaexg.ttf"
                                   # Path to font file
                                   # truetype can be used
output_path: "output/seating.png"  # Output image path

# General settings
back_clr: "white"                  # Background color
random_seed: 36893                 # Random seed for reproducing seat assignment
#random_seed: None                 # Use "None" for non-reproduceable random

# Student desk configuration
student_desk:
  padding_x: 10                    # Horizontal padding
  padding_y: 10                    # Vertical padding
  sz_x: 180                        # Desk width
  student_num:                     # Student number box settings
    sz_y: 20                       # Height
    fill_clr: "white"              # Fill color
    line_clr: "black"              # Border color
    font_pt: 18                    # Font size
    txt_clr: "black"               # Text color
    txt_left_offset: 5             # Text left margin
  kana:                            # Kana name box settings
    sz_y: 20                       # Height
    fill_clr: "white"              # Fill color
    line_clr: "black"              # Border color
    font_pt: 18                    # Font size
    txt_clr: "black"               # Text color
  name:                            # Full name box settings
    sz_y: 40                       # Height
    fill_clr: "white"              # Fill color
    line_clr: "black"              # Border color
    font_pt: 32                    # Font size
    txt_clr: "black"               # Text color
    empty_txt: "n/a"               # Text for empty seats

# Teacher desk configuration
teacher_desk:
  txt: "教卓"                       # Teacher desk text
  sz_x: 300                        # Width
  sz_y: 50                         # Height
  padding_y: 20                    # Vertical padding
  fill_clr: "white"                # Fill color
  line_clr: "black"                # Border color
  font_pt: 38                      # Font size
  txt_clr: "black"                 # Text color

# Title configuration
# Y dimension is determined by teacher desk config
title:
  txt: "Test Render"               # Title text
  txt_left_offset: 5               # Left margin
  font_pt: 32                      # Font size
  txt_clr: "black"                 # Text color

# Date configuration
# Y dimension is determined by teacher desk config
start_date:
  txt: "From Jun. 15, 2025"       # Date text
  #txt: ""                        # If empty, "from <the date script is run>"
  txt_right_offset: 5             # Right margin
  font_pt: 32                     # Font size
  txt_clr: "black"                # Text color
```

### 2. layout.csv

The path is defined in `config.yaml`.

This file defines the seating layout using a grid system.
Each cell in the grid represents a desk position and contains a group identifier that corresponds to `group` column in `names.csv`.

Group identifiers:

- `A`, `B`, etc... (whatever unique string)
  - Group identifiers for student desks.
  - Corresponds to the `group` column in `names.csv`.
- `e`: Empty desk (desk exists, not used)
  - In the output, it will be marked as "n/a" by default
- `x`: No desk (desk does not exist)
  - Empty value is not allowed; use `x` to fill in the blanks\
  - Nothing will be rendered for `x` in the output.

NOTE:

- The output image will be rendered in the **inverted layout**; teacher's desk is at the top in `layout.csv`
- First column must be row index: 0, 1, 2, ...
- First row must be column index: 0, 1, 2, ...
- Empty value is not allowed in any column/row

Example layout:

```csv
0,1,2,3,4,5,6,7
1,e,A,A,A,A,A,e
2,B,B,B,B,B,B,B
3,B,B,B,B,B,B,B
4,B,B,B,B,B,B,B
5,B,B,B,B,B,B,B
6,B,B,x,x,x,x,x
```

In this example,
group `A` represents the students with poor eye sight; thus allocating a seat in the front.
Group `B` is the rest of students which we don't need special care.

In `names.csv`, we put `A` in the `group` column for the students with poor eye sight and put `B` for the rest of the students.

Read on below for details on `names.csv`.

### 3. names.csv

The path is defined in `config.yaml`.

This file contains the student information with the following columns:

- `number`: Student number
- `name`: Student's full name
- `kana`: Student's name in kana
- `group`: Group identifier that corresponds to the values in `layout.csv`
  - `A`, `B`, etc...: whatever unique string except `x` and `e` can be used.

Example:

```csv
number,name,kana,group
1,安藤 光希,あんどう こうき,B
2,石田 晴香,いしだ はるか,B
...
```

## Notes

- The number of students in each group in `names.csv` must match the number of desks for that group in `layout.csv`
  - In the example above, group `A` is 5 people in `names.csv` and 5 desks in `layout.csv`; the count should match for all groups. 
- Group identifiers `x` and `e` are reserved and should not be used in `names.csv`
  - `x` and `e` are used only in `layout.csv`
  - `x`: no desk (empty value not allowed in `layout.csv`)
  - `e`: empty desk (desk exists but is not used)
- The random seed in `config.yaml` can be set to "none" for random assignment each time
- The output image will be saved in the specified `output_path`
- Can I directly set the output image size in `config.yaml`?: No
  - The size of the output image is just a result of tiling the desks
  - Change the layout or the parameters of desk size to adjust
