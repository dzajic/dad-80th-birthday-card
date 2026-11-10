# Sources and licenses

The paintings in this card are original illustrations made for it. They are not photographs, and they are not portraits of Dad or the family. Reference images were used only to get real subjects right, then set aside. They are not shipped in the site.

## Map

The North Atlantic map is drawn from **Natural Earth** 1:50 million cultural and physical data (admin-0 countries and lakes), which is in the public domain.

- https://www.naturalearthdata.com/about/terms-of-use/
- Countries: `ne_50m_admin_0_countries` via https://github.com/martynafford/natural-earth-geojson
- Lakes: `ne_50m_lakes` from the same set

`scripts/build_map.py` projects the coastlines with a Lambert conformal conic centered on the North Atlantic, clips them to the crossing from Montreal to Czechia, and draws the route Prague → Paris → London → Montréal. Rebuild it only if you want to change the window or the labels. The committed file is `images/journey-map.svg`.

## Reference photographs

Used as visual references, not as page assets.

| Subject | Source | License |
| --- | --- | --- |
| Prague, Charles Bridge and Castle | [Prague Vltava River, Charles Bridge and Castle View](https://commons.wikimedia.org/wiki/File:Prague_Vltava_River_Charles_Bridge_and_Castle_View.jpg), MichaelOpdenacker | CC BY-SA 4.0 |
| Pontiac Aztek, 2002–2005 | [2002-05 Pontiac Aztek](https://commons.wikimedia.org/wiki/File:2002-05_Pontiac_Aztek.jpg), IFCAR | Public domain |
| Mount Washington Cog Railway | [Mt. Washington Cog Railway](https://commons.wikimedia.org/wiki/File:Mt._Washington_Cog_Railway.jpg), Dnoahg | CC BY-SA 4.0 |
| Swiss chalet (architecture) | [Weggis, Chalet Antique](https://commons.wikimedia.org/wiki/File:Weggis-House_Chalet_Antique-01ASD.jpg), Asurnipal | CC BY-SA 4.0 |
| Hockey goal (net shape) | [Ice hockey goal 2014](https://commons.wikimedia.org/wiki/File:Ice_hockey_goal_2014.JPG) | See the file page on Wikimedia Commons |

The canoe, the outdoor hockey action, the vintage camera, the Canadian road, the supersonic airliner, and the tablet were grounded with faithful study images of those subjects (a real open canoe with two adults and two children, a shot on a goalie, an SLR, a northern mine road, and the 2022 Boom Overture arrangement: long nose, wing-mounted engines, conventional tail). Those study images are not photos of this family and are not in the site.

## Type

- [Fraunces](https://github.com/undercasetype/fraunces), Undercase Type, SIL Open Font License
- [Source Sans 3](https://github.com/adobe-fonts/source-sans), Adobe, SIL Open Font License

The files in `fonts/` are the Latin and Latin-extended subsets published by Fontsource.
