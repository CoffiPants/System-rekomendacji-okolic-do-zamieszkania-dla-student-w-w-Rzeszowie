import streamlit as st

st.set_page_config(
    page_title="StudentFinder Rzeszów",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 StudentFinder Rzeszów")

st.subheader(
    "System rekomendacji okolic mieszkalnych dla studentów"
)

st.markdown(
    "Znajdź najlepszą okolicę do zamieszkania "
    "na podstawie swoich indywidualnych preferencji."
)

with st.sidebar:
    st.header("⚙️ Twoje preferencje")

    st.info("Wybór uczelni zostanie podłączony do danych projektu.")

    max_walk_time = st.slider(
        "Maksymalny czas dojścia do uczelni (min)",
        min_value=5,
        max_value=60,
        value=30,
        step=5
    )

    st.divider()
    st.subheader("Ważność poszczególnych kryteriów")

    university_weight = st.slider(
        "Bliskość uczelni", 0, 5, 3
    )

    shop_weight = st.slider(
        "Dostępność sklepów", 0, 5, 3
    )

    bus_weight = st.slider(
        "Dostępność komunikacji miejskiej", 0, 5, 3
    )

    park_weight = st.slider(
        "Dostępność parków", 0, 5, 3
    )

    generate = st.button(
        "Generuj rekomendacje",
        type="primary",
        use_container_width=True
    )

col1, col2, col3 = st.columns(3)

col1.metric("Lokalizacje uczelni", 28)
col2.metric("Obiekty usługowe", 500)
col3.metric("Obszary mieszkalne", 25)

st.divider()

left, right = st.columns([1, 2])

with left:
    st.header("🏆 TOP 3 okolice")

    if generate:
        st.warning(
            "Silnik rekomendacji nie został jeszcze podłączony."
        )
    else:
        st.info(
            "Określ swoje preferencje i wygeneruj rekomendacje."
        )

with right:
    st.header("📍 Mapa Rzeszowa")

    st.info(
        "W tym miejscu pojawi się interaktywna mapa "
        "z lokalizacjami rekomendowanych okolic."
    )

st.divider()

st.caption(
    "Projekt informatyczny | Uniwersytet Rzeszowski | 2026"
)