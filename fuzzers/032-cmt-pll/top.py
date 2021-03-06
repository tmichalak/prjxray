import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.db import Database
import json


def gen_sites():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['PLLE2_ADV']:
                yield site_name


def main():
    f = open('params.jl', 'w')
    f.write('module,loc,params\n')

    print(
        """module top(input clk);

    (* KEEP, DONT_TOUCH *)
    LUT1 dummy();
            """)

    for site in sorted(gen_sites()):
        params = {
            "site":
            site,
            'active':
            random.random() > .2,
            "clkin1_conn":
            random.choice((
                "clkfbout_mult_BUFG_" + site,
                "clk",
            )),
            "clkin2_conn":
            random.choice((
                "clkfbout_mult_BUFG_" + site,
                "clk",
            )),
            "dclk_conn":
            random.choice((
                "0",
                "clk",
            )),
            "dwe_conn":
            random.choice((
                "",
                "1",
                "0",
                "dwe_" + site,
                "den_" + site,
            )),
            "den_conn":
            random.choice((
                "",
                "1",
                "0",
                "den_" + site,
            )),
            "daddr4_conn":
            random.choice((
                "0",
                "dwe_" + site,
            )),
            "IS_RST_INVERTED":
            random.randint(0, 1),
            "IS_PWRDWN_INVERTED":
            random.randint(0, 1),
            "IS_CLKINSEL_INVERTED":
            random.randint(0, 1),
            "CLKFBOUT_MULT":
            random.randint(2, 4),
            "CLKOUT0_DIVIDE":
            random.randint(1, 128),
            "CLKOUT1_DIVIDE":
            random.randint(1, 128),
            "CLKOUT2_DIVIDE":
            random.randint(1, 128),
            "CLKOUT3_DIVIDE":
            random.randint(1, 128),
            "CLKOUT4_DIVIDE":
            random.randint(1, 128),
            "CLKOUT5_DIVIDE":
            random.randint(1, 128),
            "DIVCLK_DIVIDE":
            random.randint(1, 5),
            "CLKOUT0_DUTY_CYCLE":
            "0.500",
            "STARTUP_WAIT":
            verilog.quote('TRUE' if random.randint(0, 1) else 'FALSE'),
            "COMPENSATION":
            verilog.quote(
                random.choice((
                    'ZHOLD',
                    'BUF_IN',
                    'EXTERNAL',
                    'INTERNAL',
                ))),
            "BANDWIDTH":
            verilog.quote(random.choice((
                'OPTIMIZED',
                'HIGH',
                'LOW',
            ))),
        }

        if verilog.unquote(params['COMPENSATION']) == 'ZHOLD':
            params['clkfbin_conn'] = random.choice(
                (
                    "",
                    "clkfbout_mult_BUFG_" + site,
                ))
        elif verilog.unquote(params['COMPENSATION']) == 'INTERNAL':
            params['clkfbin_conn'] = random.choice(
                (
                    "",
                    "clkfbout_mult_" + site,
                ))
        else:
            params['clkfbin_conn'] = random.choice(
                ("", "clk", "clkfbout_mult_BUFG_" + site))

        f.write('%s\n' % (json.dumps(params)))

        if not params['active']:
            continue

        print(
            """

    wire den_{site};
    wire dwe_{site};

    LUT1 den_lut_{site} (
        .O(den_{site})
    );

    LUT1 dwe_lut_{site} (
        .O(dwe_{site})
    );

    wire clkfbout_mult_{site};
    wire clkfbout_mult_BUFG_{site};
    wire clkout0_{site};
    wire clkout1_{site};
    wire clkout2_{site};
    wire clkout3_{site};
    wire clkout4_{site};
    wire clkout5_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PLLE2_ADV #(
            .IS_RST_INVERTED({IS_RST_INVERTED}),
            .IS_PWRDWN_INVERTED({IS_PWRDWN_INVERTED}),
            .IS_CLKINSEL_INVERTED({IS_CLKINSEL_INVERTED}),
            .CLKOUT0_DIVIDE({CLKOUT0_DIVIDE}),
            .CLKOUT1_DIVIDE({CLKOUT1_DIVIDE}),
            .CLKOUT2_DIVIDE({CLKOUT2_DIVIDE}),
            .CLKOUT3_DIVIDE({CLKOUT3_DIVIDE}),
            .CLKOUT4_DIVIDE({CLKOUT4_DIVIDE}),
            .CLKOUT5_DIVIDE({CLKOUT5_DIVIDE}),
            .CLKFBOUT_MULT({CLKFBOUT_MULT}),
            .DIVCLK_DIVIDE({DIVCLK_DIVIDE}),
            .STARTUP_WAIT({STARTUP_WAIT}),
            .CLKOUT0_DUTY_CYCLE({CLKOUT0_DUTY_CYCLE}),
            .COMPENSATION({COMPENSATION}),
            .BANDWIDTH({BANDWIDTH}),
            .CLKIN1_PERIOD(10.0),
            .CLKIN2_PERIOD(10.0)
    ) pll_{site} (
            .CLKFBOUT(clkfbout_mult_{site}),
            .CLKOUT0(clkout0_{site}),
            .CLKOUT1(clkout1_{site}),
            .CLKOUT2(clkout2_{site}),
            .CLKOUT3(clkout3_{site}),
            .CLKOUT4(clkout4_{site}),
            .CLKOUT5(clkout5_{site}),
            .DRDY(),
            .LOCKED(),
            .DO(),
            .CLKFBIN({clkfbin_conn}),
            .CLKIN1({clkin1_conn}),
            .CLKIN2({clkin2_conn}),
            .CLKINSEL(),
            .DCLK({dclk_conn}),
            .DEN({den_conn}),
            .DWE({dwe_conn}),
            .PWRDWN(),
            .RST(),
            .DI(),
            .DADDR({{7{{ {daddr4_conn} }} }}));

    (* KEEP, DONT_TOUCH *)
    BUFG bufg_{site} (
        .I(clkfbout_mult_{site}),
        .O(clkfbout_mult_BUFG_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkfbout_mult_{site} (
        .C(clkfbout_mult_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkout0_{site} (
        .C(clkout0_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkout1_{site} (
        .C(clkout1_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkout2_{site} (
        .C(clkout2_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkout3_{site} (
        .C(clkout3_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkout4_{site} (
        .C(clkout4_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkout5_{site} (
        .C(clkout5_{site})
    );
            """.format(**params))

    print('endmodule')

    f.close()


if __name__ == "__main__":
    main()
