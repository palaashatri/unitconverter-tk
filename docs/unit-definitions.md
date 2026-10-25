# Unit definitions and conventions

All linear factors are relative to the base unit shown. Values are stored as floating-point numbers, so calculations can have ordinary floating-point rounding. The tests use `pytest.approx` for reference values and round trips.

## Standards and sources

- NIST, [Guide for the Use of the International System of Units (SI), SP 811](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.811e2008.pdf), unit symbols, SI conversions, and customary-unit relationships.
- NIST, [Metric SI prefixes](https://www.nist.gov/pml/owm/metric-si-prefixes), decimal SI prefixes.
- BIPM, [The International System of Units (SI)](https://www.bipm.org/en/publications/si-brochure), SI base/derived units and exact definitions.
- NIST, [Fundamental Physical Constants](https://physics.nist.gov/cuu/Constants/), electronvolt conversion to joules.
- NASA Glenn, [Speed of Sound](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/speed-of-sound/), Mach-number dependence on the medium and conditions.

## Length

Base unit: metre (m).

| Code | Unit | Metres per unit |
|---|---|---:|
| nmi | international nautical mile | 1852 |
| mi | international mile | 1609.344 |
| yd | international yard | 0.9144 |
| ft | international foot | 0.3048 |
| inch | international inch | 0.0254 |
| km | kilometre | 1000 |
| m | metre | 1 |
| cm | centimetre | 0.01 |
| mm | millimetre | 0.001 |

## Area

Base unit: square metre (sqm).

| Code | Unit | Square metres per unit |
|---|---|---:|
| sqkm | square kilometre | 1,000,000 |
| sqr | square rood | 1011.7141056 |
| sqcm | square centimetre | 0.0001 |
| sqf | square foot | 0.09290304 |
| sqin | square inch | 0.00064516 |
| sqmile | square mile | 2,589,988.110336 |
| sqmm | square millimetre | 0.000001 |
| sqrod | square rod | 25.29285264 |
| sqyard | square yard | 0.83612736 |
| sqtownship | square township (36 square miles) | 93,239,571.972096 |
| sqacre | acre | 4046.8564224 |
| sqare | are | 100 |
| sqbarn | barn | 1e-28 |
| sqhectare | hectare | 10,000 |
| sqhomestead | homestead (160 acres) | 647,497.027584 |

`mm` remains a compatibility alias for square millimetres; the UI and expression parser use the unambiguous `sqmm` code.

## Mass (shown in the app as Weight)

Base unit: gram (g).

| Code | Unit | Grams per unit |
|---|---|---:|
| kg | kilogram | 1000 |
| hg | hectogram | 100 |
| dag | decagram | 10 |
| g | gram | 1 |
| dg | decigram | 0.1 |
| cg | centigram | 0.01 |
| mg | milligram | 0.001 |

`deg` remains a compatibility alias for decigram. The former incorrect decagram code `dg` now has the correct SI meaning; decagram is `dag`.

## Volume and cooking measures

Base unit: millilitre (mL). U.S. customary liquid definitions are used for cup, spoon, fluid ounce, pint, quart, and gallon. They are not Imperial or U.S. legal cup values.

| Code | Unit | Millilitres per unit |
|---|---|---:|
| tsp | U.S. customary teaspoon | 4.92892159375 |
| tbsp | U.S. customary tablespoon | 14.78676478125 |
| floz | U.S. customary fluid ounce | 29.5735295625 |
| cup | U.S. customary cup | 236.5882365 |
| pint | U.S. customary liquid pint | 473.176473 |
| quart | U.S. customary liquid quart | 946.352946 |
| gal | U.S. customary liquid gallon | 3785.411784 |
| ml | millilitre | 1 |
| l | litre | 1000 |
| cm3 | cubic centimetre | 1 |
| in3 | cubic inch | 16.387064 |
| ft3 | cubic foot | 28,316.846592 |
| m3 | cubic metre | 1,000,000 |

One U.S. customary cup is 8 fluid ounces, one tablespoon is 1/2 fluid ounce, and one teaspoon is 1/3 tablespoon. The Cooking tab is a focused view over the same volume conversion definitions.

## Digital storage and data rate

Digital storage uses bytes as its base. The existing storage category uses decimal SI multiples: kB = 1000 bytes, MB = 1,000,000 bytes, GB = 1,000,000,000 bytes, TB = 1,000,000,000,000 bytes, and PB = 1,000,000,000,000,000 bytes. One byte is 8 bits.

Data rate uses bits per second as its base. Lowercase `k`, `M`, `G`, and `T` denote decimal SI multiples (powers of 1000); `Ki`, `Mi`, `Gi`, and `Ti` denote binary IEC multiples (powers of 1024). Uppercase `B` denotes bytes; lowercase `bit` denotes bits.

## Angle

Base unit: radian (rad).

| Code | Unit | Radians per unit |
|---|---|---:|
| rad | radian | 1 |
| deg | degree | π/180 |
| grad | gradian | π/200 |
| turn | full turn | 2π |
| arcmin | arcminute | π/10,800 |
| arcsec | arcsecond | π/648,000 |

## Fuel economy

The app supports L/100 km, km/L, U.S. mpg, and Imperial mpg. The latter two mean miles per U.S. liquid gallon and miles per Imperial gallon, respectively. Fuel economy is reciprocal: zero and negative values are rejected.

For a positive amount:

- `L/100 km = 100 / (km/L)`.
- `L/100 km = (100 × 3.785411784 / 1.609344) / (U.S. mpg)`.
- `L/100 km = (100 × 4.54609 / 1.609344) / (Imperial mpg)`.
- Reverse conversions apply the corresponding numerator divided by L/100 km.

The gallon and mile definitions are exact; the displayed decimal values inherit floating-point rounding.

## Speed

Base unit: metre per second (m/s).

| Code | Unit | Metres per second per unit |
|---|---|---:|
| mps | metre per second | 1 |
| kph | kilometre per hour | 1/3.6 |
| mph | international mile per hour | 1609.344/3600 |
| fps | international foot per second | 0.3048 |
| knot | international nautical mile per hour | 1852/3600 |
| mach | Mach 1 at the app's dry-air 20 °C reference | 343.2 |

Mach is not a fixed speed outside a specified medium and condition; the app uses 343.2 m/s as a stated reference convention.

## Time

Base unit: second (s).

| Code | Unit | Seconds per unit |
|---|---|---:|
| us | microsecond | 0.000001 |
| ms | millisecond | 0.001 |
| sec | second | 1 |
| min | minute | 60 |
| hr | hour | 3600 |
| day | day | 86,400 |
| week | week | 604,800 |
| month | average Gregorian month (year/12) | 2,629,746 |
| year | average Gregorian year (365.2425 days) | 31,556,952 |

Month and year are application averages, not fixed calendar durations.

## Pressure

Base unit: pascal (Pa).

| Code | Unit | Pascals per unit |
|---|---|---:|
| pa | pascal | 1 |
| kpa | kilopascal | 1000 |
| bar | bar | 100,000 |
| psi | pound-force per square inch | 6894.757293168 |
| atm | standard atmosphere | 101,325 |
| torr | torr (standard atmosphere/760) | 101325/760 |
| mmhg | conventional millimetre of mercury at 0 °C | 133.322387415 |

Torr and mmHg are intentionally distinct definitions.

## Energy

Base unit: joule (J).

| Code | Unit | Joules per unit |
|---|---|---:|
| j | joule | 1 |
| kj | kilojoule | 1000 |
| cal | thermochemical calorie | 4.184 |
| kcal | thermochemical kilocalorie | 4184 |
| wh | watt-hour | 3600 |
| kwh | kilowatt-hour | 3,600,000 |
| btu | International Table British thermal unit | 1055.05585262 |
| ftlb | foot-pound force | 1.3558179483314004 |
| ev | electronvolt | 1.602176634e-19 |

## Temperature

Temperature uses affine formulas rather than factors:

- °F = °C × 9/5 + 32
- K = °C + 273.15
- °C = (°F − 32) × 5/9
- K = (°F − 32) × 5/9 + 273.15
- °C = K − 273.15
- °F = (K − 273.15) × 9/5 + 32

Temperatures below absolute zero are rejected. The old spelling `covert_celToKel` remains as a compatibility alias for `convert_celToKel`.
