"""StudentFinder Rzeszów — interfejs rekomendacji okolic dla studentów."""

import csv
import io

from html import escape
from pathlib import Path
from textwrap import dedent

import folium
import streamlit as st
from streamlit_folium import st_folium

from scripts.recommendation_engine import (
    RecommendationEngine,
    generate_recommendations,
)


# ==========================================
# KONFIGURACJA
# ==========================================

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="StudentFinder Rzeszów",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# STYL APLIKACJI
# ==========================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1450px;
            padding-top: 1.7rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            min-width: 340px !important;
            max-width: 380px !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            background: #f1f5f9;
        }

        h1, h2, h3 {
            color: #14213d;
            letter-spacing: -0.025em;
        }

        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 14px 18px;
        }

        [data-testid="stMetricValue"] {
            color: #14213d;
        }

        div.stButton > button[kind="primary"] {
            border-radius: 10px;
            font-weight: 700;
            min-height: 46px;
            background: #2563eb;
        }

        div[data-baseweb="select"] > div {
            min-height: 44px;
        }

        div[data-baseweb="popover"] {
            min-width: min(450px, 90vw);
        }

        .hero-note {
            color: #64748b;
            font-size: 1.04rem;
            margin-top: -0.4rem;
            margin-bottom: 1.1rem;
        }

        .result-card {
            height: 100%;
            min-height: 240px;
            padding: 18px;
            border: 1px solid #e2e8f0;
            border-top: 5px solid var(--accent);
            border-radius: 16px;
            background: #fff;
            box-shadow: 0 4px 16px rgba(15,23,42,.04);
        }

        .result-card .rank {
            font-size: .8rem;
            font-weight: 700;
            color: var(--accent);
            letter-spacing: .03em;
        }

        .result-card .area {
            font-size: 1.25rem;
            font-weight: 750;
            color: #14213d;
            margin: .4rem 0;
            overflow-wrap: anywhere;
        }

        .result-card .score {
            font-size: 1.85rem;
            font-weight: 800;
            color: #14213d;
        }

        .result-card .score span {
            font-size: .9rem;
            color: #64748b;
            font-weight: 500;
        }

        .result-card .detail {
            font-size: .89rem;
            color: #334155;
            margin-top: .5rem;
        }

        .result-card .reason {
            font-size: .8rem;
            color: #64748b;
            margin-top: .8rem;
            overflow-wrap: anywhere;
        }

        .map-legend {
            font-size: .9rem;
            color: #475569;
            margin: 0 0 12px;
        }

        .small-muted {
            font-size: .84rem;
            color: #64748b;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 1rem;
            }

            .result-card {
                min-height: 0;
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# WCZYTYWANIE DANYCH
# ==========================================

@st.cache_resource
def load_engine():
    return RecommendationEngine.from_files(
        ROOT / "data/processed/services.json",
        ROOT / "data/processed/universities.json",
        ROOT / "config/residential-areas.json"
    )


try:
    engine = load_engine()

except (OSError, ValueError, KeyError, TypeError) as error:
    st.error(f"Nie można wczytać danych projektu: {error}")
    st.stop()


# ==========================================
# NAZWY UCZELNI
# ==========================================

UNIVERSITY_NAMES = {
    "UR": "Uniwersytet Rzeszowski (UR)",
    "PRz": "Politechnika Rzeszowska (PRz)",
    "WSIiZ": "WSIiZ",
    "WSPiA": "WSPiA",
}


# ==========================================
# UJEDNOLICONE NAZWY LOKALIZACJI
# ==========================================

# Nazwy wyświetlane w interfejsie.
# Oryginalne dane JSON pozostają bez zmian.

LOCATION_LABELS = {
    ("UR", "Aleksandra Zelwerowicza 4, Rzeszów"):
        "Wydz. Biologiczno-Rolniczy – Centrum Transferu Technologii",

    ("UR", "Cicha 2a, Rzeszów"):
        "Budynek E4 – Cicha",

    ("PRz", "Poznańska 2, Rzeszów"):
        "Budynek P",

    ("PRz", "aleja Powstańców Warszawy 6, Rzeszów"):
        "Wydz. Matematyki i Fizyki – Katedra Fizyki",

    ("PRz", "Aleja Powstańców Warszawy 12, Rzeszów"):
        "Regionalne Centrum Dydaktyczno-Konferencyjne",

    ("UR", "Aleja Tadeusza Rejtana 16c, Rzeszów"):
        "Budynek A1",

    ("UR", "Grunwaldzka 13, Rzeszów"):
        "Wydział Prawa i Administracji",

    ("UR", "Stanisława Moniuszki 10, Rzeszów"):
        "Instytut Archeologii",

    ("UR", "Księdza Józefa Jałowego 24, Rzeszów"):
        "Instytut Pedagogiki",

    ("PRz", "Wincentego Pola 2, Rzeszów"):
        "Wydz. Elektrotechniki i Informatyki",

    ("UR", "Aleja Tadeusza Rejtana 16a, Rzeszów"):
        "Budynek A2",

    ("UR", "Aleja Tadeusza Rejtana 16b, Rzeszów"):
        "Budynek A3",

    ("UR", "Profesora Stanisława Pigonia 1, Rzeszów"):
        "Budynek A0",

    ("PRz", "Marii Skłodowskiej-Curie 8/1, Rzeszów"):
        "Budynek D",

    ("PRz", "Franciszka Żwirki i Stanisława Wigury 2, Rzeszów"):
        "Budynek E",

    ("WSPiA", "Cegielniana 14, Rzeszów"):
        "Siedziba uczelni – Cegielniana 14",

    ("UR", "Klementyny Hoffmanowej 25, Rzeszów"):
        "Wydział Wychowania Fizycznego",

    ("WSIiZ", "Majora Henryka Sucharskiego 2, Rzeszów"):
        "Siedziba uczelni – Sucharskiego 2",

    ("UR", "Warzywna 1a, Rzeszów"):
        "Kolegium Nauk Medycznych – Warzywna",

    ("UR", "Leszka Czarnego 4, Rzeszów"):
        "Zakład Nauk o Człowieku",

    ("UR", "Litawora 2, Rzeszów"):
        "Kolegium Nauk Medycznych – Litawora",

    ("UR", "Warszawska 26a, Rzeszów"):
        "Centrum Symulacji Medycznej",

    ("UR", "Aleksandra Zelwerowicza 8b, Rzeszów"):
        "Wydz. Biologiczno-Rolniczy – Centrum Badawcze",

    ("UR", "Mieczysławy Ćwiklińskiej 2, Rzeszów"):
        "Wydział Ekonomii",

    ("PRz", "Poznańska 2e, Rzeszów"):
        "Budynek W",
}


def get_location_label(location):
    """
    Zwraca krótką nazwę lokalizacji.
    Rozróżnia budynki C i F, które mają ten sam adres.
    """

    name = location["name"]

    if location["university"] == "PRz":

        if name == "Budynek C":
            return "Budynek C"

        if name == "Budynek F":
            return "Budynek F"

    return LOCATION_LABELS.get(
        (location["university"], location["address"]),
        name
    )


# ==========================================
# PRZYGOTOWANIE LOKALIZACJI
# ==========================================

locations_by_id = {
    item["id"]: item
    for item in engine.locations
}

available_universities = [
    code
    for code in UNIVERSITY_NAMES
    if any(
        loc["university"] == code
        for loc in engine.locations
    )
]


# ==========================================
# PANEL BOCZNY
# ==========================================

with st.sidebar:

    st.header("⚙️ Twoje preferencje")

    # WYBÓR UCZELNI

    selected_university = st.selectbox(
        "Wybierz uczelnię",
        available_universities,
        format_func=lambda code: UNIVERSITY_NAMES[code],
        key="university_select"
    )

    # FILTROWANIE BUDYNKÓW

    university_locations = sorted(
        (
            loc
            for loc in engine.locations
            if loc["university"] == selected_university
        ),
        key=lambda loc: (
            get_location_label(loc).casefold(),
            loc.get("address", "")
        )
    )

    location_lookup = {
        loc["id"]: loc
        for loc in university_locations
    }

    # WYBÓR BUDYNKU

    selected_location_id = st.selectbox(
        "Wybierz budynek / wydział",
        list(location_lookup),
        format_func=lambda loc_id: get_location_label(
            location_lookup[loc_id]
        ),
        key="location_select"
    )

    selected_location = location_lookup[selected_location_id]

    st.caption(
        f"📍 {selected_location.get('address', 'Adres nieznany')}"
    )

    # MAKSYMALNY CZAS DOJŚCIA

    max_walk_time = st.selectbox(
        "Maksymalny czas dojścia do uczelni",
        [15, 30, 45, None],
        index=1,
        format_func=lambda value: "Bez limitu" if value is None else f"{value} min",
    )

    st.divider()

    # WAGI KRYTERIÓW

    st.subheader("Ważność kryteriów")

    st.caption("1 — mniej ważne · 3 — bardzo ważne")

    university_weight = st.slider(
        "Bliskość uczelni",
        1,
        3,
        2
    )

    shop_weight = st.slider(
        "Dostępność sklepów",
        1,
        3,
        2
    )

    bus_weight = st.slider(
        "Dostępność komunikacji miejskiej",
        1,
        3,
        2
    )

    park_weight = st.slider(
        "Dostępność parków",
        1,
        3,
        2
    )

    generate = st.button(
        "✨ Generuj rekomendacje",
        type="primary",
        use_container_width=True
    )


# ==========================================
# PREFERENCJE UŻYTKOWNIKA
# ==========================================

weights = {
    "university": university_weight,
    "shop": shop_weight,
    "bus_stop": bus_weight,
    "park": park_weight
}

preferences = (
    selected_location_id,
    max_walk_time,
    *weights.values()
)


# ==========================================
# SESSION STATE
# ==========================================

if "result_preferences" not in st.session_state:
    st.session_state.result_preferences = None

if "recommendation_response" not in st.session_state:
    st.session_state.recommendation_response = None


# Usuwanie nieaktualnych wyników

if st.session_state.result_preferences != preferences:

    st.session_state.recommendation_response = None
    st.session_state.result_preferences = None


# ==========================================
# GENEROWANIE REKOMENDACJI
# ==========================================

if generate:
    st.session_state.recommendation_response = generate_recommendations(
        {
            "location_id": selected_location_id,
            "max_walk_time_minutes": max_walk_time,
            "weights": weights,
        },
        engine=engine,
    )
    st.session_state.result_preferences = preferences


recommendation_response = st.session_state.recommendation_response
recommendations = (
    recommendation_response["recommendations"]
    if recommendation_response and recommendation_response["status"] == "SUCCESS"
    else []
    if recommendation_response and recommendation_response["status"] == "NO_MATCHES"
    else None
)


# ==========================================
# NAGŁÓWEK STRONY
# ==========================================

st.title("🎓 StudentFinder Rzeszów")

st.markdown(
    """
    <div class="hero-note">
        Znajdź okolicę dopasowaną do Twojego życia studenckiego.
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# STATYSTYKI
# ==========================================

m1, m2, m3 = st.columns(3)

m1.metric(
    "🎓 Lokalizacje uczelni",
    len(engine.locations)
)

m2.metric(
    "🛒 Obiekty usługowe",
    len(engine.services)
)

m3.metric(
    "🏘️ Obszary mieszkalne",
    len(engine.areas)
)

st.write("")


# ==========================================
# TOP 3 REKOMENDACJE
# ==========================================

st.header("🏆 Twoje rekomendacje")

if recommendation_response and recommendation_response["status"] in {
    "VALIDATION_ERROR",
    "DATA_ERROR",
}:

    st.error(recommendation_response["message"])

elif recommendations is None:

    st.info(
        "Wybierz uczelnię i budynek, ustaw preferencje, "
        "a następnie kliknij **Generuj rekomendacje**."
    )

elif recommendation_response["status"] == "NO_MATCHES":

    st.warning(recommendation_response["message"])

else:

    colors = [
        "#16a34a",
        "#f59e0b",
        "#dc2626"
    ]

    badges = [
        "🥇 TOP 1",
        "🥈 TOP 2",
        "🥉 TOP 3"
    ]

    columns = st.columns(
        3,
        gap="medium"
    )

    for idx, result in enumerate(recommendations):

        area_name = escape(
            str(result["area_name"])
        )

        justification = escape(
            str(result.get("justification", ""))
        )

        card = f"""
        <div class="result-card" style="--accent:{colors[idx]}">

            <div class="rank">
                {badges[idx]}
            </div>

            <div class="area">
                {area_name}
            </div>

            <div class="score">
                {float(result['score']):.1f}
                <span>/ 100</span>
            </div>

            <div class="detail">
                🚶 Czas dojścia:
                <b>{float(result['walk_time_to_univ_min']):.1f} min</b>
            </div>

            <div class="detail">
                📏 Odległość:
                <b>{float(result['walk_distance_m']):.0f} m</b>
            </div>

            <div class="reason">
                {justification}
            </div>

        </div>
        """

        with columns[idx]:

            st.markdown(
                "\n".join(
                    line.strip()
                    for line in card.splitlines()
                    if line.strip()
                ),
                unsafe_allow_html=True
            )

    if 0 < len(recommendations) < 3:
        count = len(recommendations)
        area_label = (
            "okolicę spełniającą"
            if count == 1
            else "okolice spełniające"
        )

        st.info(
            f"W wybranym limicie czasu znaleziono tylko "
            f"{count} {area_label} kryteria. "
            "Aby zobaczyć więcej wyników, zwiększ limit czasu dojścia "
            "lub wybierz opcję „Bez limitu”."
        )

    st.caption(recommendation_response["disclaimer"])

    # ==========================================
    # EKSPORT RANKINGU TOP 3 DO CSV
    # ==========================================

    csv_buffer = io.StringIO(newline="")

    csv_writer = csv.writer(csv_buffer, delimiter=";")

    csv_writer.writerow([
        "Pozycja",
        "Uczelnia",
        "Budynek",
        "Okolica",
        "Osiedle",
        "Ocena (0-100)",
        "Czas dojscia (min)",
        "Odleglosc do uczelni (m)",
        "Odleglosc do sklepu (m)",
        "Odleglosc do przystanku (m)",
        "Odleglosc do parku (m)"
    ])

    for result in recommendations:
        distances = result["distances_m"]

        csv_writer.writerow([
            result["rank"],
            UNIVERSITY_NAMES[selected_university],
            get_location_label(selected_location),
            result["area_name"],
            result["district"],
            round(float(result["score"]), 1),
            f'{float(result["walk_time_to_univ_min"]):.1f}'.replace(".", ","),
            round(float(result["walk_distance_m"]), 0),
            round(float(distances["shop"]), 0),
            round(float(distances["bus_stop"]), 0),
            round(float(distances["park"]), 0)
        ])

    csv_data = "\ufeff" + csv_buffer.getvalue()

    st.download_button(
        label="📥 Pobierz ranking TOP 3 (CSV)",
        data=csv_data.encode("utf-8"),
        file_name="studentfinder_top3.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==========================================
# MAPA
# ==========================================

st.write("")

st.header("📍 Mapa rekomendowanych okolic")

st.markdown(
    """
    <div class="map-legend">
        🟢 TOP 1 &nbsp;·&nbsp;
        🟠 TOP 2 &nbsp;·&nbsp;
        🔴 TOP 3 &nbsp;·&nbsp;
        🎓 Wybrana uczelnia
    </div>
    """,
    unsafe_allow_html=True
)


mapa = folium.Map(
    location=[50.0413, 21.9990],
    zoom_start=12,
    tiles="OpenStreetMap",
    control_scale=True
)


# ==========================================
# MARKERY NA MAPIE
# ==========================================

if recommendations:

    points = [
        (
            float(selected_location["latitude"]),
            float(selected_location["longitude"])
        )
    ]

    # MARKER UCZELNI

    folium.Marker(
        location=points[0],
        tooltip="Wybrana uczelnia",
        popup=folium.Popup(
            (
                f"<b>{escape(get_location_label(selected_location))}</b>"
                f"<br>{escape(str(selected_location.get('address', '')))}"
            ),
            max_width=330
        ),
        icon=folium.Icon(
            color="blue",
            icon="graduation-cap",
            prefix="fa"
        )
    ).add_to(mapa)

    # MARKERY REKOMENDOWANYCH OKOLIC

    for idx, result in enumerate(recommendations):

        coords = (
            float(result["center_lat"]),
            float(result["center_lon"])
        )

        points.append(coords)

        color = colors[idx]
        number = idx + 1

        folium.Circle(
            location=coords,
            radius=float(result["radius_m"]),
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.12,
            tooltip=f"Promień obszaru: {int(result['radius_m'])} m",
        ).add_to(mapa)

        marker_html = (
            f'<div style="'
            f'width:36px;'
            f'height:36px;'
            f'border-radius:50%;'
            f'background:{color};'
            f'border:3px solid white;'
            f'color:white;'
            f'display:flex;'
            f'align-items:center;'
            f'justify-content:center;'
            f'font-weight:800;'
            f'font-size:16px;'
            f'box-shadow:0 3px 9px #0005;'
            f'">'
            f'{number}'
            f'</div>'
        )

        popup_html = (
            f"<b>#{number} {escape(str(result['area_name']))}</b><br>"
            f"Ocena: {float(result['score']):.1f}/100<br>"
            f"Czas dojścia: "
            f"{float(result['walk_time_to_univ_min']):.1f} min<br>"
            f"Odległość: "
            f"{float(result['walk_distance_m']):.0f} m"
        )

        folium.Marker(
            location=coords,
            tooltip=(
                f"TOP {number}: {result['area_name']}"
            ),
            popup=folium.Popup(
                popup_html,
                max_width=320
            ),
            icon=folium.DivIcon(
                html=marker_html,
                icon_size=(36, 36),
                icon_anchor=(18, 18)
            )
        ).add_to(mapa)

    # DOPASOWANIE WIDOKU MAPY

    if len(points) > 1:

        mapa.fit_bounds(
            points,
            padding=(45, 45),
            max_zoom=15
        )


# ==========================================
# WYŚWIETLANIE MAPY
# ==========================================

st_folium(
    mapa,
    height=520,
    use_container_width=True,
    returned_objects=[],
    key="studentfinder_map"
)


# ==========================================
# INFORMACJE O SYSTEMIE
# ==========================================

with st.expander("ℹ️ Jak działa StudentFinder?"):

    st.write(
        "System porównuje okolice mieszkalne według odległości "
        "od wybranej lokalizacji uczelni oraz dostępności "
        "sklepów, przystanków i parków. "
        "Wagi 1–3 określają znaczenie kryteriów dla użytkownika. "
        "Silnik oblicza ocenę i zwraca maksymalnie trzy "
        "najwyżej ocenione okolice spełniające limit czasu dojścia."
    )

    st.info(
        "Odległości są liczone w linii prostej, "
        "a czas dojścia jest szacunkowy. "
        "Wyniki nie uwzględniają rzeczywistej sieci ulic "
        "ani warunków ruchu pieszego."
    )


# ==========================================
# STOPKA
# ==========================================

st.divider()

st.caption(
    "StudentFinder Rzeszów · Projekt informatyczny · "
    "Uniwersytet Rzeszowski · 2026"
)

st.caption(
    "Dane mapowe: © OpenStreetMap contributors (ODbL)."
)
