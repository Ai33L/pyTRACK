Statistics
==========

.. autofunction:: pyTRACK.stats_track

The stats_track function computes the track statistics from track_uv() output. This workflow runs stats in every {hemisphere}_y{year} 
directory and writes two files - stats_ff_trs_pos.nc and stats_ff_trs_neg.nc, associated the statistics of the positive and negative
vorticity anomalies.

These files have the following fields-

1. mstr - mean intensity (/s)
2. stdstr - std of intensity (/s)
3. msp - mean speed (m/s)
4. stdsp- std of speed (m/s)
5. fden - feature density (cyclones/ 5 degree spherical cap)
6. gden - genesis density (genesis/ 5 degree spherical cap)
7. lden - lysis density (lysis/ 5 degree spherical cap)
8. tden - track density (cyclones/ 5 degree spherical cap)
9. xvel - x component of mean velocity (m/s)
10. yvel - y component of mean velocity (m/s)
11. mlif - mean lifetime
12. mgdr - mean growth/decay rate (unitless)
13. miso - mean anisotropy
14. xor - x component of mean orientation vector
15. yor - y component of mean orientation vector
16. mten - mean tendency
17. marea - mean area (steradian, multiply by (Radius of earth)^2 to get units of km^2)

stats_track() also outputs other files - to see all of them, pass keep_all_files=True